MAIN = pac-man.py
CONFIG = config.json
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test package

install:
	uv sync

run:
	uv run python $(MAIN) $(CONFIG)

debug:
	uv run python -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf .mypy_cache build dist
	find . -path ./.venv -prune -o -type d -name "__pycache__" -exec rm -rf {} +

lint:
	uv run flake8 .
	uv run mypy . $(MYPY_FLAGS)

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

test:
	PYTHONPATH=src uv run python -m unittest discover -s tests

package:
	uv run pyinstaller --noconfirm pacman.spec
