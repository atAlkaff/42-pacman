"""Test maze generation with the assigned package for many sizes."""

import unittest

from models.maze_state import MazeState
from utils.maze_adapter import MazeAdapter


class MazeAdapterSizeTests(unittest.TestCase):
    """Every size a reviewer may configure must give a playable maze."""

    SIZES = (
        (3, 3), (4, 4), (5, 5), (10, 8), (8, 10), (20, 20), (21, 21),
        (22, 15), (40, 12), (12, 40), (50, 50),
    )

    def check(self, width: int, height: int, seed: int) -> None:
        """Generate one maze and check spawn, corners, and pellets."""
        adapter = MazeAdapter(width, height)
        grid = adapter.generate_maze(seed=seed)
        maze = MazeState(grid)
        self.assertEqual((maze.height, maze.width),
                         (2 * height + 1, 2 * width + 1))

        spawn_r, spawn_c = adapter.spawn
        self.assertFalse(maze.is_wall(spawn_r, spawn_c))
        self.assertEqual(grid[spawn_r][spawn_c], MazeState.CORRIDOR)

        reachable = maze.distances_from(spawn_r, spawn_c)
        corners = (
            (1, 1), (1, maze.width - 2),
            (maze.height - 2, 1), (maze.height - 2, maze.width - 2),
        )
        for corner in corners:
            self.assertIn(corner, reachable)
            self.assertEqual(grid[corner[0]][corner[1]],
                             MazeState.SUPER_PACGUM)
        # Every pellet can be eaten, so every level can be finished.
        for r in range(maze.height):
            for c in range(maze.width):
                if grid[r][c] in (MazeState.PACGUM, MazeState.SUPER_PACGUM):
                    self.assertIn((r, c), reachable)

    def test_fixed_seed_sizes(self) -> None:
        """Odd, even, tiny, and non-square sizes with the level-1 seed."""
        for width, height in self.SIZES:
            with self.subTest(width=width, height=height):
                self.check(width, height, seed=42)

    def test_random_sizes(self) -> None:
        """The same sizes with random mazes (as levels 2+ use)."""
        for width, height in self.SIZES:
            for _ in range(3):
                with self.subTest(width=width, height=height):
                    self.check(width, height, seed=0)

    def test_spawn_is_middle_for_odd_sizes(self) -> None:
        """For odd sizes the spawn stays exactly in the middle."""
        adapter = MazeAdapter(21, 21)
        grid = adapter.generate_maze(seed=42)
        self.assertEqual(adapter.spawn, (len(grid) // 2, len(grid[0]) // 2))


if __name__ == "__main__":
    unittest.main()
