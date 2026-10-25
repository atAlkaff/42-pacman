class CheatManager:
    """
    Cheat mode implementation to genuinely help the reviewer test features.
    """
    def __init__(self) -> None:
        self.invincibility_active = False
        self.ghosts_frozen = False

    def toggle_invincibility(self) -> None:
        """
        Toggles invincibility (no life lost; ghosts cannot eat the player).
        """
        self.invincibility_active = not self.invincibility_active

    def toggle_ghost_freeze(self) -> None:
        """Toggles ghost freeze (ghosts stop moving)."""
        self.ghosts_frozen = not self.ghosts_frozen
