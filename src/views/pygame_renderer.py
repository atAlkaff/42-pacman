"""Draw Pac-Man maze, entities, and basic game-state messages."""

from typing import List

import pygame

from models.entities import Ghost, Player
from models.maze_state import MazeState


class PygameRenderer:
    """Manage the display and draw the current game state."""

    TILE_SIZE = 32
    HUD_HEIGHT = 80

    COLOR_BG = (0, 0, 0)
    COLOR_WALL = (30, 30, 200)
    COLOR_PACGUM = (255, 184, 174)
    COLOR_PLAYER = (255, 255, 0)
    # One color per corner ghost (red, pink, cyan, orange).
    GHOST_COLORS = (
        (255, 0, 0),
        (255, 184, 255),
        (0, 255, 255),
        (255, 184, 82),
    )
    COLOR_GHOST_EDIBLE = (0, 0, 255)
    COLOR_GHOST_FLASH = (255, 255, 255)
    # Edible ghosts flash during the last seconds of power mode.
    FLASH_WARNING_TIME = 2.0
    COLOR_TEXT = (255, 255, 255)

    def __init__(self, grid_width: int, grid_height: int) -> None:
        """Create a game window sized to the initial maze."""
        pygame.init()
        pygame.display.set_caption("Pac-Man")
        self.tile_size = self.TILE_SIZE
        self.width = 0
        self.height = 0
        self.screen: pygame.Surface
        self.wall_img: pygame.Surface

        # Read desktop dimensions BEFORE creating or resizing the window.
        # display.Info() may report the current window size after set_mode(),
        # which would make each successive level smaller than the last.
        desktop_sizes = pygame.display.get_desktop_sizes()
        if desktop_sizes:
            desktop_width, desktop_height = desktop_sizes[0]
        else:
            info = pygame.display.Info()
            desktop_width, desktop_height = info.current_w, info.current_h

        self._desktop_width = max(1, int(desktop_width))
        self._desktop_height = max(1, int(desktop_height))
        self.resize_grid(grid_width, grid_height)

    def resize_grid(self, grid_width: int, grid_height: int) -> None:
        """Resize the display and tile sprites to fit a new level.

        Keep room for the HUD and fit large mazes on typical displays.
        """
        if grid_width <= 0 or grid_height <= 0:
            raise ValueError("Grid dimensions must be positive")

        # Use the cached DESKTOP size, never the last window's size.
        available_width = max(1, min(1000, int(self._desktop_width * 0.90)))
        available_height = max(
            1,
            min(850, int(self._desktop_height * 0.85)) - self.HUD_HEIGHT,
        )

        self.tile_size = max(
            1,
            min(
                self.TILE_SIZE,
                available_width // grid_width,
                available_height // grid_height,
            ),
        )
        self.width = grid_width * self.tile_size
        self.height = grid_height * self.tile_size + self.HUD_HEIGHT

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.wall_img = pygame.Surface((self.tile_size, self.tile_size))
        self.wall_img.fill(self.COLOR_WALL)

    def clear_screen(self) -> None:
        """Erase the previous frame."""
        self.screen.fill(self.COLOR_BG)

    def draw_maze(self, state: MazeState) -> None:
        """Draw maze walls, dots, and power pellets."""
        half_tile = self.tile_size // 2
        for r in range(state.height):
            for c in range(state.width):
                x = c * self.tile_size
                y = r * self.tile_size
                cell = state.grid[r][c]
                if cell == MazeState.WALL:
                    self.screen.blit(self.wall_img, (x, y))
                elif cell in (MazeState.PACGUM, MazeState.SUPER_PACGUM):
                    radius = (
                        max(1, self.tile_size // 8)
                        if cell == MazeState.PACGUM
                        else max(2, self.tile_size // 3)
                    )
                    pygame.draw.circle(
                        self.screen,
                        self.COLOR_PACGUM,
                        (x + half_tile, y + half_tile),
                        radius,
                    )

    def draw_entities(self, player: Player, ghosts: List[Ghost]) -> None:
        """Draw Pac-Man and the four ghosts at their grid positions."""
        half_tile = self.tile_size // 2
        radius = max(1, half_tile - 2)
        px = player.c * self.tile_size + half_tile
        py = player.r * self.tile_size + half_tile
        pygame.draw.circle(
            self.screen, self.COLOR_PLAYER, (px, py), radius
        )

        for index, ghost in enumerate(ghosts):
            if ghost.is_eaten:
                continue  # Waiting in its corner to respawn.
            gx = ghost.c * self.tile_size + half_tile
            gy = ghost.r * self.tile_size + half_tile
            if not ghost.is_edible:
                color = self.GHOST_COLORS[index % len(self.GHOST_COLORS)]
            elif (
                ghost.edible_timer < self.FLASH_WARNING_TIME
                and int(ghost.edible_timer * 6) % 2 == 0
            ):
                color = self.COLOR_GHOST_FLASH
            else:
                color = self.COLOR_GHOST_EDIBLE
            pygame.draw.circle(self.screen, color, (gx, gy), radius)

    def draw_centered_message(self, title: str, subtitle: str) -> None:
        """Draw simple placeholder menu and result messages."""
        font = pygame.font.SysFont(None, 40)
        small_font = pygame.font.SysFont(None, 26)
        center_x = self.width // 2
        center_y = (self.height - self.HUD_HEIGHT) // 2

        title_image = font.render(title, True, self.COLOR_TEXT)
        subtitle_image = small_font.render(subtitle, True, self.COLOR_TEXT)
        self.screen.blit(
            title_image, title_image.get_rect(center=(center_x, center_y))
        )
        self.screen.blit(
            subtitle_image,
            subtitle_image.get_rect(center=(center_x, center_y + 40)),
        )

    def update_display(self) -> None:
        """Present the latest frame."""
        pygame.display.flip()
