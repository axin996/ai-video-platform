FROM nvidia/cuda:12.4.0-cudnn-devel-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.12 /usr/bin/python

RUN pip install --no-cache-dir --upgrade pip

# Pre-install PyTorch and audio dependencies
RUN pip install --no-cache-dir \
    torch torchaudio --index-url https://download.pytorch.org/whl/cu124 \
    flask \
    flask_cors \
    soundfile \
    numpy

# CosyVoice model files should be mounted at /app/models
# Copy the CosyVoice API server code
COPY api.py /app/api.py

ENV NVIDIA_VISIBLE_DEVICES=0
ENV CUDA_VISIBLE_DEVICES=0

EXPOSE 9880

CMD ["python", "api.py", "--port", "9880", "--model_dir", "/app/models"]
