"""Test menus, name entry, highscore persistence, and cheat keys."""

import json
import os
import random
import tempfile
import unittest
from unittest.mock import patch

import pygame

from controllers.cheat_manager import CheatManager
from controllers.game_engine import GameEngine
from models.entities import Ghost, Player
from models.maze_state import MazeState
from utils.config_parser import GameConfig
from utils.highscore_system import HighscoreSystem


def key_event(key: int, char: str = "") -> pygame.event.Event:
    """Build a KEYDOWN event like pygame would send it."""
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=char)


class HighscoreSystemTests(unittest.TestCase):
    """The highscore file must survive every kind of bad input."""

    def setUp(self) -> None:
        """Use a fresh temporary directory for each test."""
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "scores.json")

    def tearDown(self) -> None:
        """Remove the temporary directory."""
        self.tmp.cleanup()

    def write(self, content: str) -> None:
        """Write raw text to the highscore file."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)

    def test_missing_file_starts_empty(self) -> None:
        """No file yet is a normal first run."""
        self.assertEqual(HighscoreSystem(self.path).top_scores(), [])

    def test_bad_files_start_empty(self) -> None:
        """Invalid JSON, wrong types and a directory never crash."""
        for content in ("{not json", '{"a": 1}', "42", ""):
            self.write(content)
            self.assertEqual(HighscoreSystem(self.path).top_scores(), [])
        self.assertEqual(HighscoreSystem(self.tmp.name).top_scores(), [])

    def test_invalid_bytes_start_empty(self) -> None:
        """A file that is not UTF-8 is ignored."""
        with open(self.path, "wb") as f:
            f.write(b"\xff\xfe\x00garbage")
        self.assertEqual(HighscoreSystem(self.path).top_scores(), [])

    def test_invalid_entries_are_skipped(self) -> None:
        """Only well-formed entries are kept, sorted best first."""
        self.write(json.dumps([
            {"name": "ok", "score": 5},
            {"name": "neg", "score": -1},
            {"name": "str", "score": "9"},
            {"name": "bool", "score": True},
            {"score": 3},
            "junk",
            {"name": "best!!", "score": 50},
        ]))
        self.assertEqual(
            HighscoreSystem(self.path).top_scores(),
            [("best", 50), ("ok", 5)],
        )

    def test_names_are_cleaned(self) -> None:
        """Names keep letters, digits, spaces; max 10; never empty."""
        clean = HighscoreSystem.clean_name
        self.assertEqual(clean("Bob!@# 42"), "Bob 42")
        self.assertEqual(clean("abcdefghijklmnop"), "abcdefghij")
        self.assertEqual(clean("   "), HighscoreSystem.DEFAULT_NAME)
        self.assertEqual(clean("é!"), HighscoreSystem.DEFAULT_NAME)

    def test_keeps_top_ten_and_persists(self) -> None:
        """Only the 10 best scores are written and reloaded."""
        system = HighscoreSystem(self.path)
        for score in range(15):
            self.assertTrue(system.save_score(f"p{score}", score))
        reloaded = HighscoreSystem(self.path).top_scores()
        self.assertEqual(len(reloaded), 10)
        self.assertEqual(reloaded[0], ("p14", 14))
        self.assertEqual(reloaded[-1], ("p5", 5))

    def test_negative_score_is_rejected(self) -> None:
        """Scores are non-negative integers."""
        system = HighscoreSystem(self.path)
        self.assertFalse(system.save_score("x", -5))
        self.assertEqual(system.top_scores(), [])

    def test_unwritable_file_does_not_crash(self) -> None:
        """Saving into a missing folder fails cleanly."""
        bad = os.path.join(self.tmp.name, "missing", "scores.json")
        system = HighscoreSystem(bad)
        self.assertFalse(system.save_score("x", 5))


class EngineMenuTests(unittest.TestCase):
    """Drive the real engine's menus without opening a window."""

    def setUp(self) -> None:
        """Build an engine on a tiny maze with a temporary score file."""
        self.tmp = tempfile.TemporaryDirectory()
        path = os.path.join(self.tmp.name, "scores.json")
        engine = GameEngine.__new__(GameEngine)
        engine.current_state = GameEngine.STATE_MENU
        engine.config = GameConfig(highscore_filename=path)
        engine.highscores = HighscoreSystem(path)
        engine.cheat_manager = CheatManager()
        engine.menu_index = 0
        engine.pause_index = 0
        engine.name_input = ""
        engine._running = True
        engine._held_move_keys = []
        engine._move_elapsed = 0.0
        engine._respawn_pause = 0.0
        engine._rng = random.Random(0)
        engine.time_left = 90.0
        engine.level = 1
        engine.maze = MazeState([
            [1, 1, 1, 1, 1],
            [1, 0, 2, 0, 1],
            [1, 2, 0, 2, 1],
            [1, 1, 1, 1, 1],
        ])
        engine.player = Player(2, 2, 3)
        engine.ghosts = [Ghost(1, 1)]
        self.engine = engine

    def tearDown(self) -> None:
        """Remove the temporary directory."""
        self.tmp.cleanup()

    def press(self, key: int, char: str = "") -> None:
        """Send one key press to the engine."""
        self.engine._handle_input(key_event(key, char))

    def type_text(self, text: str) -> None:
        """Type characters one by one."""
        for char in text:
            self.press(pygame.K_a, char)

    def test_menu_navigation_wraps(self) -> None:
        """Up from the first item selects the last one (Exit)."""
        self.press(pygame.K_UP)
        self.assertEqual(
            GameEngine.MENU_ITEMS[self.engine.menu_index],
            GameEngine.MENU_EXIT,
        )
        self.press(pygame.K_s)
        self.assertEqual(self.engine.menu_index, 0)

    def test_menu_opens_screens_and_back(self) -> None:
        """Highscores and Instructions open, and ESC returns."""
        self.press(pygame.K_DOWN)
        self.press(pygame.K_RETURN)
        self.assertEqual(
            self.engine.current_state, GameEngine.STATE_HIGHSCORES
        )
        self.press(pygame.K_ESCAPE)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_MENU)
        self.press(pygame.K_DOWN)
        self.press(pygame.K_SPACE)
        self.assertEqual(
            self.engine.current_state, GameEngine.STATE_INSTRUCTIONS
        )
        self.press(pygame.K_RETURN)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_MENU)

    def test_exit_stops_the_loop(self) -> None:
        """Choosing Exit ends the game loop."""
        self.press(pygame.K_UP)
        self.press(pygame.K_RETURN)
        self.assertFalse(self.engine._running)

    def test_start_game(self) -> None:
        """Start Game begins level 1."""
        with patch.object(self.engine, "_init_level") as init:
            self.press(pygame.K_RETURN)
            init.assert_called_once_with()
        self.assertEqual(self.engine.current_state, GameEngine.STATE_PLAYING)
        self.assertEqual(self.engine.level, 1)

    def test_pause_menu_returns_to_main_menu(self) -> None:
        """Pause, select Main Menu, confirm."""
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.press(pygame.K_ESCAPE)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_PAUSED)
        self.press(pygame.K_DOWN)
        self.press(pygame.K_RETURN)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_MENU)

    def test_pause_menu_resume(self) -> None:
        """Pause, then confirm Resume."""
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.press(pygame.K_ESCAPE)
        self.press(pygame.K_RETURN)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_PLAYING)

    def test_name_entry_saves_score(self) -> None:
        """Typing a name and pressing ENTER saves it, then shows the menu."""
        self.engine.player.score = 1234
        self.engine._end_game(GameEngine.STATE_GAME_OVER)
        self.type_text("Al!ce Smith_long")
        self.assertEqual(self.engine.name_input, "Alce Smith")
        self.press(pygame.K_BACKSPACE)
        self.press(pygame.K_RETURN)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_MENU)
        reloaded = HighscoreSystem(self.engine.config.highscore_filename)
        self.assertEqual(reloaded.top_scores(), [("Alce Smit", 1234)])

    def test_name_entry_escape_skips_saving(self) -> None:
        """ESC on the victory screen returns without saving."""
        self.engine._end_game(GameEngine.STATE_VICTORY)
        self.type_text("Bob")
        self.press(pygame.K_ESCAPE)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_MENU)
        self.assertEqual(self.engine.highscores.top_scores(), [])

    def test_last_level_leads_to_victory_name_entry(self) -> None:
        """Clearing the final level opens the victory screen."""
        self.engine.level = len(self.engine.config.level)
        self.engine._advance_level()
        self.assertEqual(self.engine.current_state, GameEngine.STATE_VICTORY)
        self.assertEqual(self.engine.name_input, "")

    def test_timeout_leads_to_game_over(self) -> None:
        """The F7 cheat sets the timer to 5 s; running out ends the game."""
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.press(pygame.K_F7)
        self.assertEqual(self.engine.time_left, GameEngine.LOW_TIME_CHEAT)
        self.engine._update_playing(GameEngine.LOW_TIME_CHEAT + 0.1)
        self.assertEqual(
            self.engine.current_state, GameEngine.STATE_GAME_OVER
        )

    def test_extra_life_cheat(self) -> None:
        """F4 adds a life."""
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.press(pygame.K_F4)
        self.assertEqual(self.engine.player.lives, 4)

    def test_power_mode_cheat(self) -> None:
        """F6 makes ghosts edible without a super-pacgum."""
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.press(pygame.K_F6)
        self.assertTrue(all(g.is_edible for g in self.engine.ghosts))

    def test_speed_cheat_halves_step_interval(self) -> None:
        """F5 makes the player take steps twice as often."""
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.engine.player = Player(1, 1, 3)
        self.engine.maze = MazeState([
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ])
        self.press(pygame.K_F5)
        self.assertIn("F5 speed", self.engine.cheat_manager.active_labels())
        self.press(pygame.K_RIGHT)  # Immediate first step.
        self.engine._update_player_movement(GameEngine.PLAYER_MOVE_INTERVAL)
        self.assertEqual(self.engine.player.c, 4)


if __name__ == "__main__":
    unittest.main()
