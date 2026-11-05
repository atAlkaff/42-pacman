"""Test configuration defaults, clamping, and level padding."""

import json
import os
import tempfile
import unittest

from utils.config_parser import (
    MAX_MAZE_SIZE, MIN_LEVELS, MIN_MAZE_SIZE, GameConfig, parse_config,
)


class ConfigParserTests(unittest.TestCase):
    """Every config a reviewer may write must give a playable game."""

    def setUp(self) -> None:
        """Use a temporary directory for config files."""
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "config.json")

    def tearDown(self) -> None:
        """Remove the temporary directory."""
        self.tmp.cleanup()

    def load(self, content: str) -> GameConfig:
        """Write ``content`` to a file and parse it."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)
        return parse_config(self.path)

    def test_defaults_have_ten_levels(self) -> None:
        """No file, no level key, or a broken level list: 10 levels."""
        self.assertEqual(len(GameConfig().level), MIN_LEVELS)
        self.assertEqual(len(parse_config("missing.json").level), MIN_LEVELS)
        self.assertEqual(len(self.load("{}").level), MIN_LEVELS)
        self.assertEqual(len(self.load('{"level": 5}').level), MIN_LEVELS)

    def test_short_level_list_is_padded(self) -> None:
        """Fewer than 10 levels repeat the configured ones."""
        config = self.load(json.dumps({"level": [
            {"width": 11, "height": 9}, {"width": 13, "height": 13},
        ]}))
        self.assertEqual(len(config.level), MIN_LEVELS)
        self.assertEqual(
            [lvl.width for lvl in config.level[:4]], [11, 13, 11, 13]
        )

    def test_long_level_list_is_kept(self) -> None:
        """More than 10 levels are all kept."""
        config = self.load(json.dumps({"level": [{"width": 5}] * 12}))
        self.assertEqual(len(config.level), 12)

    def test_sizes_are_clamped(self) -> None:
        """Too small or too large sizes are clamped, not rejected."""
        config = self.load(json.dumps({"level": [
            {"width": 1000, "height": -4},
        ]}))
        self.assertEqual(config.level[0].width, MAX_MAZE_SIZE)
        self.assertEqual(config.level[0].height, MIN_MAZE_SIZE)

    def test_invalid_size_type_uses_default(self) -> None:
        """A non-number size falls back to the default size."""
        config = self.load(json.dumps({"level": [
            {"width": "big", "height": True},
        ]}))
        self.assertEqual((config.level[0].width, config.level[0].height),
                         (21, 21))

    def test_hash_and_slash_comments(self) -> None:
        """Full-line # and // comments are ignored."""
        config = self.load("# comment\n{\n  // another\n  \"lives\": 5\n}\n")
        self.assertEqual(config.lives, 5)


if __name__ == "__main__":
    unittest.main()
