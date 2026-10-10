NAME="rag.py"

# uv run hf env
CACHE_FOLDER=~/goinfre/rag_cache/
CACHE_VENV=$(CACHE_FOLDER).venv
CACHE_LLM=$(CACHE_FOLDER)hugging_face
CACHE_UV=$(CACHE_FOLDER)uv

export UV_PROJECT_ENVIRONMENT=$(CACHE_VENV)
export HF_HUB_CACHE=$(CACHE_LLM)
export HF_HOME=$(CACHE_LLM)

install:
	uv sync

run:
	uv run python -m src

helix:
	uv run hx .

debug:
	uv run python -m src

clean:
	uv cache clean
	rm -rf $(CACHE_FOLDER)
	rm -rf __pycache__ .mypy_cache .venv uv.lock

lint:
	- uv run flake8 . --extend-exclude \
			'.venv/,vllm/,$(CACHE_FOLDER)'
	- uv run mypy . --warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs \
			--exclude 'vllm/' \
			--exclude $(CACHE_FOLDER)

lint-strict:
	- uv run flake8 . --extend-exclude '.venv,llm_sdk/'
	- uv run mypy . --strict --exclude 'llm_sdk/'

.PHONY: install run helix debug clean lint lint-strict
