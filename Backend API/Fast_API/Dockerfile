# Use an official Python 3.8 base image
FROM python:3.8.5

# Set environment variables to prevent interactive prompts
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy==1.21.5 \
    tensorflow==2.8.0 \
    keras==2.6.0 \
    fastapi[all]==0.100.0 \
    uvicorn[standard]==0.23.0 \
    loguru==0.7.2 \
    protobuf==3.20.3

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
