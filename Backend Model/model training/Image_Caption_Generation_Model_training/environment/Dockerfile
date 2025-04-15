# hash:sha256:d3bb9149c823020028717ec6bf1c229fcf536163ceb633ced8054e6a319d8976
FROM registry.codeocean.com/codeocean/miniconda3:4.9.2-cuda11.7.0-cudnn8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN pip install -U --no-cache-dir \
    jupyter \
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
