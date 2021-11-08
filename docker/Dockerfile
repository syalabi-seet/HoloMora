FROM nvcr.io/nvidia/tensorrt:21.10-py3

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    libsndfile1 \
    libportaudio2 \
    ffmpeg \
    libsm6 \
    libxext6 \
    xcb \
    libxcb.*-dev \ 
    libx11-xcb-dev \
    libglu1-mesa-dev \
    libxrender-dev \
    libxi-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

LABEL maintainer="Syalabi Seet"

ENV PYTHONUNBUFFERED=TRUE
ENV TOKENIZERS_PARALLELISM=false

COPY . /usr/src/app