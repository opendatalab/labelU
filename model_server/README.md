# LabelU Model Server

LabelU 自动标注功能的参考模型服务实现。提供两套方案，均实现统一的 API 协议。

## 方案对比

| | Florence-2 | GroundingDINO + EfficientSAM |
|---|---|---|
| 开放词汇 | 支持 | 支持 |
| 检测 (rectTool) | 好 | 很好 |
| 分割 (polygonTool) | 支持 | 精度更高 |
| 最低显存 | ~4GB (base) | ~4GB (tiny + vitt) |
| CPU 可用 | 可以（较慢） | 不推荐 |
| 模型大小 | ~500MB | ~900MB |
| 部署复杂度 | 低 | 中 |

**推荐**：有 GPU 选 GroundingDINO+SAM，只有 CPU 或显存紧张选 Florence-2。

## 快速启动

### Florence-2

```bash
cd model_server/florence2
pip install -r requirements.txt
python server.py --device cpu --port 5000
```

### GroundingDINO + EfficientSAM

```bash
cd model_server/grounding_dino_sam
pip install -r requirements.txt
python server.py --device cuda --port 5000

# 仅检测（不加载 SAM，节省显存）
python server.py --device cuda --port 5000 --no-sam
```

### Docker

```bash
# Florence-2
cd model_server/florence2
docker build -t labelu-florence2 .
docker run -p 5000:5000 labelu-florence2

# GroundingDINO + EfficientSAM (GPU)
cd model_server/grounding_dino_sam
docker build -t labelu-dino-sam .
docker run --gpus all -p 5000:5000 labelu-dino-sam python server.py --device cuda
```

## 配置 LabelU 连接

在 LabelU 的 `.env` 或环境变量中设置：

```env
AI_AUTO_LABEL_ENABLED=true
AI_MODEL_ENDPOINT=http://localhost:5000/
AI_MODEL_TIMEOUT_SECONDS=60
AI_MODEL_NAME=florence-2-base     # 或 grounding-dino-tiny+efficient-sam
```

## API 协议

### POST /

**请求：**

```json
{
  "request_id": "uuid",
  "image_url": "https://presigned-or-public-url/image.jpg",
  "task": { "id": 10, "name": "demo-task" },
  "labels": [
    { "name": "car", "tool": "rectTool" },
    { "name": "person", "tool": "polygonTool" }
  ],
  "constraints": {
    "allowed_tools": ["rectTool", "polygonTool"],
    "max_results_per_label": 100
  },
  "prompt": null
}
```

**响应：**

```json
{
  "model": "microsoft/Florence-2-base",
  "latency_ms": 1840,
  "results": [
    {
      "toolName": "rectTool",
      "label": "car",
      "result": { "x": 120, "y": 80, "width": 260, "height": 140 },
      "score": 0.94
    },
    {
      "toolName": "polygonTool",
      "label": "person",
      "result": {
        "type": "line",
        "points": [
          { "x": 50, "y": 100 },
          { "x": 80, "y": 200 },
          { "x": 30, "y": 200 }
        ]
      },
      "score": 0.87
    }
  ],
  "warning_message": null
}
```

### GET /health

返回模型加载状态。

## 自定义模型

如果要接入其他模型，只需实现上述 API 协议即可。LabelU 后端通过 HTTP POST 调用模型服务，不感知具体模型实现。
