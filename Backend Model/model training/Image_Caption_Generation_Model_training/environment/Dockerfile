# hash:sha256:910977a567ba90ef66831fc972782b8013a23bba486e56dc97aa4464410807ae
FROM registry.codeocean.com/codeocean/miniconda3:4.9.2-cuda11.7.0-cudnn8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1=1.3.2-1~ubuntu0.20.04.2 \
        libglib2.0-0=2.64.6-1~ubuntu20.04.8 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir \
    jupyter==1.1.1 \
    keras==2.6.0 \
    matplotlib==3.5.3 \
    nltk==3.6.5 \
    numpy==1.21.5 \
    opencv-python==4.11.0.86 \
    protobuf==3.20.0 \
    pydot==2.0.0 \
    scikit-image==0.19.1 \
    tensorflow==2.8.0 \
    tensorflow-addons==0.15.0

COPY postInstall /
RUN /postInstall
