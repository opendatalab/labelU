# LabelU Model Server

LabelU 自动标注功能的参考模型服务实现。提供三套方案，均实现统一的 API 协议。

## 方案对比

| | Florence-2 | GroundingDINO + EfficientSAM | SAM 3 |
|---|---|---|---|
| 架构 | 单模型（检测+分割分步） | 两模型串联 | 单模型统一 |
| 开放词汇 | 支持 | 支持 | 支持（400万+概念） |
| 检测 (rectTool) | 一般 | 很好 | 很好 |
| 分割 (polygonTool) | 支持 | 精度高 | 精度最高 |
| 最低显存 | ~4GB (base) | ~4GB (tiny + vitt) | ~8GB |
| CPU 可用 | 可以（较慢） | 不推荐 | 不支持 |
| 模型大小 | ~500MB | ~900MB | ~1.7GB (848M params) |
| 部署复杂度 | 低 | 中 | 中 |
| Python 要求 | 3.8+ | 3.8+ | **3.12+** |
| PyTorch 要求 | 2.1+ | 2.1+ | **2.7+** |
| CUDA 要求 | 可选 | 推荐 | **12.6+（必须）** |
| GPU 算力要求 | 无限制 | 无限制 | **SM 80+（Ampere/Ada）** |

**推荐**：
- 有 4090/A100 等高端 GPU → **SAM 3**（质量最好，单模型最简单）
- 有中端 GPU（如 1660/2060） → **GroundingDINO + EfficientSAM**
- 只有 CPU 或显存紧张 → **Florence-2**

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

### SAM 3

```bash
# 需要 Python 3.12+, CUDA 12.6+
conda create -n sam3 python=3.12
conda activate sam3
pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128

cd model_server/sam3
pip install -r requirements.txt
python server.py --device cuda --port 5000
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

# SAM 3 (GPU, CUDA 12.6+)
cd model_server/sam3
docker build -t labelu-sam3 .
docker run --gpus all -p 5000:5000 labelu-sam3
```

## 配置 LabelU 连接

在 LabelU 的 `.env` 或环境变量中设置：

```env
AI_AUTO_LABEL_ENABLED=true
AI_MODEL_ENDPOINT=http://localhost:5000/
AI_MODEL_TIMEOUT_SECONDS=60
AI_MODEL_NAME=florence-2-base     # 或 grounding-dino-tiny+efficient-sam / sam3
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
    "max_results_per_label": 100,
    "filter_by_labels": false
  },
  "prompt": null
}
```

**constraints 字段说明：**

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `allowed_tools` | string[] | [] | 限制返回的工具类型，为空不限制 |
| `max_results_per_label` | int | 100 | 每个标签最多返回的结果数 |
| `filter_by_labels` | bool | false | 是否过滤掉不在 labels 列表中的检测结果 |

`filter_by_labels` 说明：
- `false`（默认）：模型检测到什么就返回什么，标签名作为 prompt 提示但不做过滤
- `true`：仅返回与配置标签名精确匹配的结果

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
