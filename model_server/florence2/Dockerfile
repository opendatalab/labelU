FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Pre-download model at build time (optional, ~500MB)
RUN python -c "from transformers import AutoModelForCausalLM, AutoProcessor; \
    AutoProcessor.from_pretrained('microsoft/Florence-2-base', trust_remote_code=True); \
    AutoModelForCausalLM.from_pretrained('microsoft/Florence-2-base', trust_remote_code=True)"

EXPOSE 5000
CMD ["python", "server.py", "--device", "cpu"]
