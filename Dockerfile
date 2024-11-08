FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# 환경 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    unzip \
    cmake \
    pkg-config \
    libcairo2-dev \
    # GStreamer 설치
    libnice-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-nice \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    python3-gst-1.0 \
    #apt-get 초기화
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# meson 빌더 설치
RUN wget https://github.com/mesonbuild/meson/releases/download/0.63.3/meson-0.63.3.tar.gz \
    && tar -xvf meson-0.63.3.tar.gz \
    && cd meson-0.63.3 \
    && python3 setup.py install \
    && cd .. \
    && rm -rf meson-0.63.3 meson-0.63.3.tar.gz

# ninja 빌더 설치
RUN wget https://github.com/ninja-build/ninja/releases/download/v1.10.2/ninja-linux.zip \
    && unzip ninja-linux.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/ninja \
    && rm ninja-linux.zip

# Python 종속성 설치
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . /app
WORKDIR /app

# webrtcbin 확인
CMD ["python3", "main.py"]
