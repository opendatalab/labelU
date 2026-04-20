import json
import time
import uuid
from typing import Any

import httpx
from fastapi import status
from loguru import logger
from sqlalchemy.orm import Session

from labelu.internal.adapter.persistence import crud_pre_annotation, crud_sample, crud_task
from labelu.internal.application.command.auto_label import AutoLabelCommand
from labelu.internal.application.response.auto_label import AutoLabelResponse
from labelu.internal.common.db import begin_transaction
from labelu.internal.common.error_code import ErrorCode, LabelUException
from labelu.internal.common.storage import get_model_read_url
from labelu.internal.common.config import settings
from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.domain.models.task import MediaType
from labelu.internal.domain.models.user import User


SUPPORTED_IMAGE_TOOLS = {"rectTool", "polygonTool", "pointTool", "lineTool"}


def _parse_task_config(raw_config: str | dict | None) -> dict[str, Any]:
    if not raw_config:
        return {}
    if isinstance(raw_config, dict):
        return raw_config
    try:
        return json.loads(raw_config)
    except json.JSONDecodeError:
        logger.warning("failed to parse task config: {}", raw_config)
        return {}


def _extract_tool_configs(task_config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    config_by_tool: dict[str, Any] = {}
    for tool in task_config.get("tools", []) or []:
        tool_name = tool.get("tool")
        tool_config = tool.get("config", {}) or {}
        if tool_name not in SUPPORTED_IMAGE_TOOLS:
            continue
        attributes = tool_config.get("attributes", []) or []
        if not attributes:
            continue
        config_by_tool[tool_name] = tool_config
        for attr in attributes:
            labels.append(
                {
                    "name": attr.get("value") or attr.get("key"),
                    "display_name": attr.get("key"),
                    "color": attr.get("color"),
                    "tool": tool_name,
                }
            )
    return labels, config_by_tool


def _get_image_url(attachment) -> str:
    """Get a readable URL for the image, handling both local/global-S3 and external data source attachments."""
    if getattr(attachment, "data_source_id", None) and getattr(attachment, "data_source", None):
        from labelu.internal.application.service.datasource import get_presigned_url
        return get_presigned_url(attachment.data_source, attachment.path)
    return get_model_read_url(attachment.path)


def _build_model_payload(sample, task, task_config: dict[str, Any], cmd: AutoLabelCommand) -> dict[str, Any]:
    labels, config_by_tool = _extract_tool_configs(task_config)
    if not labels:
        raise LabelUException(
            code=ErrorCode.CODE_56002_AUTO_LABEL_NO_LABELS_CONFIGURED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return {
        "request_id": str(uuid.uuid4()),
        "image_url": _get_image_url(sample.file),
        "task": {
            "id": task.id,
            "name": task.name,
        },
        "labels": labels,
        "constraints": {
            "allowed_tools": list(config_by_tool.keys()),
            "max_results_per_label": 100,
        },
        "prompt": cmd.prompt,
    }


def _annotation_meta(data: str | dict | None) -> dict[str, Any]:
    if not data:
        return {}
    parsed = data if isinstance(data, dict) else json.loads(data)
    return parsed.get("meta", {}) or {}


def _is_ai_generated(pre_annotation: TaskPreAnnotation) -> bool:
    try:
        return _annotation_meta(pre_annotation.data).get("source_type") == "ai_generated"
    except Exception:
        return False


def _normalize_single_result(tool_name: str, item: dict[str, Any], order: int) -> dict[str, Any]:
    result_payload = item.get("result", item)
    attributes = item.get("attributes") or {}
    if item.get("score") is not None:
        attributes = {**attributes, "score": str(item["score"])}

    base = {
        "id": item.get("id") or str(uuid.uuid4()),
        "order": item.get("order", order),
        "label": item.get("label"),
        "visible": item.get("visible", True),
    }
    if attributes:
        base["attributes"] = attributes

    if tool_name == "rectTool":
        return {
            **base,
            "x": result_payload["x"],
            "y": result_payload["y"],
            "width": result_payload["width"],
            "height": result_payload["height"],
        }

    if tool_name == "polygonTool":
        return {
            **base,
            "type": result_payload.get("type", "line"),
            "points": result_payload.get("points") or result_payload.get("pointList") or [],
        }

    if tool_name == "lineTool":
        return {
            **base,
            "type": result_payload.get("type", "line"),
            "points": result_payload.get("points") or result_payload.get("pointList") or [],
        }

    if tool_name == "pointTool":
        return {
            **base,
            "x": result_payload["x"],
            "y": result_payload["y"],
        }

    raise LabelUException(
        code=ErrorCode.CODE_56005_AUTO_LABEL_INVALID_RESPONSE,
        status_code=status.HTTP_502_BAD_GATEWAY,
    )


def _normalize_results(model_data: dict[str, Any], sample_name: str, task_config: dict[str, Any]) -> dict[str, Any]:
    results = model_data.get("results", [])
    flattened: list[tuple[str, dict[str, Any]]] = []
    if isinstance(results, dict):
        for tool_name, items in results.items():
            for item in items or []:
                flattened.append((tool_name, item))
    else:
        for item in results:
            flattened.append((item.get("toolName"), item))

    grouped_annotations: dict[str, dict[str, Any]] = {}
    for index, (tool_name, item) in enumerate(flattened):
        if tool_name not in SUPPORTED_IMAGE_TOOLS:
            continue
        grouped_annotations.setdefault(tool_name, {"toolName": tool_name, "result": []})
        grouped_annotations[tool_name]["result"].append(_normalize_single_result(tool_name, item, index))

    _, config_by_tool = _extract_tool_configs(task_config)
    # Pre-annotation config format: { toolName: [{key, value, color}, ...] }
    pre_annotation_config = {
        tool_name: tool_cfg.get("attributes", [])
        for tool_name, tool_cfg in config_by_tool.items()
    }
    return {
        "sample_name": sample_name,
        "annotations": grouped_annotations,
        "config": pre_annotation_config,
        "meta": {
            "source_type": "ai_generated",
            "provider": settings.AI_PROVIDER,
            "model": model_data.get("model") or settings.AI_MODEL_NAME,
            "latency_ms": model_data.get("latency_ms"),
            "warning_message": model_data.get("warning_message"),
        },
    }


async def create(
    db: Session,
    task_id: int,
    sample_id: int,
    cmd: AutoLabelCommand,
    current_user: User,
) -> AutoLabelResponse:
    if not settings.AI_AUTO_LABEL_ENABLED:
        raise LabelUException(
            code=ErrorCode.CODE_56000_AUTO_LABEL_DISABLED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not settings.AI_MODEL_ENDPOINT:
        logger.error("AI_MODEL_ENDPOINT is not configured")
        raise LabelUException(
            code=ErrorCode.CODE_56004_AUTO_LABEL_NOT_CONFIGURED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        raise LabelUException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    collaborator_ids = {c.id for c in task.collaborators}
    if task.created_by != current_user.id and current_user.id not in collaborator_ids:
        raise LabelUException(
            code=ErrorCode.CODE_30001_NO_PERMISSION,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if task.media_type != MediaType.IMAGE.value:
        raise LabelUException(
            code=ErrorCode.CODE_56001_AUTO_LABEL_UNSUPPORTED_MEDIA,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    sample = crud_sample.get(db=db, sample_id=sample_id)
    if not sample or sample.task_id != task_id or not sample.file:
        raise LabelUException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    existing_pre_annotations, _ = crud_pre_annotation.list_by(
        db=db,
        task_id=task_id,
        sample_name=sample.file.filename,
        page=0,
        size=100,
    )
    existing_ai_annotations = [item for item in existing_pre_annotations if _is_ai_generated(item)]
    if existing_ai_annotations and not cmd.overwrite:
        latest_pre_annotation = existing_ai_annotations[-1]
        meta = _annotation_meta(latest_pre_annotation.data)
        return AutoLabelResponse(
            status="COMPLETED",
            task_id=task_id,
            sample_id=sample_id,
            media_type=task.media_type,
            provider=meta.get("provider") or settings.AI_PROVIDER,
            model=meta.get("model") or settings.AI_MODEL_NAME,
            latency_ms=meta.get("latency_ms"),
            pre_annotation_id=latest_pre_annotation.id,
            warning_message=meta.get("warning_message"),
        )

    model_payload = _build_model_payload(sample, task, _parse_task_config(task.config), cmd)
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.AI_MODEL_TIMEOUT_SECONDS) as client:
            response = await client.post(settings.AI_MODEL_ENDPOINT, json=model_payload)
            if response.status_code >= 400:
                logger.error(
                    "model service returned {}: {}",
                    response.status_code,
                    response.text,
                )
            response.raise_for_status()
            model_data = response.json()
    except Exception as exc:
        logger.opt(exception=exc).error("auto label model request failed")
        raise LabelUException(
            code=ErrorCode.CODE_56003_AUTO_LABEL_MODEL_ERROR,
            message=response.text,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )

    normalized_payload = _normalize_results(
        model_data=model_data,
        sample_name=sample.file.filename,
        task_config=_parse_task_config(task.config),
    )
    normalized_payload["meta"]["latency_ms"] = int((time.perf_counter() - start) * 1000)

    with begin_transaction(db):
        if existing_ai_annotations:
            crud_pre_annotation.delete(
                db=db,
                pre_annotation_ids=[item.id for item in existing_ai_annotations],
            )

        pre_annotations = crud_pre_annotation.batch(
            db=db,
            pre_annotations=[
                TaskPreAnnotation(
                    task_id=task_id,
                    file_id=None,
                    sample_name=sample.file.filename,
                    data=json.dumps(normalized_payload, ensure_ascii=False),
                    created_by=current_user.id,
                    updated_by=current_user.id,
                )
            ],
        )

    created_pre_annotation = pre_annotations[0]
    meta = normalized_payload.get("meta", {})
    return AutoLabelResponse(
        status="COMPLETED",
        task_id=task_id,
        sample_id=sample_id,
        media_type=task.media_type,
        provider=meta.get("provider") or settings.AI_PROVIDER,
        model=meta.get("model") or settings.AI_MODEL_NAME,
        latency_ms=meta.get("latency_ms"),
        pre_annotation_id=created_pre_annotation.id,
        warning_message=meta.get("warning_message"),
    )
