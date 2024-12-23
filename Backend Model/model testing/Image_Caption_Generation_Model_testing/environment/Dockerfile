# hash:sha256:4116c74f85b41437b1a1b30f18291bd054c9643915ad6174c2ef359fb9923b88
FROM registry.codeocean.com/codeocean/miniconda3:4.9.2-cuda11.7.0-cudnn8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN pip install -U --no-cache-dir \
    jupyter==1.0.0 \
    keras==2.6.0 \
    matplotlib==3.5.3 \
    nltk==3.6.5 \
    numpy==1.21.5 \
    opencv-python-headless==4.5.4.60 \
    protobuf==3.20.0 \
    pydot==2.0.0 \
    scikit-image==0.19.1 \
    tensorflow==2.8.0 \
    tensorflow-addons==0.15.0
