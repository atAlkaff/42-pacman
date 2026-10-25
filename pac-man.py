import sys
import os
import logging
from typing import NoReturn

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'src')
))

from utils.config_parser import parse_config, GameConfig

# Configure logging for the main entry point to avoid tracebacks
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main() -> NoReturn | None:
    """
    Main entry point for the Pac-Man game.
    Validates command-line arguments, loads the configuration, and
    starts the game loop.
    """
    # Enforce exactly one argument for the configuration file
    if len(sys.argv) != 2:
        logging.error("Usage: python3 pac-man.py <config.json>")
        sys.exit(1)

    config_filepath: str = sys.argv[1]

    # Parse configuration, which handles missing files and invalid keys cleanly
    config: GameConfig = parse_config(config_filepath)

    logging.info("Configuration loaded successfully. Starting game engine...")

    # TODO: Initialize and run the main game controller/engine here.
    # engine = GameEngine(config)
    # engine.run()

    sys.exit(0)


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
