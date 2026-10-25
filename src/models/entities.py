import math
from typing import Tuple


class Entity:
    """Base class for all moving characters in the game."""
    def __init__(self, start_r: int, start_c: int) -> None:
        self.start_r: int = start_r
        self.start_c: int = start_c
        self.r: int = start_r
        self.c: int = start_c
        self.dr: int = 0
        self.dc: int = 0

    def reset_position(self) -> None:
        """Returns the entity to its original spawn point."""
        self.r = self.start_r
        self.c = self.start_c
        self.dr = 0
        self.dc = 0


class Player(Entity):
    """
    The main player character.
    Tracks remaining lives, total score, and grid coordinates.
    """
    def __init__(self, start_r: int, start_c: int, initial_lives: int) -> None:
        super().__init__(start_r, start_c)
        self.lives: int = initial_lives
        self.score: int = 0

    def lose_life(self) -> None:
        """Decrements a life when touched by a non-edible ghost."""
        if self.lives > 0:
            self.lives -= 1


class Ghost(Entity):
    """
    Autonomous enemy entity.
    Can switch between chasing the player and fleeing when edible.
    """
    def __init__(self, start_r: int, start_c: int) -> None:
        super().__init__(start_r, start_c)
        self.is_edible: bool = False
        self.edible_timer: float = 0.0

    def set_edible(self, duration: float) -> None:
        """Makes the ghost edible for a specified duration."""
        self.is_edible = True
        self.edible_timer = duration

    def update_timer(self, dt: float) -> None:
        """Decrements the edible timer and reverts state if time expires."""
        if self.is_edible:
            self.edible_timer -= dt
            if self.edible_timer <= 0:
                self.is_edible = False
                self.edible_timer = 0.0

    def get_next_move(
        self,
        target_r: int,
        target_c: int,
        valid_moves: list[Tuple[int, int]]
    ) -> Tuple[int, int]:
        """
        Determines the next move based on distance to the target.
        If edible, the target should be a point far away from the player.
        """
        if not valid_moves:
            return (0, 0)

        best_move = valid_moves[0]
        min_dist = float('inf')

        for move_dr, move_dc in valid_moves:
            next_r = self.r + move_dr
            next_c = self.c + move_dc
            # Euclidean distance to determine closest tile to target
            dist = math.hypot(target_r - next_r, target_c - next_c)

            if dist < min_dist:
                min_dist = dist
                best_move = (move_dr, move_dc)

        return best_move
