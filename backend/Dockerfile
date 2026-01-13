FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first (much smaller, no CUDA dependencies)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies with increased timeout and retries
RUN pip install --no-cache-dir --default-timeout=300 -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
# Cloud Run expects PORT 8080 by default
ENV PORT=8080
ENV HOST=0.0.0.0

# Expose the port Cloud Run expects
EXPOSE 8080

CMD ["python", "run.py"]
