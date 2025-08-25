# SPDX-License-Identifier: AGPL-3.0-only
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
# Make Ultralytics config writeable
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics

# System libs for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgl1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy deps
COPY requirements.txt /tmp/requirements.txt

# IMPORTANT: install numpy<2 first, then the rest
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy app + weights
COPY app/ ./
COPY app/best.pt /app/best.pt

# Defaults (override with -e if needed)
ENV MODEL_PATH=best.pt
ENV CONFIDENCE_THRESHOLD=0.5
ENV INPUT_ROOT=/../data-in
ENV OUTPUT_ROOT=/../data-out
ENV USE_GPU=false
ENV SAVE_SUMMARY=false
# IO dirs (bind-mount at runtime)
RUN mkdir -p /data-in /data-out

LABEL org.opencontainers.image.title="YOLO Parking Sign Detector"
LABEL org.opencontainers.image.description="Detects Slovakian parking signs; writes per-image JSON and a summary CSV."
LABEL org.opencontainers.image.licenses="AGPL-3.0-only"

ENTRYPOINT [ "bash", "-c", "python main.py --folder \"$INPUT_ROOT\" --out \"$OUTPUT_ROOT\"; exec bash" ]