*This project has been created as part of the 42 curriculum by [flinguen](https://linguenheld.net/)*

## 42_rag
RAG against the machine. Will you answer my questions?

### Ressources
[vllm](https://docs.vllm.ai/en/latest/)


### Usage

This project uses [UV](https://docs.astral.sh/uv/) for automatic virtual environment management.  
Once installed, you can use it with the Makefile with these commands:

On the 42's computers, uncomment the following lines to put the cache in the *goinfre* folder:

```Bash
UV_CACHE_DIR = "~/goinfre/.cache_rag"
export UV_CACHE_DIR
```

```Bash
    make install
    make clean
    make lint
```
Usage:
```Bash
    uv run python -m src --help
```
