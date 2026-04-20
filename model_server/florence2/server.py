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


def _detect_with_grounding(
    image: Image.Image,
    labels: list[LabelItem],
    max_per_label: int,
) -> list[ResultItem]:
    """Use <CAPTION_TO_PHRASE_GROUNDING> for open-vocabulary detection."""
    caption = ". ".join(lbl.name for lbl in labels)
    raw = _run_florence(image, "<CAPTION_TO_PHRASE_GROUNDING>", caption)
    data = raw.get("<CAPTION_TO_PHRASE_GROUNDING>", {})
    bboxes = data.get("bboxes", [])
    detected_labels = data.get("labels", [])

    label_name_set = {lbl.name.lower() for lbl in labels}
    label_tool_map = {lbl.name.lower(): lbl.tool for lbl in labels}
    counts: dict[str, int] = {}
    results: list[ResultItem] = []

    for bbox, det_label in zip(bboxes, detected_labels):
        det_clean = det_label.strip().lower()
        if det_clean not in label_name_set:
            continue
        counts[det_clean] = counts.get(det_clean, 0) + 1
        if counts[det_clean] > max_per_label:
            continue
        tool = label_tool_map.get(det_clean, "rectTool")
        results.append(ResultItem(
            toolName=tool,
            label=det_clean,
            result=_bbox_to_rect(bbox),
            score=None,
        ))
    return results


def _segment_for_labels(
    image: Image.Image,
    labels: list[LabelItem],
    max_per_label: int,
) -> list[ResultItem]:
    """Use <REFERRING_EXPRESSION_SEGMENTATION> per label for polygon output."""
    results: list[ResultItem] = []
    for lbl in labels:
        if lbl.tool != "polygonTool":
            continue
        raw = _run_florence(image, "<REFERRING_EXPRESSION_SEGMENTATION>", lbl.name)
        seg_data = raw.get("<REFERRING_EXPRESSION_SEGMENTATION>", {})
        polygons_raw = seg_data.get("polygons", [])

        for i, polygon in enumerate(polygons_raw[:max_per_label]):
            if isinstance(polygon, list) and len(polygon) > 0:
                if isinstance(polygon[0], list):
                    points = [{"x": float(polygon[0][j]), "y": float(polygon[0][j + 1])}
                              for j in range(0, len(polygon[0]), 2)]
                else:
                    points = [{"x": float(polygon[j]), "y": float(polygon[j + 1])}
                              for j in range(0, len(polygon), 2)]
                if len(points) >= 3:
                    results.append(ResultItem(
                        toolName="polygonTool",
                        label=lbl.name,
                        result={"type": "line", "points": points},
                    ))
    return results


# ── main endpoint ─────────────────────────────────────────────────────
@app.post("/", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    start = time.perf_counter()
    try:
        image = await _download_image(req.image_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {exc}")

    allowed = set(req.constraints.allowed_tools) if req.constraints.allowed_tools else None
    max_per = req.constraints.max_results_per_label
    results: list[ResultItem] = []

    need_detect = allowed is None or allowed & {"rectTool", "pointTool", "lineTool"}
    need_segment = allowed is None or "polygonTool" in (allowed or set())

    if need_detect:
        detect_labels = [l for l in req.labels if l.tool != "polygonTool"] if need_segment else req.labels
        if detect_labels:
            results.extend(_detect_with_grounding(image, detect_labels, max_per))

    if need_segment:
        seg_labels = [l for l in req.labels if l.tool == "polygonTool"]
        if seg_labels:
            results.extend(_segment_for_labels(image, seg_labels, max_per))

    latency = int((time.perf_counter() - start) * 1000)
    return PredictResponse(model=MODEL_NAME, latency_ms=latency, results=results)


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME, "device": device}


# ── entrypoint ────────────────────────────────────────────────────────
def main():
    global model, processor, device

    parser = argparse.ArgumentParser(description="LabelU Florence-2 Model Server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--model", type=str, default=MODEL_NAME)
    args = parser.parse_args()

    device = args.device
    global MODEL_NAME
    MODEL_NAME = args.model

    logger.info("Loading %s on %s ...", MODEL_NAME, device)
    processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, trust_remote_code=True, torch_dtype=torch.float16 if "cuda" in device else torch.float32,
    ).to(device).eval()
    logger.info("Model loaded.")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
