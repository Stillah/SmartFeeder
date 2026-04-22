# Use official PyTorch image with CUDA 12.4 and Python 3.11
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (OpenCV requires libgl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install remaining Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model weights
COPY . .

EXPOSE 8080

CMD ["python", "app.py"]