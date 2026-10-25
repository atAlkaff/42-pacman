"""Coordinate Pac-Man game states, levels, and rendering."""

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
        grid = self.adapter.generate_maze(seed=seed)
        self.maze = MazeState(grid)

        # Update the window and refresh HUD references after set_mode().
        self.renderer.resize_grid(self.maze.width, self.maze.height)
        self.hud = HUD(
            self.renderer.screen,
            self.renderer.height - self.renderer.HUD_HEIGHT,
            self.renderer.width,
        )

        current_score = self.player.score if self.player else 0
        current_lives = self.player.lives if self.player else self.config.lives

        center_r = self.maze.height // 2
        center_c = self.maze.width // 2
        self.player = Player(center_r, center_c, current_lives)
        self.player.score = current_score

        self.ghosts = [
            Ghost(1, 1),
            Ghost(1, self.maze.width - 2),
            Ghost(self.maze.height - 2, 1),
            Ghost(self.maze.height - 2, self.maze.width - 2),
        ]
        self.time_left = float(self.config.level_max_time)

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
        self.hud.draw(
            self.player.score,
            self.player.lives,
            self.level,
            max(0, int(self.time_left)),
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
        """Handle menu, pause, and evaluation shortcut keys."""
        if event.type != pygame.KEYDOWN:
            return

        if self.current_state == self.STATE_MENU:
            if event.key == pygame.K_SPACE:
                self.level = 1
                self.player = None  # New game starts with fresh score/lives.
                self._init_level()
                self.current_state = self.STATE_PLAYING
        elif self.current_state == self.STATE_PLAYING:
            if event.key == pygame.K_ESCAPE:
                self.current_state = self.STATE_PAUSED
            elif event.key == pygame.K_F1:
                self.cheat_manager.toggle_invincibility()
            elif event.key == pygame.K_F2:
                self._advance_level()
        elif self.current_state == self.STATE_PAUSED:
            if event.key == pygame.K_ESCAPE:
                self.current_state = self.STATE_PLAYING
        elif self.current_state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
            if event.key == pygame.K_SPACE:
                self.current_state = self.STATE_MENU

    def _update_playing(self, dt: float) -> None:
        """Update the level timer and existing win/loss conditions.

        Player controls, ghost movement, collisions, and highscore saving
        remain separate unfinished gameplay tasks.
        """
        if self.player is None or self.maze is None:
            return

        self.time_left -= dt
        if self.time_left <= 0 or self.player.lives <= 0:
            self.time_left = max(0.0, self.time_left)
            self.current_state = self.STATE_GAME_OVER
            return

        if self.maze.is_completed():
            self._advance_level()
