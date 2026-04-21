"""
LabelU Model Server — Florence-2

Lightweight reference implementation using Microsoft Florence-2 for
open-vocabulary image detection and segmentation.

Implements the LabelU auto-label model API protocol:
  POST /  →  { request_id, image_url, labels, constraints, prompt }
  Returns  →  { model, results: [{ toolName, label, result, score }], ... }

Quick start:
  pip install -r requirements.txt
  python server.py                        # default: 0.0.0.0:5000
  python server.py --port 5001 --device cuda
"""

from __future__ import annotations

import argparse
import io
import time
import logging
from typing import Any

import httpx
import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("florence2-server")

app = FastAPI(title="LabelU Florence-2 Model Server")

# ── globals (set in main) ─────────────────────────────────────────────
model = None
processor = None
device = "cpu"

MODEL_NAME = "microsoft/Florence-2-base"


# ── request / response schemas ────────────────────────────────────────
class LabelItem(BaseModel):
    name: str
    display_name: str | None = None
    color: str | None = None
    tool: str


class Constraints(BaseModel):
    allowed_tools: list[str] = []
    max_results_per_label: int = 100
    filter_by_labels: bool = False


class PredictRequest(BaseModel):
    request_id: str = ""
    image_url: str
    task: dict[str, Any] = {}
    labels: list[LabelItem] = []
    constraints: Constraints = Field(default_factory=Constraints)
    prompt: str | None = None


class ResultItem(BaseModel):
    toolName: str
    label: str
    result: dict[str, Any]
    score: float | None = None


class PredictResponse(BaseModel):
    model: str = MODEL_NAME
    latency_ms: int = 0
    results: list[ResultItem] = []
    warning_message: str | None = None


# ── helpers ───────────────────────────────────────────────────────────
async def _download_image(url: str) -> Image.Image:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _run_florence(image: Image.Image, task_prompt: str, text_input: str = "") -> dict:
    full_prompt = task_prompt if not text_input else task_prompt + text_input
    inputs = processor(text=full_prompt, images=image, return_tensors="pt").to(device)
    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=1024,
            num_beams=3,
        )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    return processor.post_process_generation(
        generated_text, task=task_prompt, image_size=image.size
    )


def _bbox_to_rect(bbox: list[float]) -> dict[str, float]:
    """Convert [x1, y1, x2, y2] to {x, y, width, height}."""
    x1, y1, x2, y2 = bbox
    return {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1}


def _mask_to_polygon_points(mask: np.ndarray) -> list[dict[str, float]]:
    """Extract the largest contour from a binary mask as polygon points."""
    import cv2

    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return []
    largest = max(contours, key=cv2.contourArea)
    epsilon = 0.005 * cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, epsilon, True)
    return [{"x": float(pt[0][0]), "y": float(pt[0][1])} for pt in approx]


def _detect_with_od(
    image: Image.Image,
    default_tool: str,
) -> list[ResultItem]:
    """Use <OD> for general object detection (Florence2 built-in categories)."""
    raw = _run_florence(image, "<OD>")
    data = raw.get("<OD>", {})
    bboxes = data.get("bboxes", [])
    detected_labels = data.get("labels", [])

    results: list[ResultItem] = []
    for bbox, det_label in zip(bboxes, detected_labels):
        det_clean = det_label.strip().lower()
        results.append(ResultItem(
            toolName=default_tool,
            label=det_clean,
            result=_bbox_to_rect(bbox),
            score=None,
        ))
    return results


def _detect_with_grounding(
    image: Image.Image,
    labels: list[LabelItem],
    max_per_label: int,
    filter_by_labels: bool = False,
) -> list[ResultItem]:
    """Use <OD> as baseline, then <CAPTION_TO_PHRASE_GROUNDING> for custom labels."""
    label_tool_map = {lbl.name.lower(): lbl.tool for lbl in labels}
    default_tool = labels[0].tool if labels else "rectTool"

    # Step 1: Run <OD> to get all standard detections
    od_results = _detect_with_od(image, default_tool)
    od_labels_found = {r.label for r in od_results}
    logger.info("<OD> found %d objects: %s", len(od_results), od_labels_found)

    # Step 2: Find configured labels not covered by <OD>, run grounding for those
    uncovered = [lbl for lbl in labels if lbl.name.lower() not in od_labels_found]
    grounding_results: list[ResultItem] = []
    if uncovered:
        caption = ". ".join(lbl.name for lbl in uncovered)
        raw = _run_florence(image, "<CAPTION_TO_PHRASE_GROUNDING>", caption)
        logger.info("<CAPTION_TO_PHRASE_GROUNDING> raw: %s", raw)
        data = raw.get("<CAPTION_TO_PHRASE_GROUNDING>", {})
        for bbox, det_label in zip(data.get("bboxes", []), data.get("labels", [])):
            det_clean = det_label.strip().lower()
            tool = label_tool_map.get(det_clean, default_tool)
            grounding_results.append(ResultItem(
                toolName=tool,
                label=det_clean,
                result=_bbox_to_rect(bbox),
                score=None,
            ))

    # Merge: OD results + grounding results for uncovered labels
    all_results = od_results + grounding_results

    if filter_by_labels:
        label_name_set = {lbl.name.lower() for lbl in labels}
        all_results = [r for r in all_results if r.label in label_name_set]

    # Apply tool mapping from configured labels
    for r in all_results:
        if r.label in label_tool_map:
            r.toolName = label_tool_map[r.label]

    return all_results


def _segment_for_labels(
    image: Image.Image,
    labels: list[LabelItem],
    max_per_label: int,
    filter_by_labels: bool = False,
) -> list[ResultItem]:
    """Detect all instances first, then segment each via <REGION_TO_SEGMENTATION>.

    <REFERRING_EXPRESSION_SEGMENTATION> only returns ONE object per query.
    To get all instances we: 1) detect bboxes, 2) segment each bbox region.
    """
    results: list[ResultItem] = []
    seg_labels = [lbl for lbl in labels if lbl.tool == "polygonTool"]
    if not seg_labels:
        return results

    # Step 1: detect all objects to get bounding boxes
    det_results = _detect_with_grounding(image, seg_labels, max_per_label, filter_by_labels)
    logger.info("Segment pipeline: detected %d bboxes for polygon labels", len(det_results))

    # Step 2: for each detected bbox, run region-based segmentation
    for det in det_results:
        bbox = det.result  # {x, y, width, height}
        x1 = bbox["x"]
        y1 = bbox["y"]
        x2 = x1 + bbox["width"]
        y2 = y1 + bbox["height"]

        # Florence-2 <REGION_TO_SEGMENTATION> expects "<loc_x1><loc_y1><loc_x2><loc_y2>"
        # where coordinates are normalized to 0-999 range
        w, h = image.size
        loc_x1 = int(x1 / w * 999)
        loc_y1 = int(y1 / h * 999)
        loc_x2 = int(x2 / w * 999)
        loc_y2 = int(y2 / h * 999)
        region_text = f"<loc_{loc_x1}><loc_{loc_y1}><loc_{loc_x2}><loc_{loc_y2}>"

        try:
            raw = _run_florence(image, "<REGION_TO_SEGMENTATION>", region_text)
            seg_data = raw.get("<REGION_TO_SEGMENTATION>", {})
            polygons_raw = seg_data.get("polygons", [])

            for polygon in polygons_raw[:1]:  # one polygon per bbox
                if isinstance(polygon, list) and len(polygon) > 0:
                    coords = polygon[0] if isinstance(polygon[0], list) else polygon
                    points = [
                        {"x": float(coords[j]), "y": float(coords[j + 1])}
                        for j in range(0, len(coords), 2)
                    ]
                    if len(points) >= 3:
                        results.append(
                            ResultItem(
                                toolName="polygonTool",
                                label=det.label,
                                result={"type": "line", "points": points},
                                score=det.score,
                            )
                        )
        except Exception as exc:
            logger.warning("Region segmentation failed for bbox %s: %s", bbox, exc)
            # Fallback: skip this object's polygon
            continue

    return results


# ── main endpoint ─────────────────────────────────────────────────────
@app.post("/", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    start = time.perf_counter()
    try:
        image = await _download_image(req.image_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {exc}")

    allowed = (
        set(req.constraints.allowed_tools) if req.constraints.allowed_tools else None
    )
    max_per = req.constraints.max_results_per_label
    results: list[ResultItem] = []

    need_detect = allowed is None or allowed & {"rectTool", "pointTool", "lineTool"}
    need_segment = allowed is None or "polygonTool" in (allowed or set())

    if need_detect:
        detect_labels = (
            [l for l in req.labels if l.tool != "polygonTool"]
            if need_segment
            else req.labels
        )

        logger.info("detect_labels: %s", detect_labels)

        if detect_labels:
            results.extend(
                _detect_with_grounding(
                    image, detect_labels, max_per, req.constraints.filter_by_labels
                )
            )

    if need_segment:
        seg_labels = [l for l in req.labels if l.tool == "polygonTool"]
        if seg_labels:
            results.extend(_segment_for_labels(image, seg_labels, max_per, req.constraints.filter_by_labels))

    latency = int((time.perf_counter() - start) * 1000)
    return PredictResponse(model=MODEL_NAME, latency_ms=latency, results=results)


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME, "device": device}


# ── entrypoint ────────────────────────────────────────────────────────
def main():
    global model, processor, device, MODEL_NAME

    parser = argparse.ArgumentParser(description="LabelU Florence-2 Model Server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument(
        "--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu"
    )
    parser.add_argument("--model", type=str, default=MODEL_NAME)
    args = parser.parse_args()

    device = args.device
    MODEL_NAME = args.model

    logger.info("Loading %s on %s ...", MODEL_NAME, device)
    processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = (
        AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            torch_dtype=torch.float16 if "cuda" in device else torch.float32,
        )
        .to(device)
        .eval()
    )
    logger.info("Model loaded.")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
