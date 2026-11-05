"""Test ghost AI, ghost/player collisions, and life loss."""

import random
import unittest

import pygame

from controllers.cheat_manager import CheatManager
from controllers.game_engine import GameEngine
from models.entities import Ghost, Player
from models.maze_state import MazeState
from utils.config_parser import GameConfig


# A ring corridor around a solid block, with one long straight row.
GRID = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]


class GhostTests(unittest.TestCase):
    """Exercise ghosts on a small hand-made maze without a window."""

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
        """Build an engine with one player and one ghost."""
        self.engine = GameEngine.__new__(GameEngine)
        self.engine.current_state = GameEngine.STATE_PLAYING
        self.engine.config = GameConfig(lives=3, points_per_ghost=200)
        self.engine.maze = MazeState([row[:] for row in GRID])
        self.engine.player = Player(3, 3, 3)
        self.ghost = Ghost(1, 1)
        self.engine.ghosts = [self.ghost]
        self.engine._held_move_keys = []
        self.engine._move_elapsed = 0.0
        self.engine._respawn_pause = 0.0
        self.engine._rng = random.Random(0)
        self.engine.cheat_manager = CheatManager()
        self.engine.time_left = 90.0
        self.engine.level = 1

    def step_ghosts(self) -> None:
        """Advance exactly one ghost step."""
        self.engine._update_ghosts(GameEngine.GHOST_MOVE_INTERVAL)

    def test_distances_follow_corridors(self) -> None:
        """Walking distance goes around walls, not through them."""
        distances = self.maze.distances_from(3, 3)
        self.assertEqual(distances[(3, 3)], 0)
        self.assertEqual(distances[(1, 3)], 6)
        self.assertNotIn((2, 3), distances)  # A wall tile.

    def test_ghost_moves_toward_player(self) -> None:
        """A full-chase ghost reduces its walking distance every step."""
        distances = self.maze.distances_from(3, 3)
        before = distances[(self.ghost.r, self.ghost.c)]
        self.step_ghosts()
        after = distances[(self.ghost.r, self.ghost.c)]
        self.assertEqual(after, before - 1)

    def test_ghost_never_enters_walls(self) -> None:
        """Random ghosts only ever stand on corridor tiles."""
        self.ghost.chase_chance = 0.0
        self.player.r, self.player.c = 1, 5
        self.engine.cheat_manager.invincibility_active = True
        for _ in range(200):
            self.step_ghosts()
            self.assertFalse(
                self.maze.is_wall(self.ghost.r, self.ghost.c)
            )

    def test_edible_ghost_moves_away(self) -> None:
        """An edible ghost increases its distance from the player."""
        self.ghost.r, self.ghost.c = 3, 1
        self.ghost.set_edible(5.0)
        distances = self.maze.distances_from(3, 3)
        self.engine._update_ghosts(GameEngine.GHOST_MOVE_INTERVAL)
        self.assertEqual((self.ghost.r, self.ghost.c), (3, 1))  # Slower.
        self.engine._update_ghosts(GameEngine.GHOST_EDIBLE_MOVE_INTERVAL)
        self.assertEqual(distances[(self.ghost.r, self.ghost.c)], 3)

    def test_ghost_catching_player_costs_a_life(self) -> None:
        """Contact loses a life and sends everyone back to spawn."""
        self.player.r, self.player.c = 1, 2
        self.step_ghosts()
        self.assertEqual(self.player.lives, 2)
        self.assertEqual(
            (self.player.r, self.player.c), (3, 3)
        )
        self.assertEqual((self.ghost.r, self.ghost.c), (1, 1))
        self.assertGreater(self.engine._respawn_pause, 0)
        self.assertEqual(self.engine.current_state, GameEngine.STATE_PLAYING)

    def test_player_walking_into_ghost_costs_a_life(self) -> None:
        """Moving onto a ghost is a collision too."""
        self.player.r, self.player.c = 1, 2
        self.engine._handle_input(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        )
        self.assertEqual(self.player.lives, 2)

    def test_last_life_ends_the_game(self) -> None:
        """Losing the final life switches to the game-over screen."""
        self.player.lives = 1
        self.player.r, self.player.c = 1, 2
        self.step_ghosts()
        self.assertEqual(self.player.lives, 0)
        self.assertEqual(
            self.engine.current_state, GameEngine.STATE_GAME_OVER
        )

    def test_respawn_pause_freezes_play(self) -> None:
        """Nothing moves and the timer stops during the READY pause."""
        self.engine._respawn_pause = 1.0
        self.engine._update_playing(0.5)
        self.assertEqual((self.ghost.r, self.ghost.c), (1, 1))
        self.assertEqual(self.engine.time_left, 90.0)
        self.engine._update_playing(0.6)
        self.assertEqual(self.engine._respawn_pause, 0.0)

    def test_invincibility_prevents_life_loss(self) -> None:
        """With the F1 cheat on, ghosts cannot hurt the player."""
        self.engine.cheat_manager.invincibility_active = True
        self.player.r, self.player.c = 1, 2
        self.step_ghosts()
        self.assertEqual(self.player.lives, 3)

    def test_eating_edible_ghost_scores_and_respawns_later(self) -> None:
        """An eaten ghost scores, leaves play, then returns to its corner."""
        self.ghost.r, self.ghost.c = 3, 4
        self.ghost.set_edible(5.0)
        self.engine._handle_input(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        )
        self.assertEqual(self.player.score, 200)
        self.assertEqual(self.player.lives, 3)
        self.assertTrue(self.ghost.is_eaten)
        self.assertEqual((self.ghost.r, self.ghost.c), (1, 1))

        # An eaten ghost neither moves nor collides.
        self.step_ghosts()
        self.assertEqual((self.ghost.r, self.ghost.c), (1, 1))

        self.ghost.update_timer(GameEngine.GHOST_RESPAWN_DELAY + 0.1)
        self.assertFalse(self.ghost.is_eaten)
        self.assertFalse(self.ghost.is_edible)

    def test_freeze_cheat_stops_ghosts(self) -> None:
        """F3 toggles the ghost freeze cheat."""
        self.engine._handle_input(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F3)
        )
        self.step_ghosts()
        self.assertEqual((self.ghost.r, self.ghost.c), (1, 1))


if __name__ == "__main__":
    unittest.main()
