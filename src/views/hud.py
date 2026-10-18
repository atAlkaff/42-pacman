import pygame
from typing import Tuple


class HUD:
    """
    Renders the constantly visible In-Game HUD displaying score,
    lives, level, and time.
    """
    COLOR_TEXT = (255, 255, 255)

    def __init__(
        self,
        screen: pygame.Surface,
        start_y: int,
        width: int
    ) -> None:
        self.screen = screen
        self.start_y = start_y
        self.width = width
        # Use default Pygame font (equivalent to mlx_string_put constraints)
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, score: int, lives: int, level: int, time_left: int) -> None:
        """
        Draws the required HUD elements at the bottom of the screen.
        """
        # Render text surfaces
        score_surf = self.font.render(f"Score: {score}", True, self.COLOR_TEXT)
        lives_surf = self.font.render(f"Lives: {lives}", True, self.COLOR_TEXT)
        level_surf = self.font.render(f"Level: {level}", True, self.COLOR_TEXT)
        time_surf = self.font.render(
            f"Time: {time_left}s",
            True,
            self.COLOR_TEXT
        )

        # Distribute horizontally across the bottom area
        padding = 20
        self.screen.blit(score_surf, (padding, self.start_y + 20))
        self.screen.blit(lives_surf, (self.width // 4, self.start_y + 20))
        self.screen.blit(level_surf, (self.width // 2, self.start_y + 20))
        self.screen.blit(time_surf, (self.width * 3 // 4, self.start_y + 20))
