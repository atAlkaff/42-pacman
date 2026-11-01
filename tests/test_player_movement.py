"""Unit tests for Pac-Man player movement (no game window needed)."""

import unittest

import pygame

from controllers.game_engine import GameEngine
from models.entities import Player
from models.maze_state import MazeState
from utils.config_parser import GameConfig
from utils.maze_adapter import MazeAdapter


class PlayerMovementTests(unittest.TestCase):
    """Verify keyboard input, walls, repeated movement, and pause."""

    def setUp(self) -> None:
        """Construct a small deterministic grid without opening a window."""
        # Fake only the rendering setup; movement uses the real models.
        self.engine = GameEngine.__new__(GameEngine)
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.player = Player(3, 3, 3)
        self.engine.player = self.player
        self.maze = MazeState([
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ])
        self.engine.maze = self.maze
        self.engine.config = GameConfig()
        self.engine.ghosts = []
        self.engine._held_move_keys = []
        self.engine._move_elapsed = 0.0
        self.engine.time_left = 90.0
        self.engine.level = 1

    def press(self, key: int) -> None:
        """Simulate a keyboard key press."""
        self.engine._handle_input(pygame.event.Event(pygame.KEYDOWN, key=key))

    def release(self, key: int) -> None:
        """Simulate a keyboard key release."""
        self.engine._handle_input(pygame.event.Event(pygame.KEYUP, key=key))

    def test_arrow_key_moves_one_tile(self) -> None:
        """Pressing Right should move once into an open corridor."""
        self.press(pygame.K_RIGHT)
        self.assertEqual((self.player.r, self.player.c), (3, 4))

    def test_wasd_moves_one_tile(self) -> None:
        """WASD should work as an alternative to arrow keys."""
        self.press(pygame.K_w)
        self.assertEqual((self.player.r, self.player.c), (2, 3))

    def test_wall_blocks_player(self) -> None:
        """Movement must not cross a wall or leave the maze."""
        self.player.r = 3
        self.player.c = 5
        self.press(pygame.K_RIGHT)
        self.assertEqual((self.player.r, self.player.c), (3, 5))

    def test_holding_moves_then_releasing_stops(self) -> None:
        """Holding a direction repeats movement at the configured interval."""
        self.press(pygame.K_RIGHT)
        self.engine._update_player_movement(GameEngine.PLAYER_MOVE_INTERVAL)
        self.assertEqual((self.player.r, self.player.c), (3, 5))
        self.release(pygame.K_RIGHT)
        self.engine._update_player_movement(1.0)
        self.assertEqual((self.player.r, self.player.c), (3, 5))

    def test_pause_disables_movement(self) -> None:
        """Keys cannot move Pac-Man while the game is paused."""
        self.press(pygame.K_ESCAPE)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_PAUSED)
        self.press(pygame.K_LEFT)
        self.assertEqual((self.player.r, self.player.c), (3, 3))
        self.press(pygame.K_ESCAPE)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_PLAYING)

    def test_real_generated_maze_allows_a_valid_move(self) -> None:
        """Check movement in a generated maze from the assigned backend."""
        grid = MazeAdapter().generate_maze(seed=42)
        self.maze = MazeState(grid)
        self.engine.maze = self.maze
        center = (len(grid) // 2, len(grid[0]) // 2)
        self.player.r, self.player.c = center
        directions = (
            (pygame.K_UP, -1, 0),
            (pygame.K_DOWN, 1, 0),
            (pygame.K_LEFT, 0, -1),
            (pygame.K_RIGHT, 0, 1),
        )
        key, dr, dc = next(
            (key, dr, dc) for key, dr, dc in directions
            if not self.maze.is_wall(center[0] + dr, center[1] + dc)
        )
        self.press(key)
        self.assertEqual(
            (self.player.r, self.player.c),
            (center[0] + dr, center[1] + dc),
        )

    def test_releasing_last_key_restores_previous_direction(self) -> None:
        """The previous held direction becomes active after releasing a key."""
        self.press(pygame.K_RIGHT)
        self.press(pygame.K_UP)  # A wall is at row 2, column 4.
        self.assertEqual((self.player.r, self.player.c), (3, 4))
        self.release(pygame.K_UP)
        self.engine._update_player_movement(GameEngine.PLAYER_MOVE_INTERVAL)
        self.assertEqual((self.player.r, self.player.c), (3, 5))


if __name__ == "__main__":
    unittest.main()
