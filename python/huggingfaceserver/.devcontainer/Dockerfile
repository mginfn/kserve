# Use CUDA base image for GPU support (matching host CUDA 12.2)
# For CPU-only, use: FROM python:3.12-slim
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

ARG PYTHON_VERSION=3.12
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12
RUN apt-get update -y && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1

# Install system dependencies
RUN apt-get update -y \
    && apt-get install -y \
        build-essential \
        git \
        curl \
        sudo \
        ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install uv for the non-root user
USER $USERNAME
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Create cache directories with proper permissions
RUN mkdir -p /home/${USERNAME}/.cache/uv && \
    mkdir -p /home/${USERNAME}/.cache/huggingface

# Set working directory
WORKDIR /workspace

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV UV_PYTHON_PREFERENCE=only-system

# Keep container running
CMD ["/bin/bash"]
