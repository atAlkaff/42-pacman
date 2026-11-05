import random
from typing import Tuple

Move = Tuple[int, int]


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

    A ghost chases the player while dangerous, flees while edible, and
    waits in its corner for a while after being eaten.
    """

    # Distance used for tiles the player cannot reach.
    UNREACHABLE = 10 ** 9

    def __init__(
        self, start_r: int, start_c: int, chase_chance: float = 1.0
    ) -> None:
        """Create a ghost at its corner.

        Args:
            start_r: Spawn row.
            start_c: Spawn column.
            chase_chance: Probability (0..1) of taking the smartest move at
                each step. The remaining steps are random, which gives every
                ghost its own personality.
        """
        super().__init__(start_r, start_c)
        self.chase_chance: float = min(1.0, max(0.0, chase_chance))
        self.is_edible: bool = False
        self.edible_timer: float = 0.0
        self.is_eaten: bool = False
        self.respawn_timer: float = 0.0
        self.move_elapsed: float = 0.0

    def set_edible(self, duration: float) -> None:
        """Makes the ghost edible for a specified duration."""
        if self.is_eaten:
            return
        self.is_edible = True
        self.edible_timer = duration

    def get_eaten(self, respawn_delay: float) -> None:
        """Send the ghost back to its corner and keep it out of play."""
        self.reset_position()
        self.is_edible = False
        self.edible_timer = 0.0
        self.is_eaten = True
        self.respawn_timer = respawn_delay
        self.move_elapsed = 0.0

    def reset(self) -> None:
        """Return to the corner in the normal, dangerous state."""
        self.reset_position()
        self.is_edible = False
        self.edible_timer = 0.0
        self.is_eaten = False
        self.respawn_timer = 0.0
        self.move_elapsed = 0.0

    def update_timer(self, dt: float) -> None:
        """Count down the edible and respawn timers."""
        if self.is_edible:
            self.edible_timer -= dt
            if self.edible_timer <= 0:
                self.is_edible = False
                self.edible_timer = 0.0
        if self.is_eaten:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.is_eaten = False
                self.respawn_timer = 0.0

    def choose_direction(
        self,
        valid_moves: list[Move],
        distances: dict[Move, int],
        rng: random.Random,
    ) -> Move:
        """Pick the next step using distances to the player.

        Ghosts never turn back unless it is the only option, so they keep
        flowing through corridors. With probability ``chase_chance`` the
        ghost takes the move that brings it closest to the player (or, when
        edible, the farthest away); otherwise it picks a random move.

        Args:
            valid_moves: Directions (dr, dc) that do not hit a wall.
            distances: Walking distance from the player to each tile.
            rng: Random generator used for the random moves.

        Returns:
            The chosen (dr, dc), or (0, 0) when the ghost cannot move.
        """
        if not valid_moves:
            return (0, 0)

        reverse = (-self.dr, -self.dc)
        forward = [move for move in valid_moves if move != reverse]
        options = forward or valid_moves

        if rng.random() >= self.chase_chance:
            return rng.choice(options)

        def distance_after(move: Move) -> int:
            target = (self.r + move[0], self.c + move[1])
            return distances.get(target, self.UNREACHABLE)

        if self.is_edible:
            return max(options, key=distance_after)
        return min(options, key=distance_after)
