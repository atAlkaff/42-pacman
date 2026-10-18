import logging
from typing import Any, List

# Type alias for a 2D grid
MazeGrid = List[List[int]]


class MazeAdapter:
    """
    Adapter for the external 'A-Maze-ing' package.
    Translates the external maze generation into our internal MazeGrid format.
    Handles any external crashes or missing dependencies gracefully
    to avoid tracebacks.
    """

    # Internal representation constants
    CORRIDOR = 0
    WALL = 1
    PACGUM = 2
    SUPER_PACGUM = 3

    def __init__(self, width: int = 21, height: int = 21) -> None:
        self.width = width
        self.height = height

    def generate_maze(self, seed: int) -> MazeGrid:
        """
        Attempts to generate a maze using the external package.
        Falls back to a hardcoded maze on failure.
        """
        try:
            # Dynamically import to prevent crashes if the package is
            # missing during review
            import a_maze_ing  # type: ignore

            # The subject specifies PERFECT=False for Pac-Man-compatible
            # corridors and passing a seed for reproducible generation.
            external_maze = a_maze_ing.generate(
                width=self.width,
                height=self.height,
                perfect=False,
                seed=seed
            )
            return self._translate_maze(external_maze)

        except Exception as e:
            logging.error(f"External A-Maze-ing package failed: {e}."
                          f" Loading fallback maze.")
            return self._get_fallback_maze()

    def _translate_maze(self, external_maze: List[List[int]]) -> MazeGrid:
        """
        Translates the external package's grid to our internal format.
        Assuming external_maze is a 2D list where 1 is wall, 0 is path.
        """
        # Translation logic mapping external constants to internal ones.
        # This decouples our engine from their specific implementation.
        grid: MazeGrid = []
        for row in external_maze:
            translated_row = []
            for cell in row:
                if cell == 1:
                    translated_row.append(self.WALL)
                else:
                    # Initially fill all valid corridors with Pacgums
                    translated_row.append(self.PACGUM)
            grid.append(translated_row)

        # Place Super-pacgums in the 4 corners of the maze
        self._place_super_pacgums(grid)

        # Clear the center tile for player spawn
        self._clear_spawn_point(grid)

        return grid

    def _place_super_pacgums(self, grid: MazeGrid) -> None:
        """
        Replaces standard Pacgums with Super-pacgums in the 4 corners.
        """
        corners = [
            (1, 1),
            (1, self.width - 2),
            (self.height - 2, 1),
            (self.height - 2, self.width - 2)
        ]

        for r, c in corners:
            if 0 <= r < self.height and 0 <= c < self.width:
                if grid[r][c] != self.WALL:
                    grid[r][c] = self.SUPER_PACGUM

    def _clear_spawn_point(self, grid: MazeGrid) -> None:
        """
        Clears the center of the maze for the player to spawn
        without eating instantly.
        """
        center_r, center_c = self.height // 2, self.width // 2
        if grid[center_r][center_c] != self.WALL:
            grid[center_r][center_c] = self.CORRIDOR

    def _get_fallback_maze(self) -> MazeGrid:
        """
        Provides a hardcoded, valid border maze if the external
        generator fails.
        """
        grid = [
            [
                self.PACGUM for _ in range(self.width)
            ] for _ in range(self.height)
        ]

        # Build border walls
        for i in range(self.width):
            grid[0][i] = self.WALL
            grid[self.height - 1][i] = self.WALL
        for i in range(self.height):
            grid[i][0] = self.WALL
            grid[i][self.width - 1] = self.WALL

        self._place_super_pacgums(grid)
        self._clear_spawn_point(grid)

        return grid
