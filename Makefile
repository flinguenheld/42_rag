NAME="rag.py"

# On 42 computers, run `source export_to_goinfre.sh` (or .fish) first:
# make inherits the variables, so every rule uses the goinfre.
# Otherwise, uv's default locations are used.
VENV := $(or $(UV_PROJECT_ENVIRONMENT),.venv)


install:
	uv sync

run:
	uv run python -m src

helix:
	uv run hx .

debug:
	uv run python -m pdb -m src

clean:
	find . -name __pycache__ -not -path './data/*' -prune -exec rm -rf {} +
	rm -rf .mypy_cache

fclean: clean
	uv cache clean
	rm -rf $(VENV)
	$(if $(HF_HOME),rm -rf $(HF_HOME))

lint:
	- uv run flake8 . --extend-exclude '.venv/,data/'
	- uv run mypy . --warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs \
			--exclude 'data/'

.PHONY: install run helix debug clean fclean lint
