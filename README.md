*This project has been created as part of the 42 curriculum by [flinguen](https://linguenheld.net/)*

## 42_rag
RAG against the machine. Will you answer my questions?

### Ressources
[vllm](https://docs.vllm.ai/en/latest/)


### Usage

This project uses [UV](https://docs.astral.sh/uv/) for automatic virtual environment management.  
Once installed, you can use it with the Makefile with these commands:

On the 42's computers, the session space is limited: first put the virtual
environment, the uv cache and the Hugging Face models in the *goinfre* folder.
The script has to be **sourced** (not executed), in every new terminal:

```Bash
source export_to_goinfre.sh      # bash / zsh
source export_to_goinfre.fish    # fish
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
