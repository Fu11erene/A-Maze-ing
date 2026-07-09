.PHONY: install run debug clean lint lint-strict build

install:
	uv sync

run:
	uv run a_maze_ing.py config.txt

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -type d \( -name ".mypy_cache" -o -name "__pycache__" \) -prune -exec rm -rf {} +

lint:
	flake8 . ; mypy . --warn-return-any \
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs

lint-strict:
	flake8 . ; mypy . --strict