"""Coordinate Pac-Man game states, levels, and rendering."""

import logging
import random
from typing import List

import pygame

from controllers.cheat_manager import CheatManager
from models.entities import Ghost, Player
from models.maze_state import MazeState
from utils.config_parser import GameConfig
from utils.maze_adapter import MazeAdapter
from views.hud import HUD
from views.pygame_renderer import PygameRenderer


class GameEngine:
    """Control the game loop and move between configured levels."""

    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    STATE_GAME_OVER = 3
    STATE_VICTORY = 4

    # Seconds between grid steps. Ghosts are a little slower than the
    # player, and slower still while edible, so they can be caught.
    PLAYER_MOVE_INTERVAL = 0.12
    GHOST_MOVE_INTERVAL = 0.16
    GHOST_EDIBLE_MOVE_INTERVAL = 0.28
    POWER_MODE_DURATION = 6.0
    GHOST_RESPAWN_DELAY = 5.0
    # Short "READY!" pause after losing a life.
    RESPAWN_PAUSE = 1.5
    # How often each ghost takes the smartest move (one per corner).
    # 1.0 always chases; lower values wander more.
    GHOST_CHASE_CHANCES = (1.0, 0.85, 0.7, 0.5)
    # Random mazes that fail validation are regenerated this many times.
    MAZE_ATTEMPTS = 5
    MOVE_KEYS: dict[int, tuple[int, int]] = {
        pygame.K_UP: (-1, 0),
        pygame.K_w: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_s: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_a: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_d: (0, 1),
    }

    def __init__(
        self,
        config: GameConfig,
        renderer: PygameRenderer,
        adapter: MazeAdapter,
    ) -> None:
        """Initialize game state without starting the game loop."""
        self.config = config
        self.renderer = renderer
        self.adapter = adapter
        self.hud = HUD(
            renderer.screen,
            renderer.height - renderer.HUD_HEIGHT,
            renderer.width,
        )
        self.cheat_manager = CheatManager()

        self.current_state = self.STATE_MENU
        self.level = 1
        self.time_left = float(config.level_max_time)
        self.clock = pygame.time.Clock()

        self.player: Player | None = None
        self.ghosts: List[Ghost] = []
        self.maze: MazeState | None = None

        # Pressing a direction moves once immediately. Holding it
        # repeats moves at a frame-rate-independent interval.
        self._held_move_keys: list[int] = []
        self._move_elapsed = 0.0

        # Ghost decisions use their own generator: the maze package reseeds
        # the global random module whenever a maze is generated.
        self._rng = random.Random()
        self._respawn_pause = 0.0

    def _init_level(self) -> None:
        """Initialize a configured level, preserving score and lives."""
        if not 1 <= self.level <= len(self.config.level):
            raise ValueError(f"Level {self.level} is not configured")

        level_settings = self.config.level[self.level - 1]
        seed = self.config.seed if self.level == 1 else 0

        # Keep the originally supplied generator backend, but use this
        # level's dimensions instead of fixed dimensions from level 1.
        self.adapter = MazeAdapter(
            width=level_settings.width,
            height=level_settings.height,
            backend=self.adapter.backend,
        )
        grid = self._generate_grid(seed)
        self.maze = MazeState(grid)

        # Resize for the new maze and bind the HUD to the new surface.
        self._refresh_level_display()

        current_score = self.player.score if self.player else 0
        current_lives = self.player.lives if self.player else self.config.lives

        center_r = self.maze.height // 2
        center_c = self.maze.width // 2
        self.player = Player(center_r, center_c, current_lives)
        self.player.score = current_score

        corners = (
            (1, 1),
            (1, self.maze.width - 2),
            (self.maze.height - 2, 1),
            (self.maze.height - 2, self.maze.width - 2),
        )
        self.ghosts = [
            Ghost(r, c, chance)
            for (r, c), chance in zip(corners, self.GHOST_CHASE_CHANCES)
        ]
        self._respawn_pause = 0.0
        self.time_left = float(
            level_settings.time_limit
            if level_settings.time_limit is not None
            else self.config.level_max_time
        )
        self._held_move_keys.clear()
        self._move_elapsed = 0.0

    def _generate_grid(self, seed: int) -> list[list[int]]:
        """Generate a level grid, retrying random mazes that are unusable.

        A fixed seed always yields the same maze, so it is tried once.

        Raises:
            ValueError: If no playable maze could be generated.
        """
        attempts = 1 if seed != 0 else self.MAZE_ATTEMPTS
        last_error: ValueError | None = None
        for attempt in range(1, attempts + 1):
            try:
                return self.adapter.generate_maze(seed=seed)
            except ValueError as exc:
                last_error = exc
                logging.warning(
                    "Maze generation attempt %d failed: %s", attempt, exc
                )
        raise ValueError(
            f"Could not generate a playable maze for level {self.level}: "
            f"{last_error}"
        )

    def _refresh_level_display(self) -> None:
        """Resize once per level and refresh the HUD display surface."""
        if self.maze is None:
            return

        self.renderer.resize_grid(self.maze.width, self.maze.height)
        self.hud = HUD(
            self.renderer.screen,
            self.renderer.height - self.renderer.HUD_HEIGHT,
            self.renderer.width,
        )

    def _advance_level(self) -> None:
        """Move to the next configured level or stop at victory."""
        if self.level >= len(self.config.level):
            self.current_state = self.STATE_VICTORY
            return

        self.level += 1
        self._init_level()

    def _draw_play_field(self) -> None:
        """Draw the current level when player and maze are initialized."""
        if self.maze is None or self.player is None:
            return

        self.renderer.draw_maze(self.maze)
        self.renderer.draw_entities(self.player, self.ghosts)
        cheats = []
        if self.cheat_manager.invincibility_active:
            cheats.append("F1 invincible")
        if self.cheat_manager.ghosts_frozen:
            cheats.append("F3 ghosts frozen")
        self.hud.draw(
            self.player.score,
            self.player.lives,
            self.level,
            max(0, int(self.time_left)),
            "  ".join(cheats),
        )

    def run(self) -> None:
        """Process events, update the game, and render each frame."""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._handle_input(event)

            if not running:
                break

            if self.current_state == self.STATE_PLAYING:
                self._update_playing(dt)

            self.renderer.clear_screen()

            if self.current_state == self.STATE_PLAYING:
                self._draw_play_field()
                if self._respawn_pause > 0 and self.player is not None:
                    self.renderer.draw_centered_message(
                        "READY!", f"Lives left: {self.player.lives}"
                    )
            elif self.current_state == self.STATE_PAUSED:
                self._draw_play_field()
                self.renderer.draw_centered_message(
                    "PAUSED", "Press ESC to resume"
                )
            elif self.current_state == self.STATE_MENU:
                self.renderer.draw_centered_message(
                    "PAC-MAN", "Press SPACE to start"
                )
            elif self.current_state == self.STATE_GAME_OVER:
                self.renderer.draw_centered_message(
                    "GAME OVER", "Press SPACE for menu"
                )
            elif self.current_state == self.STATE_VICTORY:
                self.renderer.draw_centered_message(
                    "VICTORY!", "Press SPACE for menu"
                )

            self.renderer.update_display()

        pygame.quit()

    def _handle_input(self, event: pygame.event.Event) -> None:
        """Handle game controls, including arrow keys and WASD."""
        if event.type == pygame.KEYUP:
            # Release a held direction so Pac-Man stops moving.
            if event.key in self._held_move_keys:
                self._held_move_keys.remove(event.key)
            if not self._held_move_keys:
                self._move_elapsed = 0.0
            return

        if event.type != pygame.KEYDOWN:
            return

        if self.current_state == self.STATE_MENU:
            if event.key == pygame.K_SPACE:
                self.level = 1
                self.player = None  # A new game resets score and lives.
                self._init_level()
                self.current_state = self.STATE_PLAYING
        elif self.current_state == self.STATE_PLAYING:
            if event.key == pygame.K_ESCAPE:
                self.current_state = self.STATE_PAUSED
                self._held_move_keys.clear()
                self._move_elapsed = 0.0
            elif event.key == pygame.K_F1:
                self.cheat_manager.toggle_invincibility()
            elif event.key == pygame.K_F2:
                self._advance_level()
            elif event.key == pygame.K_F3:
                self.cheat_manager.toggle_ghost_freeze()
            elif event.key in self.MOVE_KEYS:
                if event.key not in self._held_move_keys:
                    self._held_move_keys.append(event.key)
                    self._move_player_one_tile()
                    self._move_elapsed = 0.0
        elif self.current_state == self.STATE_PAUSED:
            if event.key == pygame.K_ESCAPE:
                self.current_state = self.STATE_PLAYING
        elif self.current_state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
            if event.key == pygame.K_SPACE:
                self.current_state = self.STATE_MENU

    def _move_player_one_tile(self) -> bool:
        """Move Pac-Man one cell, but never through walls or boundaries."""
        if (
            self.current_state != self.STATE_PLAYING
            or self.player is None
            or self.maze is None
            or not self._held_move_keys
            or self._respawn_pause > 0
        ):
            return False

        direction_key = self._held_move_keys[-1]
        dr, dc = self.MOVE_KEYS[direction_key]
        new_r = self.player.r + dr
        new_c = self.player.c + dc
        if self.maze.is_wall(new_r, new_c):
            return False

        self.player.r = new_r
        self.player.c = new_c
        self.player.dr = dr
        self.player.dc = dc
        self._consume_current_tile()
        self._check_ghost_collisions()
        return True

    def _consume_current_tile(self) -> None:
        """Collect one maze item and update the score only once."""
        if self.player is None or self.maze is None:
            return

        item = self.maze.consume_item(self.player.r, self.player.c)
        if item == MazeState.PACGUM:
            self.player.score += self.config.points_per_pacgum
        elif item == MazeState.SUPER_PACGUM:
            self.player.score += self.config.points_per_super_pacgum
            for ghost in self.ghosts:
                ghost.set_edible(self.POWER_MODE_DURATION)

    def _update_player_movement(self, dt: float) -> None:
        """Repeat movement while a direction key is held."""
        if not self._held_move_keys:
            self._move_elapsed = 0.0
            return

        self._move_elapsed += max(0.0, dt)
        while self._move_elapsed >= self.PLAYER_MOVE_INTERVAL:
            self._move_elapsed -= self.PLAYER_MOVE_INTERVAL
            self._move_player_one_tile()

    def _update_ghosts(self, dt: float) -> None:
        """Move every active ghost one step when its interval has passed."""
        if (
            self.player is None
            or self.maze is None
            or self.cheat_manager.ghosts_frozen
        ):
            return

        distances: dict[tuple[int, int], int] | None = None
        for ghost in self.ghosts:
            if ghost.is_eaten:
                continue
            interval = (
                self.GHOST_EDIBLE_MOVE_INTERVAL
                if ghost.is_edible else self.GHOST_MOVE_INTERVAL
            )
            ghost.move_elapsed += max(0.0, dt)
            if ghost.move_elapsed < interval:
                continue
            # At most one step per frame; drop any leftover lag.
            ghost.move_elapsed = min(ghost.move_elapsed - interval, interval)

            if distances is None:
                # One search from the player serves all ghosts this frame.
                distances = self.maze.distances_from(
                    self.player.r, self.player.c
                )
            dr, dc = ghost.choose_direction(
                self.maze.open_moves(ghost.r, ghost.c), distances, self._rng
            )
            ghost.r += dr
            ghost.c += dc
            ghost.dr, ghost.dc = dr, dc

            self._check_ghost_collisions()
            if self.current_state != self.STATE_PLAYING:
                return
            if self._respawn_pause > 0:
                return  # Positions were reset; skip the rest of this frame.

    def _check_ghost_collisions(self) -> None:
        """Resolve the player sharing a tile with any ghost.

        Moves are made one tile at a time and checked after each step, so a
        player and a ghost can never pass through each other unnoticed.
        """
        if self.player is None or self._respawn_pause > 0:
            return

        for ghost in self.ghosts:
            if ghost.is_eaten:
                continue
            if (ghost.r, ghost.c) != (self.player.r, self.player.c):
                continue
            if ghost.is_edible:
                ghost.get_eaten(self.GHOST_RESPAWN_DELAY)
                self.player.score += self.config.points_per_ghost
            elif not self.cheat_manager.invincibility_active:
                self._lose_life()
                return

    def _lose_life(self) -> None:
        """Remove a life, then respawn everyone or end the game."""
        if self.player is None:
            return

        self.player.lose_life()
        self._held_move_keys.clear()
        self._move_elapsed = 0.0
        if self.player.lives <= 0:
            self.current_state = self.STATE_GAME_OVER
            return

        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset()
        self._respawn_pause = self.RESPAWN_PAUSE

    def _update_playing(self, dt: float) -> None:
        """Advance timers, the player, the ghosts, and win/loss checks."""
        if self.player is None or self.maze is None:
            return

        if self._respawn_pause > 0:
            # Everything waits (including the level timer) after a death.
            self._respawn_pause = max(0.0, self._respawn_pause - dt)
            self._move_elapsed = 0.0
            return

        self.time_left -= dt
        if self.time_left <= 0 or self.player.lives <= 0:
            self.time_left = max(0.0, self.time_left)
            self.current_state = self.STATE_GAME_OVER
            return

        for ghost in self.ghosts:
            ghost.update_timer(dt)

        self._update_player_movement(dt)
        if self.current_state != self.STATE_PLAYING:
            return
        if self.maze.is_completed():
            self._advance_level()
            return

        self._update_ghosts(dt)
