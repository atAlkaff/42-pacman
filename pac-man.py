"""Command-line entry point: python3 pac-man.py <config.json>."""

import logging
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'src')
))

import pygame  # noqa: E402

from controllers.game_engine import GameEngine  # noqa: E402
from utils.config_parser import GameConfig, parse_config  # noqa: E402
from utils.maze_adapter import MazeAdapter  # noqa: E402
from views.pygame_renderer import PygameRenderer  # noqa: E402

# Configure logging for the main entry point to avoid tracebacks.
# force=True: an imported module may already have configured logging.
logging.basicConfig(
    level=logging.INFO, format='%(levelname)s: %(message)s', force=True
)


def is_packaged() -> bool:
    """True when running as the PyInstaller build (e.g. from itch.io)."""
    return bool(getattr(sys, "frozen", False))


def packaged_config_path() -> str:
    """Config for the packaged game when it is started without arguments.

    A game platform or a double-click passes no arguments, so the build
    uses the config.json next to the executable (players can edit it), or
    the copy bundled inside the build.
    """
    beside_executable = os.path.join(
        os.path.dirname(sys.executable), "config.json"
    )
    if os.path.isfile(beside_executable):
        return beside_executable
    bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.join(bundle_dir, "config.json")


def main() -> None:
    """
    Main entry point for the Pac-Man game.
    Validates command-line arguments, loads the configuration, and
    starts the game loop.
    """
    # Enforce exactly one argument for the configuration file. Only the
    # packaged build may start without one (see packaged_config_path).
    if len(sys.argv) == 1 and is_packaged():
        config_filepath = packaged_config_path()
    elif len(sys.argv) == 2:
        config_filepath = sys.argv[1]
    else:
        logging.error("Usage: python3 pac-man.py <config.json>")
        sys.exit(1)

    # Parse configuration, which handles missing files and invalid keys cleanly
    config: GameConfig = parse_config(config_filepath)

    if is_packaged() and not os.path.isabs(config.highscore_filename):
        # The bundled files live in a temporary folder that is deleted on
        # exit, so keep highscores next to the executable instead.
        config.highscore_filename = os.path.join(
            os.path.dirname(sys.executable), config.highscore_filename
        )

    logging.info("Configuration loaded successfully. Starting game engine...")

    # The adapter turns each maze cell into a floor tile plus a wall/passage
    # tile, with one closing border, so the grid is (2 * size + 1) per side.
    first_level = config.level[0]
    renderer = PygameRenderer(
        first_level.width * 2 + 1, first_level.height * 2 + 1
    )
    adapter = MazeAdapter(first_level.width, first_level.height)
    engine = GameEngine(config, renderer, adapter)
    try:
        engine.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Game interrupted by user. Exiting cleanly.")
        sys.exit(0)
    except Exception as e:
        # Catch-all to ensure no unhandled exceptions or
        # tracebacks are ever displayed
        logging.critical(f"An unexpected fatal error occurred: {e}")
        sys.exit(1)
