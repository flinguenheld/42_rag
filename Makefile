NAME="rag.py"

# uv run hf env
CACHE_FOLDER=~/goinfre/rag_cache/
CACHE_LLM=$(CACHE_FOLDER)hugging_face
CACHE_UV=$(CACHE_FOLDER)uv

export HF_HUB_CACHE=$(CACHE_LLM)
export HF_HOME=$(CACHE_LLM)
UV=uv --cache-dir $(CACHE_UV)

install:
	$(UV) sync

run:
	$(UV) run python -m src

helix:
	$(UV) run hx .

debug:
	$(UV) run python -m src

clean:
	$(UV) cache clean
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
