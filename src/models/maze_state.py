from collections import deque
from typing import List, Tuple

MazeGrid = List[List[int]]


class MazeState:
    """
    Represents the internal state of the current level's maze.
    Tracks remaining collectables and handles wall collision logic.
    """
    CORRIDOR = 0
    WALL = 1
    PACGUM = 2
    SUPER_PACGUM = 3

    def __init__(self, grid: MazeGrid) -> None:
        """Initializes the maze state from a parsed grid."""
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

        # Count total collectables to track level completion condition
        self.remaining_collectables: int = sum(
            row.count(self.PACGUM) + row.count(self.SUPER_PACGUM)
            for row in grid
        )

    def is_wall(self, r: int, c: int) -> bool:
        """Checks if a given coordinate is a wall or out of bounds."""
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.grid[r][c] == self.WALL
        return True

    def open_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Return the directions (dr, dc) that lead to a non-wall tile."""
        return [
            (dr, dc)
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if not self.is_wall(r + dr, c + dc)
        ]

    def distances_from(self, r: int, c: int) -> dict[Tuple[int, int], int]:
        """Walking distance (in tiles) from (r, c) to every reachable tile.

        A breadth-first search, so ghosts follow corridors instead of
        trying to go straight through walls.
        """
        if self.is_wall(r, c):
            return {}
        distances = {(r, c): 0}
        queue = deque([(r, c)])
        while queue:
            cr, cc = queue.popleft()
            for dr, dc in self.open_moves(cr, cc):
                nxt = (cr + dr, cc + dc)
                if nxt not in distances:
                    distances[nxt] = distances[(cr, cc)] + 1
                    queue.append(nxt)
        return distances

    def consume_item(self, r: int, c: int) -> int:
        """
        Eats a Pacgum or Super-pacgum at the given coordinates
        if one exists.
        Returns the type of item consumed (PACGUM, SUPER_PACGUM,
        or CORRIDOR if empty).
        """
        if 0 <= r < self.height and 0 <= c < self.width:
            item = self.grid[r][c]
            if item in (self.PACGUM, self.SUPER_PACGUM):
                self.grid[r][c] = self.CORRIDOR
                self.remaining_collectables -= 1
                return item
        return self.CORRIDOR

    def is_completed(self) -> bool:
        """Returns True if all Pacgums and Super-pacgums have been eaten"""
        return self.remaining_collectables <= 0
