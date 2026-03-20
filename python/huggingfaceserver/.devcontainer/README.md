# HuggingFace Server Dev Container

This devcontainer setup provides a complete development environment for the KServe HuggingFace Server with all dependencies pre-configured.

## Features

- **NVIDIA CUDA 12.8.1** support for GPU acceleration (optional)
- **Python 3.12** with all required dependencies
- **uv** package manager for fast dependency management
- **Pre-configured VSCode extensions** for Python development:
  - Python
  - Pylance
  - Black formatter
  - Mypy type checker
  - Ruff linter

## Requirements

- [Docker](https://www.docker.com/products/docker-desktop)
- [VSCode](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- (Optional) NVIDIA GPU with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU support

## Getting Started

### 1. Open in Dev Container

1. Open the `huggingfaceserver` folder in VSCode
2. Press `F1` or `Ctrl+Shift+P` to open the command palette
3. Select **"Dev Containers: Reopen in Container"**
4. Wait for the container to build and start (first time may take 10-15 minutes)
5. Dependencies will be installed automatically via the `postCreateCommand`

### 2. Without GPU Support

If you don't have an NVIDIA GPU, edit `.devcontainer/devcontainer.json` and:

1. Comment out or remove the `runArgs` section:

   ```json
   // "runArgs": [
   //   "--gpus=all"
   // ],
   ```

2. Optionally, change the base image in `.devcontainer/Dockerfile` to a non-CUDA version:

   ```dockerfile
   FROM python:3.12-slim
   ```

   And remove CUDA-related setup steps.

## Usage

### Running the HuggingFace Server

Once inside the container, you can run the server:

```bash
# Run with a specific model
uv run python -m huggingfaceserver --model_id=bert-base-uncased --model_name=bert
uv run python -m huggingfaceserver --model_id=Qwen/Qwen2.5-0.5B-Instruct-GPTQ-Int4 --model_name=qwen \
  --max_num_seqs=4 \
  --gpu_memory_utilization=0.5 \
  --max_model_len=2048 \
  --enforce_eager

# Run with custom dtype
python -m huggingfaceserver --model_id=bert-base-uncased --model_name=bert --dtype=float16
```

The server will be available at:

- **HTTP**: `http://localhost:8080`
- **gRPC**: `http://localhost:8081`

### Testing the Server

In a new terminal (inside the container):

```bash
curl -H "content-type:application/json" -v localhost:8080/v1/models/bert:predict \
  -d '{"instances": ["The capital of france is [MASK]."] }'
```

### Development Commands

```bash
# Install development dependencies
make dev_install

# Run tests
make test

# Type checking
make type_check
```

## Ports

The following ports are automatically forwarded:

- **8080**: HTTP server
- **8081**: gRPC server

## Persistent Storage

The devcontainer uses a Docker volume to persist the HuggingFace model cache at `/home/vscode/.cache/huggingface`, so downloaded models won't need to be re-downloaded when recreating the container.

## Environment Variables

The following environment variables are pre-configured:

- `SAFETENSORS_FAST_GPU=1`: Improves model loading performance
- `HF_HUB_DISABLE_TELEMETRY=1`: Disables HuggingFace telemetry
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered

## Troubleshooting

### Container fails to start with GPU errors

- Ensure NVIDIA Container Toolkit is installed
- Check Docker can access your GPU: `docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi`
- Remove GPU support as described in the "Without GPU Support" section

### Dependencies installation fails

- Check the logs in the VSCode terminal
- Manually run: `cd /workspace/huggingfaceserver && make dev_install`
- Try rebuilding the container: Command Palette → "Dev Containers: Rebuild Container"

### Port already in use

- Check if another service is using ports 8080 or 8081
- Stop the conflicting service or change the ports in `devcontainer.json`

## Additional Resources

- [HuggingFace Server README](../README.md)
- [KServe Documentation](https://kserve.github.io/website/)
- [VSCode Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
