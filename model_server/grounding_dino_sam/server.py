"""
LabelU Model Server — GroundingDINO + EfficientSAM

High-quality reference implementation for open-vocabulary detection
(GroundingDINO) paired with segmentation (EfficientSAM).

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

import cv2
import httpx
import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dino-sam-server")

app = FastAPI(title="LabelU GroundingDINO + EfficientSAM Model Server")

# ── globals ───────────────────────────────────────────────────────────
dino_model = None
dino_processor = None
sam_model = None
sam_processor = None
device = "cpu"

DINO_MODEL_ID = "IDEA-Research/grounding-dino-tiny"
SAM_MODEL_ID = "ybelkada/efficient-sam-vitt"
MODEL_LABEL = "grounding-dino-tiny+efficient-sam"

BOX_THRESHOLD = 0.25
TEXT_THRESHOLD = 0.25


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
    model: str = MODEL_LABEL
    latency_ms: int = 0
    results: list[ResultItem] = []
    warning_message: str | None = None


# ── helpers ───────────────────────────────────────────────────────────
async def _download_image(url: str) -> Image.Image:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _detect_objects(
    image: Image.Image,
    text_prompt: str,
    box_threshold: float = BOX_THRESHOLD,
    text_threshold: float = TEXT_THRESHOLD,
) -> tuple[list[list[float]], list[str], list[float]]:
    """Run GroundingDINO detection. Returns (boxes_xyxy_abs, labels, scores)."""
    inputs = dino_processor(images=image, text=text_prompt, return_tensors="pt").to(device)
    with torch.inference_mode():
        outputs = dino_model(**inputs)

    post = dino_processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        box_threshold=box_threshold,
        text_threshold=text_threshold,
        target_sizes=[image.size[::-1]],
    )[0]

    boxes = post["boxes"].cpu().numpy().tolist()
    labels_out = post["labels"]
    scores = post["scores"].cpu().numpy().tolist()
    return boxes, labels_out, scores


def _segment_box(image: Image.Image, box_xyxy: list[float]) -> np.ndarray | None:
    """Run EfficientSAM on a single bounding box prompt. Returns binary mask."""
    if sam_model is None:
        return None

    w, h = image.size
    input_points = torch.tensor([[[
        [box_xyxy[0] / w, box_xyxy[1] / h],
        [box_xyxy[2] / w, box_xyxy[3] / h],
    ]]]).to(device)
    input_labels = torch.tensor([[[2, 3]]]).to(device)  # box prompt: top-left=2, bottom-right=3

    inputs = sam_processor(image, input_points=input_points, input_labels=input_labels, return_tensors="pt").to(device)
    with torch.inference_mode():
        outputs = sam_model(**inputs)

    mask = sam_processor.image_processor.post_process_masks(
        outputs.pred_masks.cpu(),
        inputs["original_sizes"].cpu(),
        inputs["reshaped_input_sizes"].cpu(),
    )[0]

    mask_np = mask[0, 0].numpy().astype(np.uint8)
    return mask_np


def _mask_to_polygon(mask: np.ndarray) -> list[dict[str, float]]:
    """Extract the largest contour as simplified polygon points."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []
    largest = max(contours, key=cv2.contourArea)
    epsilon = 0.005 * cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, epsilon, True)
    return [{"x": float(pt[0][0]), "y": float(pt[0][1])} for pt in approx]


def _bbox_to_rect(box_xyxy: list[float]) -> dict[str, float]:
    x1, y1, x2, y2 = box_xyxy
    return {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1}


# ── main endpoint ─────────────────────────────────────────────────────
@app.post("/", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    start = time.perf_counter()
    try:
        image = await _download_image(req.image_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {exc}")

    label_names = [lbl.name for lbl in req.labels]
    label_tool_map = {lbl.name.lower().strip(): lbl.tool for lbl in req.labels}
    text_prompt = " . ".join(label_names) + " ."
    max_per = req.constraints.max_results_per_label
    allowed = set(req.constraints.allowed_tools) if req.constraints.allowed_tools else None

    boxes, det_labels, scores = _detect_objects(image, text_prompt)

    results: list[ResultItem] = []
    counts: dict[str, int] = {}

    for box, det_label, score in zip(boxes, det_labels, scores):
        clean = det_label.strip().lower()
        counts[clean] = counts.get(clean, 0) + 1
        if counts[clean] > max_per:
            continue

        tool = label_tool_map.get(clean, "rectTool")
        if allowed and tool not in allowed:
            continue

        if tool == "polygonTool" and sam_model is not None:
            mask = _segment_box(image, box)
            if mask is not None:
                points = _mask_to_polygon(mask)
                if len(points) >= 3:
                    results.append(ResultItem(
                        toolName="polygonTool",
                        label=clean,
                        result={"type": "line", "points": points},
                        score=round(score, 4),
                    ))
                    continue

        results.append(ResultItem(
            toolName=tool,
            label=clean,
            result=_bbox_to_rect(box),
            score=round(score, 4),
        ))

    latency = int((time.perf_counter() - start) * 1000)
    warning = None if sam_model else "EfficientSAM not loaded; polygon results use bounding boxes"
    return PredictResponse(model=MODEL_LABEL, latency_ms=latency, results=results, warning_message=warning)


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_LABEL, "device": device, "sam_loaded": sam_model is not None}


# ── entrypoint ────────────────────────────────────────────────────────
def main():
    global dino_model, dino_processor, sam_model, sam_processor, device

    parser = argparse.ArgumentParser(description="LabelU GroundingDINO + EfficientSAM Model Server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--no-sam", action="store_true", help="Disable EfficientSAM (detection only)")
    parser.add_argument("--box-threshold", type=float, default=BOX_THRESHOLD)
    parser.add_argument("--text-threshold", type=float, default=TEXT_THRESHOLD)
    args = parser.parse_args()

    device = args.device
    global BOX_THRESHOLD, TEXT_THRESHOLD
    BOX_THRESHOLD = args.box_threshold
    TEXT_THRESHOLD = args.text_threshold

    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor as AP

    logger.info("Loading GroundingDINO (%s) on %s ...", DINO_MODEL_ID, device)
    dino_processor = AP.from_pretrained(DINO_MODEL_ID)
    dino_model = AutoModelForZeroShotObjectDetection.from_pretrained(DINO_MODEL_ID).to(device).eval()
    logger.info("GroundingDINO loaded.")

    if not args.no_sam:
        from transformers import EfficientSamModel, SamImageProcessor
        logger.info("Loading EfficientSAM (%s) on %s ...", SAM_MODEL_ID, device)
        sam_processor = SamImageProcessor.from_pretrained(SAM_MODEL_ID)
        sam_model = EfficientSamModel.from_pretrained(SAM_MODEL_ID).to(device).eval()
        logger.info("EfficientSAM loaded.")
    else:
        logger.info("EfficientSAM disabled (--no-sam).")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
