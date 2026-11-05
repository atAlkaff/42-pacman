"""Toggleable cheat modes that help reviewers test every feature."""


class CheatManager:
    """
    Cheat mode implementation to genuinely help the reviewer test features.

    Only the cheats that stay on are stored here. One-shot cheats (skip a
    level, extra life, power mode, low timer) are actions in the engine.
    """

    def __init__(self) -> None:
        """Start with every cheat turned off."""
        self.invincibility_active = False
        self.ghosts_frozen = False
        self.speed_boost_active = False

    def toggle_invincibility(self) -> None:
        """
        Toggles invincibility (no life lost; ghosts cannot eat the player).
        """
        self.invincibility_active = not self.invincibility_active

    def toggle_ghost_freeze(self) -> None:
        """Toggles ghost freeze (ghosts stop moving)."""
        self.ghosts_frozen = not self.ghosts_frozen

    def toggle_speed_boost(self) -> None:
        """Toggles increased speed (the player moves twice as fast)."""
        self.speed_boost_active = not self.speed_boost_active

    def active_labels(self) -> list[str]:
        """Short names of the cheats that are currently on, for the HUD."""
        labels = []
        if self.invincibility_active:
            labels.append("F1 invincible")
        if self.ghosts_frozen:
            labels.append("F3 frozen")
        if self.speed_boost_active:
            labels.append("F5 speed")
        return labels
