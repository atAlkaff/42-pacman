MAIN = pac-man.py
CONFIG = config.json
# Platform label in the release zip name, e.g. `make release PLATFORM=windows`.
PLATFORM ?= linux
RELEASE_DIR = release
RELEASE_ZIP = PacMan-$(PLATFORM).zip
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test package release

install:
	uv sync

run:
	uv run python $(MAIN) $(CONFIG)

debug:
	uv run python -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf .mypy_cache build dist $(RELEASE_DIR) PacMan-*.zip
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

# Build the game, then zip it with an editable config.json and the README,
# ready to upload to itch.io. Python's zipfile keeps the executable bit, and
# unlike `zip` it is always available.
release: package
	rm -rf $(RELEASE_DIR) $(RELEASE_ZIP)
	mkdir -p $(RELEASE_DIR)/PacMan
	cp dist/PacMan* config.json README.md $(RELEASE_DIR)/PacMan/
	uv run python -m zipfile -c $(RELEASE_ZIP) $(RELEASE_DIR)/PacMan
	@echo "Created $(RELEASE_ZIP): upload it to itch.io as the $(PLATFORM) build."
