install:
	uv sync

run:
	python3 a_maze_ing.py config.txt

clean:
	find ./ -type d -name ".mypy_cache" -o -name "__pycache__" -prune -exec rm -rf {} \;

lint:
	flake8 . && mypy . --warn-return-any \
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs

lint-strict:
	flake8 . && mypy . --strict