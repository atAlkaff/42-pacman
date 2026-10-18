import pygame
from typing import List, Tuple
from models.maze_state import MazeState
from models.entities import Player, Ghost


class PygameRenderer:
    """
    Handles all visual rendering using MLX-equivalent Pygame functions.
    Restricts operations to window creation and surface blitting.
    """
    TILE_SIZE = 32

    # Colors
    COLOR_BG = (0, 0, 0)
    COLOR_WALL = (30, 30, 200)
    COLOR_PACGUM = (255, 184, 174)
    COLOR_PLAYER = (255, 255, 0)
    COLOR_GHOST = (255, 0, 0)
    COLOR_GHOST_EDIBLE = (0, 0, 255)

    def __init__(self, grid_width: int, grid_height: int) -> None:
        """Initializes the window display (equivalent to mlx_new_window)."""
        pygame.init()
        self.width = grid_width * self.TILE_SIZE
        # Extra space at the bottom for the HUD
        self.height = (grid_height * self.TILE_SIZE) + 80
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pac-Man")

        # Pre-create simple surfaces (equivalent to mlx images)
        self.wall_img = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
        self.wall_img.fill(self.COLOR_WALL)

    def clear_screen(self) -> None:
        """Clears the previous frame."""
        self.screen.fill(self.COLOR_BG)

    def draw_maze(self, state: MazeState) -> None:
        """
        Draws walls, Pacgums, and Super-pacgums based on the internal grid.
        """
        for r in range(state.height):
            for c in range(state.width):
                x = c * self.TILE_SIZE
                y = r * self.TILE_SIZE
                cell = state.grid[r][c]

                if cell == MazeState.WALL:
                    self.screen.blit(self.wall_img, (x, y))
                elif cell == MazeState.PACGUM:
                    # Draw a small dot
                    pygame.draw.circle(self.screen, self.COLOR_PACGUM,
                                       (x + self.TILE_SIZE // 2,
                                        y + self.TILE_SIZE // 2), 4)
                elif cell == MazeState.SUPER_PACGUM:
                    # Draw a larger power pellet
                    pygame.draw.circle(self.screen, self.COLOR_PACGUM,
                                       (x + self.TILE_SIZE // 2,
                                        y + self.TILE_SIZE // 2), 10)

    def draw_entities(self, player: Player, ghosts: List[Ghost]) -> None:
        """Draws the player and all ghosts at their current grid positions."""
        # Draw player
        px = player.c * self.TILE_SIZE + self.TILE_SIZE // 2
        py = player.r * self.TILE_SIZE + self.TILE_SIZE // 2
        pygame.draw.circle(
            self.screen,
            self.COLOR_PLAYER,
            (px, py),
            self.TILE_SIZE // 2 - 2
        )

        # Draw ghosts
        for ghost in ghosts:
            gx = ghost.c * self.TILE_SIZE + self.TILE_SIZE // 2
            gy = ghost.r * self.TILE_SIZE + self.TILE_SIZE // 2
            if ghost.is_edible:
                color = self.COLOR_GHOST_EDIBLE
            else:
                color = self.COLOR_GHOST
            pygame.draw.circle(
                self.screen,
                color,
                (gx, gy),
                self.TILE_SIZE // 2 - 2
            )

    def update_display(self) -> None:
        """Pushes the rendered frame to the display."""
        pygame.display.flip()
