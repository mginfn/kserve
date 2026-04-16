# AGENTS

This is the root of the [KServe](https://github.com/kserve/kserve) monorepo.

The main project is the HuggingFace Server, which serves HuggingFace and vLLM models with an OpenAI-compatible API.
It is implemented in Python and located in `python/huggingfaceserver/`.

See `python/huggingfaceserver/AGENTS.md` for details on project structure and package management.

From the root of the monorepo, you can build the HuggingFace Server image defined in `python/huggingface_server.Dockerfile` with:

```sh
export KO_DOCKER_REPO=docker.io/mginfn
export HUGGINGFACE_IMG=kserve-huggingfaceserver
make docker-build-huggingface
```
