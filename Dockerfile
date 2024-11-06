FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
# 기본 빌더 설치
    build-essential \
    pkg-config \
    libcairo2-dev \
    meson \
# 파이선 설치
    python3 \
    python3-pip \
# GI Object 설치
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
# apt 초기화
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 
    

# 파이썬 종속성 설치
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "main.py"]
