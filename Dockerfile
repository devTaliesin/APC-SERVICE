# Base image with Ubuntu
FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# Install basic utilities and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-gi \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 
    

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


# Copy application files
COPY . /app
WORKDIR /app

# Set default command
CMD ["python3", "main.py"]
