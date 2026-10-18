import pygame
from typing import List
from models.maze_state import MazeState
from models.entities import Player, Ghost
from views.pygame_renderer import PygameRenderer
from views.hud import HUD
from utils.maze_adapter import MazeAdapter
from utils.config_parser import GameConfig
from controllers.cheat_manager import CheatManager


class GameEngine:
    """
    Core state machine managing the game loop, level
    progression, and UI states.
    """
    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    STATE_GAME_OVER = 3

    def __init__(
        self,
        config: GameConfig,
        renderer: PygameRenderer,
        adapter: MazeAdapter
    ) -> None:
        self.config = config
        self.renderer = renderer
        self.adapter = adapter
        self.hud = HUD(
            self.renderer.screen,
            self.renderer.height - 80,
            self.renderer.width
        )
        self.cheat_manager = CheatManager()

        self.current_state = self.STATE_MENU
        self.level = 1
        self.time_left = float(self.config.level_max_time)
        self.clock = pygame.time.Clock()

        # Entities
        self.player: Player | None = None
        self.ghosts: List[Ghost] = []
        self.maze: MazeState | None = None

    def _init_level(self) -> None:
        """
        Generates the maze and instantiates entities for the current level.
        """
        if self.level == 1:
            seed = self.config.seed
        else:
            seed = None  # Fixed seed for level 1
        grid = self.adapter.generate_maze(seed=seed if seed else 0)
        self.maze = MazeState(grid)

        # Retain score and lives across levels, or initialize if starting fresh
        current_score = self.player.score if self.player else 0
        current_lives = self.player.lives if self.player else self.config.lives

        center_r, center_c = self.maze.height // 2, self.maze.width // 2
        self.player = Player(center_r, center_c, current_lives)
        self.player.score = current_score

        # 4 ghosts, one in each corner[cite: 11]
        self.ghosts = [
            Ghost(1, 1),
            Ghost(1, self.maze.width - 2),
            Ghost(self.maze.height - 2, 1),
            Ghost(self.maze.height - 2, self.maze.width - 2)
        ]
        self.time_left = float(self.config.level_max_time)

    def run(self) -> None:
        """Main game loop handling events, updates, and rendering."""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_input(event)

            self.renderer.clear_screen()

            if self.current_state == self.STATE_PLAYING:
                self._update_playing(dt)
                self.renderer.draw_maze(self.maze)  # type: ignore
                self.renderer.draw_entities(
                    self.player,
                    self.ghosts
                )  # type: ignore
                self.hud.draw(
                    self.player.score,
                    self.player.lives,
                    self.level,
                    int(self.time_left)
                )  # type: ignore
            elif self.current_state == self.STATE_MENU:
                # Rendering logic for menu (Push SPACE to play, Highscores)
                pass
            elif self.current_state == self.STATE_GAME_OVER:
                # Rendering logic for game over and name input
                pass

            self.renderer.update_display()

    def _handle_input(self, event: pygame.event.Event) -> None:
        """Processes keyboard input based on current state."""
        if event.type == pygame.KEYDOWN:
            if (
                self.current_state == self.STATE_MENU
                and event.key == pygame.K_SPACE
            ):
                self.level = 1
                self._init_level()
                self.current_state = self.STATE_PLAYING
            elif self.current_state == self.STATE_PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.current_state = self.STATE_PAUSED
                # Cheat toggles for evaluation
                elif event.key == pygame.K_F1:
                    self.cheat_manager.toggle_invincibility()
                elif event.key == pygame.K_F2:
                    self.level += 1
                    self._init_level()

    def _update_playing(self, dt: float) -> None:
        """
        Updates game logic, physics, and win/loss conditions
        during active play.
        """
        self.time_left -= dt
        if self.time_left <= 0:
            # End game on timeout
            self.current_state = self.STATE_GAME_OVER

        if self.player.lives <= 0:  # type: ignore
            # End game when lives lost
            self.current_state = self.STATE_GAME_OVER

        if self.maze.is_completed():  # type: ignore
            self.level += 1
            self._init_level()  # Move to next level
