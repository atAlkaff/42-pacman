import json
import logging
import re
from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict, ValidationError

# Configure logging for clear message output without tracebacks
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


class GameConfig(BaseModel):
    """
    Data model defining the configuration schema with safe defaults.
    Enforces strict typing and boundary validation.
    """
    model_config = ConfigDict(extra='ignore')  # Unknown keys must be ignored

    highscore_filename: str = "highscores.json"
    lives: int = Field(default=3, ge=1)
    pacgum: int = Field(default=42, ge=0)
    points_per_pacgum: int = Field(default=10, ge=0)
    points_per_super_pacgum: int = Field(default=50, ge=0)
    points_per_ghost: int = Field(default=200, ge=0)
    seed: int = 42
    level_max_time: int = Field(default=90, ge=10)


def strip_comments(json_str: str) -> str:
    """
    Removes lines starting with '#' or '//' to support custom JSON comments
    """
    # Matches any line where the first non-whitespace character is # or //
    return re.sub(r'(?m)^\s*(#|//).*$', '', json_str)


def parse_config(filepath: str) -> GameConfig:
    """
    Reads the configuration file, strips comments, and validates the JSON.
    Any missing file, invalid JSON, or faulty value is clamped to safe
    defaults.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content: str = f.read()
    except FileNotFoundError:
        logging.error(f"Configuration file '{filepath}' missing. "
                      f"Clamping to safe defaults.")
        return GameConfig()
    except Exception as e:
        logging.error(f"Error accessing configuration file: {e}. "
                      f"Clamping to safe defaults.")
        return GameConfig()

    clean_content: str = strip_comments(raw_content)

    try:
        raw_data: Dict[str, Any] = json.loads(clean_content)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON structure in '{filepath}': {e}. "
                      f"Clamping to safe defaults.")
        return GameConfig()

    # Granular clamping: validate key-by-key to preserve valid
    # entries while clamping faulty ones
    safe_data: Dict[str, Any] = {}
    defaults: Dict[str, Any] = GameConfig().model_dump()

    for key, default_value in defaults.items():
        if key in raw_data:
            try:
                # Test if the individual field passes Pydantic's type
                # checking and boundary constraints
                validated_model = GameConfig(**{key: raw_data[key]})
                safe_data[key] = getattr(validated_model, key)
            except ValidationError:
                logging.warning(f"Invalid value for '{key}'. "
                                f"Clamping to default: {default_value}.")
                safe_data[key] = default_value
        else:
            safe_data[key] = default_value

    # Merge unknown keys safely (they will be ignored by Pydantic's ConfigDict)
    safe_data.update({k: v for k, v in raw_data.items() if k not in defaults})

    return GameConfig(**safe_data)
