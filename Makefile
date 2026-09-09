CONFIG?=config.txt

.PHONY: install run debug clean test lint lint-strict build

install:
	uv sync

run:
	uv run python3 a_maze_ing.py $(CONFIG)

debug:
	uv run python3 -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -type d \( -name ".mypy_cache" -o -name "__pycache__" -o -name ".pytest_cache" \) -prune -exec rm -rf {} +

fclean: clean
	rm -rf .venv/ maze.txt *.whl

test:
	uv run pytest

build:
	uv build --wheel --out-dir .

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	              --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict