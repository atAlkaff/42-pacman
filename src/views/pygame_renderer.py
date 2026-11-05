"""Draw Pac-Man maze, entities, and basic game-state messages."""

from typing import List, Sequence

import pygame

from models.entities import Ghost, Player
from models.maze_state import MazeState


class PygameRenderer:
    """Manage the display and draw the current game state."""

    TILE_SIZE = 32
    HUD_HEIGHT = 80
    # The play area never gets smaller than this, so menus and the
    # instructions still fit when a level uses a tiny maze.
    MIN_PLAY_WIDTH = 480
    MIN_PLAY_HEIGHT = 480

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
    COLOR_TITLE = (255, 255, 0)
    COLOR_SELECTED = (255, 255, 0)
    COLOR_DIM = (170, 170, 170)
    COLOR_OVERLAY = (0, 0, 0, 170)

    FONT_TITLE = 56
    FONT_ITEM = 32
    FONT_LINE = 23

    def __init__(self, grid_width: int, grid_height: int) -> None:
        """Create a game window sized to the initial maze."""
        pygame.init()
        pygame.display.set_caption("Pac-Man")
        self.tile_size = self.TILE_SIZE
        self.width = 0
        self.height = 0
        self.offset_x = 0
        self.offset_y = 0
        self.screen: pygame.Surface
        self.wall_img: pygame.Surface
        self._fonts: dict[int, pygame.font.Font] = {}

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
        maze_width = grid_width * self.tile_size
        maze_height = grid_height * self.tile_size
        self.width = max(maze_width, self.MIN_PLAY_WIDTH)
        play_height = max(maze_height, self.MIN_PLAY_HEIGHT)
        self.height = play_height + self.HUD_HEIGHT
        # Center a small maze inside the (minimum-size) play area.
        self.offset_x = (self.width - maze_width) // 2
        self.offset_y = (play_height - maze_height) // 2

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
                x = self.offset_x + c * self.tile_size
                y = self.offset_y + r * self.tile_size
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
        px = self.offset_x + player.c * self.tile_size + half_tile
        py = self.offset_y + player.r * self.tile_size + half_tile
        pygame.draw.circle(
            self.screen, self.COLOR_PLAYER, (px, py), radius
        )

        for index, ghost in enumerate(ghosts):
            if ghost.is_eaten:
                continue  # Waiting in its corner to respawn.
            gx = self.offset_x + ghost.c * self.tile_size + half_tile
            gy = self.offset_y + ghost.r * self.tile_size + half_tile
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

    def _font(self, size: int) -> pygame.font.Font:
        """Return a cached default font of the given pixel size."""
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont(None, size)
        return self._fonts[size]

    def _blit_centered(
        self,
        text: str,
        size: int,
        color: tuple[int, int, int],
        center_y: int,
    ) -> None:
        """Draw one line of text centered horizontally at ``center_y``."""
        image = self._font(size).render(text, True, color)
        self.screen.blit(
            image, image.get_rect(center=(self.width // 2, center_y))
        )

    def draw_centered_message(self, title: str, subtitle: str) -> None:
        """Draw a short two-line message over the middle of the maze."""
        center_y = (self.height - self.HUD_HEIGHT) // 2
        self._blit_centered(title, 40, self.COLOR_TITLE, center_y)
        if subtitle:
            self._blit_centered(
                subtitle, 26, self.COLOR_TEXT, center_y + 40
            )

    def draw_overlay(self) -> None:
        """Darken the whole window, e.g. behind the pause menu."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

    def draw_menu(
        self,
        title: str,
        items: Sequence[str] = (),
        selected: int | None = None,
        lines: Sequence[str] = (),
    ) -> None:
        """Draw a full screen: a title, menu items, then text lines.

        Args:
            title: Large heading at the top of the block.
            items: Selectable entries; ``selected`` is highlighted.
            selected: Index of the highlighted item, or None.
            lines: Smaller information lines below the items. An empty
                string leaves a blank line.
        """
        title_gap = 70
        item_step = 42
        line_step = 25
        block_height = (
            title_gap
            + len(items) * item_step
            + (20 if items and lines else 0)
            + len(lines) * line_step
        )
        play_height = self.height - self.HUD_HEIGHT
        y = max(40, (play_height - block_height) // 2)

        self._blit_centered(title, self.FONT_TITLE, self.COLOR_TITLE, y)
        y += title_gap

        for index, item in enumerate(items):
            if index == selected:
                self._blit_centered(
                    f"> {item} <", self.FONT_ITEM, self.COLOR_SELECTED, y
                )
            else:
                self._blit_centered(item, self.FONT_ITEM, self.COLOR_TEXT, y)
            y += item_step

        if items and lines:
            y += 20
        for line in lines:
            if line:
                self._blit_centered(
                    line, self.FONT_LINE, self.COLOR_DIM, y
                )
            y += line_step

    def update_display(self) -> None:
        """Present the latest frame."""
        pygame.display.flip()
