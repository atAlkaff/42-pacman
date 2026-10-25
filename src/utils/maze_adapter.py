"""Connect an external maze generator to the Pac-Man tile grid."""

from collections import deque
from collections.abc import Callable
from typing import cast

from mazegenerator import MazeGenerator


RawMaze = list[list[int]]
MazeBackend = Callable[[int, int, int], RawMaze]


class MazeAdapter:
    """Translate directional wall masks into playable Pac-Man tiles."""

    CORRIDOR = 0
    WALL = 1
    PACGUM = 2
    SUPER_PACGUM = 3

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    def __init__(
        self,
        width: int = 21,
        height: int = 21,
        backend: MazeBackend | None = None,
    ) -> None:
        """Set source-maze size and optionally a different maze backend."""
        if (
            not isinstance(width, int)
            or isinstance(width, bool)
            or not isinstance(height, int)
            or isinstance(height, bool)
            or width < 3
            or height < 3
        ):
            raise ValueError("Maze width and height must be at least 3")

        self.width = width
        self.height = height
        self.backend = backend or self._default_backend

    @staticmethod
    def _default_backend(width: int, height: int, seed: int) -> RawMaze:
        """Load the team's assigned A-Maze-ing maze package."""
        generator = MazeGenerator(
            size=(width, height),
            perfect=False,
            seed=seed,
        )
        return cast(RawMaze, generator.maze)

    def generate_maze(self, seed: int = 0) -> RawMaze:
        """Return a game grid: 0 empty, 1 wall, 2 dot, 3 power dot."""
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("Maze seed must be an integer")

        try:
            raw = self.backend(self.width, self.height, seed)
        except Exception as exc:
            raise ValueError("External maze generation failed") from exc

        self._validate(raw)
        grid = self._convert(raw)
        center = (len(grid) // 2, len(grid[0]) // 2)
        if grid[center[0]][center[1]] == self.WALL:
            raise ValueError("Center spawn is blocked in this maze")

        reachable = self._reachable(grid, center)
        corners = (
            (1, 1),
            (1, len(grid[0]) - 2),
            (len(grid) - 2, 1),
            (len(grid) - 2, len(grid[0]) - 2),
        )
        if any(corner not in reachable for corner in corners):
            raise ValueError("A ghost corner cannot reach the player")

        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] != self.CORRIDOR:
                    continue
                if (row, col) not in reachable:
                    grid[row][col] = self.WALL
                elif (row, col) != center:
                    grid[row][col] = self.PACGUM

        for row, col in corners:
            grid[row][col] = self.SUPER_PACGUM

        return grid

    def _validate(self, raw: RawMaze) -> None:
        """Check shape, wall masks, and shared wall consistency."""
        if not isinstance(raw, list) or len(raw) != self.height:
            raise ValueError("Invalid maze height")

        for row_data in raw:
            if not isinstance(row_data, list) or len(row_data) != self.width:
                raise ValueError("Invalid maze width or row")
            for value in row_data:
                if (
                    not isinstance(value, int)
                    or isinstance(value, bool)
                    or not 0 <= value <= 15
                ):
                    raise ValueError("Invalid wall mask (expected 0 to 15)")

        for row in range(self.height):
            for col in range(self.width):
                mask = raw[row][col]
                if col + 1 < self.width:
                    east = bool(mask & self.EAST)
                    west = bool(raw[row][col + 1] & self.WEST)
                    if east != west:
                        raise ValueError("Inconsistent east/west walls")
                if row + 1 < self.height:
                    south = bool(mask & self.SOUTH)
                    north = bool(raw[row + 1][col] & self.NORTH)
                    if south != north:
                        raise ValueError("Inconsistent north/south walls")

    def _convert(self, raw: RawMaze) -> RawMaze:
        """Expand each cell into a center tile and wall connectors."""
        rows = self.height * 2 + 1
        cols = self.width * 2 + 1
        result = [[self.WALL] * cols for _ in range(rows)]

        for row in range(self.height):
            for col in range(self.width):
                mask = raw[row][col]
                if mask == 15:
                    continue  # The external generator's isolated '42' cells.

                y = 2 * row + 1
                x = 2 * col + 1
                result[y][x] = self.CORRIDOR

                if col + 1 < self.width and not (mask & self.EAST):
                    result[y][x + 1] = self.CORRIDOR
                if row + 1 < self.height and not (mask & self.SOUTH):
                    result[y + 1][x] = self.CORRIDOR

        return result

    @staticmethod
    def _reachable(
        grid: RawMaze, start: tuple[int, int]
    ) -> set[tuple[int, int]]:
        """Find traversable squares connected to the player spawn."""
        seen = {start}
        queue = deque([start])
        while queue:
            row, col = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = row + dr, col + dc
                if (
                    0 <= nr < len(grid)
                    and 0 <= nc < len(grid[0])
                    and grid[nr][nc] != MazeAdapter.WALL
                    and (nr, nc) not in seen
                ):
                    seen.add((nr, nc))
                    queue.append((nr, nc))
        return seen
