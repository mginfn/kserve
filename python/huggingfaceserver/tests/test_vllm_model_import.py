from pathlib import Path
import sys

import pytest

pytest.importorskip("vllm", reason="vllm not installed")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from huggingfaceserver.vllm.vllm_model import VLLMModel


def test_vllm_model_module_imports():
    assert VLLMModel is not None
