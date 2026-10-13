NAME="rag.py"

CACHE_FOLDER=$(HOME)/goinfre/rag_cache/
export UV_PROJECT_ENVIRONMENT=$(CACHE_FOLDER).venv/"
export HF_HUB_CACHE=$(CACHE_FOLDER)hugging_face/"
export HF_HOME=$(CACHE_FOLDER)hugging_face/"
export UV_CACHE_DIR=$(CACHE_FOLDER)uv/"


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
