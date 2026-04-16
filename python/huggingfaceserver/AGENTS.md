# HuggingFace Server — Agent Guidelines

## Project Structure

This is a Python sub-project within the [KServe](https://github.com/kserve/kserve) monorepo.
The primary working directory is `python/huggingfaceserver/`.

Three local Python packages form a workspace dependency chain:

| Package | Path | Role |
| --------- | ------ | ------ |
| `huggingfaceserver` | `python/huggingfaceserver/` | Main application — HuggingFace/vLLM model serving |
| `kserve` | `python/kserve/` | SDK — OpenAI-compatible types, model server framework |
| `kserve-storage` | `python/storage/` | Storage utilities |

Dependencies are declared in each package's `pyproject.toml`. The huggingfaceserver
depends on `kserve[llm]` and `kserve-storage` as **local path dependencies**
(`file:///${PROJECT_ROOT}/../kserve`). They are **not** editable installs — they are
built and copied into the venv as regular packages.

Key external dependencies: `vllm` (from nightly index), `transformers`, `torch`.

## Package Manager: uv

This project uses **uv** exclusively. Never use `pip install` or `uv pip install`.

### Common Commands

Always `cd python/huggingfaceserver/` first.

```sh
# First-time setup (creates .venv, resolves deps, installs everything)
make dev_install          # runs: uv sync --active --group test

# After editing pyproject.toml in ANY of the 3 packages
uv lock --upgrade
uv sync --active --group test

# After editing source code in python/kserve/ or python/storage/
# (these are NOT editable installs, so the venv has a stale copy)
uv sync --active --group test --reinstall-package kserve
uv sync --active --group test --reinstall-package kserve-storage

# Run commands in the venv
uv run python -m huggingfaceserver --model_id=MODEL --model_name=NAME
uv pip show transformers vllm torch

# Run tests
make test
```

### Critical: kserve is NOT an editable install

When you modify source files under `python/kserve/`, the changes are **not** automatically
reflected in `python/huggingfaceserver/.venv/`. You must rebuild and reinstall:

```sh
cd python/huggingfaceserver
uv sync --active --group test --reinstall-package kserve
```

Without this step, the venv still contains the old built copy and your fixes won't take effect.

## Running the Server

Always run from `python/huggingfaceserver/`.

```sh
# CPU — encoder model (e.g. BERT)
uv run python -m huggingfaceserver --model_id=bert-base-uncased --model_name=bert

# GPU — generative model via vLLM
uv run python -m huggingfaceserver \
  --model_id=Qwen/Qwen3.5-0.8B --model_name=Qwen3.5 \
  --gpu_memory_utilization=0.7 --max_model_len=2048 --enforce-eager
```

The server listens on `http://0.0.0.0:8080` (REST) and `[::]:8081` (gRPC).

Example request to the OpenAI-compatible REST API:

```sh
curl -X POST http://localhost:8080/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

### Known issue: CUDA driver mismatch when running locally

The current vLLM nightly (0.19.x) ships `torch 2.11.0+cu130` which requires **CUDA 13.0**
and therefore an **NVIDIA driver ≥ 580**. If the host's NVIDIA driver only supports an
older CUDA version (e.g. driver 535 → CUDA 12.2), GPU models will fail at startup.

**Fix:** Update the NVIDIA driver to 580+ (`sudo apt install nvidia-driver-580`).

## Upgrading vLLM / Transformers

When upgrading `vllm` or `transformers` versions, breakage is expected because these
libraries frequently reorganize their internal module paths. E.g. the kserve SDK
(`python/kserve/kserve/protocol/rest/openai/types/__init__.py`) and
the vllm_model module (`huggingfaceserver/vllm/vllm_model.py`) import directly
from vllm internals.

### Troubleshooting import errors after an upgrade

1. **Identify the broken import** from the traceback (e.g. `ModuleNotFoundError: No module named 'vllm.entrypoints.pooling.score'`).

2. **Find the new location** in the installed vllm package:

```sh
cd python/huggingfaceserver
# List submodules to find renames
.venv/bin/python -c "import os; print(os.listdir('.venv/lib/python3.12/site-packages/vllm/entrypoints/pooling/'))"
# Test the new import path
.venv/bin/python -c "from vllm.entrypoints.pooling.scoring.protocol import RerankRequest; print('OK')"
```

1. **Fix imports** in both places — check all files that import from vllm:

```sh
grep -rn "from vllm\." python/kserve/kserve/ python/huggingfaceserver/huggingfaceserver/
```

1. **Rebuild kserve** if you changed files under `python/kserve/`:

```sh
cd python/huggingfaceserver
uv sync --active --group test --reinstall-package kserve
```

1. **Verify** the fix:

```sh
uv run python -m huggingfaceserver --model_id=bert-base-uncased --model_name=bert
```

### Updating pyproject.toml

vLLM nightly builds come from a custom index configured in `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "vllm-nightly"
url = "https://wheels.vllm.ai/nightly"

[tool.uv.sources]
vllm = { index = "vllm-nightly" }
```

After changing version constraints in any `pyproject.toml`:

```sh
cd python/huggingfaceserver
uv lock --upgrade
uv sync --active --group test
```

## Testing

```sh
cd python/huggingfaceserver
make test  # runs mypy + pytest
pytest -W ignore  # tests only
```

## VS Code

The workspace is configured to use `python/huggingfaceserver/.venv/bin/python` as the
Python interpreter for Pylance. If code navigation doesn't work, select this interpreter
via Ctrl+Shift+P → "Python: Select Interpreter".
