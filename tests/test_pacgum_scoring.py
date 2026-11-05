"""Test Pacgum collection, scoring, and temporary power mode."""

import random
import unittest
from unittest.mock import patch

import pygame

from controllers.cheat_manager import CheatManager
from controllers.game_engine import GameEngine
from models.entities import Ghost, Player
from models.maze_state import MazeState
from utils.config_parser import GameConfig


class PacgumScoringTests(unittest.TestCase):
    """Exercise real game models without opening a graphics window."""

    @property
    def player(self) -> Player:
        """The engine's player (always set in these tests)."""
        assert self.engine.player is not None
        return self.engine.player

    @property
    def maze(self) -> MazeState:
        """The engine's maze (always set in these tests)."""
        assert self.engine.maze is not None
        return self.engine.maze

    def setUp(self) -> None:
        """Make a small level with one dot and one power pellet."""
        self.engine = GameEngine.__new__(GameEngine)
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.engine.config = GameConfig(
            points_per_pacgum=13,
            points_per_super_pacgum=61,
        )
        self.engine.player = Player(2, 2, 3)
        self.engine.maze = MazeState([
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 2, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ])
        self.engine.ghosts = [Ghost(1, 1), Ghost(3, 5)]
        self.engine._held_move_keys = []
        self.engine._move_elapsed = 0.0
        self.engine._respawn_pause = 0.0
        self.engine._rng = random.Random(0)
        self.engine.cheat_manager = CheatManager()
        self.engine.time_left = 90.0
        self.engine.level = 1

    def press(self, key: int) -> None:
        """Press a movement key through the real game controller."""
        self.engine._handle_input(pygame.event.Event(pygame.KEYDOWN, key=key))

    def release(self, key: int) -> None:
        """Release a movement key through the real game controller."""
        self.engine._handle_input(pygame.event.Event(pygame.KEYUP, key=key))

    def test_small_pacgum_increases_score_and_disappears(self) -> None:
        """A small dot gives the configured points once."""
        self.press(pygame.K_UP)
        self.assertEqual((self.player.r, self.player.c), (1, 2))
        self.assertEqual(self.player.score, 13)
        self.assertEqual(self.maze.grid[1][2], MazeState.CORRIDOR)
        self.assertEqual(self.maze.remaining_collectables, 1)

    def test_wasd_collects_pacgum(self) -> None:
        """A movement key from WASD triggers the same collection."""
        self.press(pygame.K_w)
        self.assertEqual(self.player.score, 13)

    def test_empty_tile_does_not_increase_score(self) -> None:
        """Moving onto an empty corridor never changes the score."""
        self.press(pygame.K_RIGHT)
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.maze.remaining_collectables, 2)

    def test_collecting_twice_does_not_duplicate_score(self) -> None:
        """Returning to an already eaten dot cannot award it again."""
        self.press(pygame.K_UP)
        self.release(pygame.K_UP)
        self.press(pygame.K_DOWN)
        self.release(pygame.K_DOWN)
        self.press(pygame.K_UP)
        self.assertEqual(self.player.score, 13)
        self.assertEqual(self.maze.remaining_collectables, 1)

    def test_power_pacgum_scores_and_makes_ghosts_edible(self) -> None:
        """A power pellet awards points and activates ghost power mode."""
        self.press(pygame.K_RIGHT)
        self.release(pygame.K_RIGHT)
        self.press(pygame.K_RIGHT)
        self.release(pygame.K_RIGHT)
        self.press(pygame.K_UP)
        self.assertEqual((self.player.r, self.player.c), (1, 4))
        self.assertEqual(self.player.score, 61)
        self.assertEqual(self.maze.grid[1][4], MazeState.CORRIDOR)
        self.assertEqual(self.maze.remaining_collectables, 1)
        for ghost in self.engine.ghosts:
            self.assertTrue(ghost.is_edible)
            self.assertEqual(
                ghost.edible_timer, GameEngine.POWER_MODE_DURATION
            )

    def test_power_mode_expires_during_game_updates(self) -> None:
        """Power mode ends after its short countdown."""
        self.test_power_pacgum_scores_and_makes_ghosts_edible()
        self.engine._held_move_keys.clear()
        self.engine._update_playing(GameEngine.POWER_MODE_DURATION + 0.1)
        for ghost in self.engine.ghosts:
            self.assertFalse(ghost.is_edible)

    def test_wall_blocks_item_collection(self) -> None:
        """A blocked movement does not collect nearby items."""
        self.player.r, self.player.c = 1, 2
        self.press(pygame.K_UP)
        self.assertEqual((self.player.r, self.player.c), (1, 2))
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.maze.remaining_collectables, 2)

    def test_last_pacgum_triggers_level_completion(self) -> None:
        """Finishing the final dot invokes existing level progression."""
        self.engine.maze = MazeState([
            [1, 1, 1, 1],
            [1, 0, 2, 1],
            [1, 1, 1, 1],
        ])
        self.player.r = 1
        self.player.c = 1
        self.press(pygame.K_RIGHT)
        self.assertTrue(self.maze.is_completed())
        with patch.object(self.engine, "_advance_level") as advance:
            self.engine._update_playing(0.01)
            advance.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
