"""
LabelU Model Server — SAM 3 (Segment Anything with Concepts)

Uses Meta SAM 3 for unified open-vocabulary detection + segmentation.
Single model replaces GroundingDINO + SAM pipeline.

Implements the LabelU auto-label model API protocol:
  POST /  ->  { request_id, image_url, labels, constraints, prompt }
  Returns ->  { model, results: [{ toolName, label, result, score }], ... }

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

import cv2
import httpx
import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sam3-server")

app = FastAPI(title="LabelU SAM 3 Model Server")

# -- globals (set in main) ---------------------------------------------------
sam3_model = None
sam3_processor = None
device = "cpu"

MODEL_NAME = "sam3"


# -- request / response schemas ----------------------------------------------
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


# -- helpers ------------------------------------------------------------------
async def _download_image(url: str) -> Image.Image:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _bbox_to_rect(box: list[float] | torch.Tensor) -> dict[str, float]:
    """Convert [x1, y1, x2, y2] to {x, y, width, height}."""
    if isinstance(box, torch.Tensor):
        box = box.cpu().tolist()
    x1, y1, x2, y2 = box
    return {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1}


def _mask_to_polygon(mask: np.ndarray) -> list[dict[str, float]]:
    """Extract the largest contour as simplified polygon points."""
    if isinstance(mask, torch.Tensor):
        mask = mask.cpu().numpy()
    mask_uint8 = (mask > 0).astype(np.uint8)
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []
    largest = max(contours, key=cv2.contourArea)
    epsilon = 0.005 * cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, epsilon, True)
    return [{"x": float(pt[0][0]), "y": float(pt[0][1])} for pt in approx]


def _detect_and_segment(
    image: Image.Image,
    label: LabelItem,
    max_per_label: int,
) -> list[ResultItem]:
    """Run SAM 3 text-prompted detection + segmentation for a single label."""
    inference_state = sam3_processor.set_image(image)
    output = sam3_processor.set_text_prompt(
        state=inference_state,
        prompt=label.name,
    )

    masks = output.get("masks")       # [N, H, W]
    boxes = output.get("boxes")       # [N, 4] xyxy
    scores = output.get("scores")     # [N]

    if boxes is None or len(boxes) == 0:
        return []

    results: list[ResultItem] = []
    n = min(len(boxes), max_per_label)

    for i in range(n):
        score = round(float(scores[i]), 4) if scores is not None and i < len(scores) else None

        if label.tool == "polygonTool" and masks is not None and i < len(masks):
            points = _mask_to_polygon(masks[i])
            if len(points) >= 3:
                results.append(ResultItem(
                    toolName="polygonTool",
                    label=label.name,
                    result={"type": "line", "points": points},
                    score=score,
                ))
                continue

        # Default: bounding box
        results.append(ResultItem(
            toolName=label.tool,
            label=label.name,
            result=_bbox_to_rect(boxes[i]),
            score=score,
        ))

    return results


# -- main endpoint ------------------------------------------------------------
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

    for lbl in req.labels:
        if allowed and lbl.tool not in allowed:
            continue
        label_results = _detect_and_segment(image, lbl, max_per)
        results.extend(label_results)

    latency = int((time.perf_counter() - start) * 1000)
    return PredictResponse(model=MODEL_NAME, latency_ms=latency, results=results)


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME, "device": device}


# -- entrypoint ---------------------------------------------------------------
def main():
    global sam3_model, sam3_processor, device, MODEL_NAME

    parser = argparse.ArgumentParser(description="LabelU SAM 3 Model Server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    device = args.device

    from sam3.model_builder import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor

    logger.info("Loading SAM 3 on %s ...", device)
    sam3_model = build_sam3_image_model()
    sam3_processor = Sam3Processor(sam3_model)
    MODEL_NAME = "sam3"
    logger.info("SAM 3 loaded.")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
