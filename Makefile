NAME="rag.py"

UV_CACHE_DIR = .cache_rag
export UV_CACHE_DIR

install:
	uv sync

helix:
	uv run hx .

debug:
	uv run python -m src

clean:
	uv cache clean
	rm -rf __pycache__ .mypy_cache .venv uv.lock

lint:
	uv run flake8 . --extend-exclude \
			'.venv/,vllm/,.cache_rag'
	uv run mypy . --warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs \
			--exclude 'vllm/' \
			--exclude '.cache_rag/'

lint-strict:
	- uv run flake8 . --extend-exclude '.venv,llm_sdk/'
	- uv run mypy . --strict --exclude 'llm_sdk/'

.PHONY: install helix debug clean lint lint-strict
