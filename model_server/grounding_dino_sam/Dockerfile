FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Pre-download models at build time
RUN python -c "\
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection; \
AutoProcessor.from_pretrained('IDEA-Research/grounding-dino-tiny'); \
AutoModelForZeroShotObjectDetection.from_pretrained('IDEA-Research/grounding-dino-tiny'); \
from transformers import EfficientSamModel, SamImageProcessor; \
SamImageProcessor.from_pretrained('ybelkada/efficient-sam-vitt'); \
EfficientSamModel.from_pretrained('ybelkada/efficient-sam-vitt')"

EXPOSE 5000
CMD ["python", "server.py", "--device", "cpu"]
