
"""Load and validate Pac-Man settings from a commented JSON file."""

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


class LevelConfig(BaseModel):
    """Represent one level's maze dimensions and optional time limit."""

    model_config = ConfigDict(extra="ignore")

    width: int = Field(default=21, ge=3)
    height: int = Field(default=21, ge=3)
    time_limit: int | None = Field(default=None, ge=10)


class GameConfig(BaseModel):
    """Represent game settings with validated, safe defaults."""

    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = "highscores.json"
    lives: int = Field(default=3, ge=1)
    pacgum: int = Field(default=42, ge=0)
    points_per_pacgum: int = Field(default=10, ge=0)
    points_per_super_pacgum: int = Field(default=50, ge=0)
    points_per_ghost: int = Field(default=200, ge=0)
    seed: int = 42
    level_max_time: int = Field(default=90, ge=10)
    level: list[LevelConfig] = Field(
        default_factory=lambda: [LevelConfig()],
        min_length=1,
    )


def strip_comments(json_str: str) -> str:
    """Remove whole lines that begin with # or // (after whitespace)."""
    return re.sub(r"(?m)^[ \t]*(?:#|//)[^\r\n]*$", "", json_str)


def _parse_levels(value: Any) -> list[LevelConfig]:
    """Validate each level while preserving its other valid fields."""
    if not isinstance(value, list) or not value:
        logging.warning("Invalid 'level' list. Using the default level.")
        return [LevelConfig()]

    levels: list[LevelConfig] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            logging.warning(
                "Invalid level %d. Using default settings.", index
            )
            levels.append(LevelConfig())
            continue

        values: dict[str, Any] = {}
        for dimension in ("width", "height", "time_limit"):
            if dimension not in item:
                continue
            try:
                checked = LevelConfig.model_validate(
                    {dimension: item[dimension]}
                )
                values[dimension] = getattr(checked, dimension)
            except ValidationError:
                logging.warning(
                    "Invalid level %d %s. Using the default value.",
                    index,
                    dimension,
                )

        levels.append(LevelConfig.model_validate(values))

    return levels


def parse_config(filepath: str) -> GameConfig:
    """Read commented JSON and replace invalid settings with safe defaults.

    Keep valid settings even when other fields or levels are invalid.
    Unknown settings are ignored.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_content = file.read()
    except OSError as exc:
        logging.error(
            "Cannot read configuration file '%s': %s. Using defaults.",
            filepath,
            exc,
        )
        return GameConfig()

    try:
        parsed_json: object = json.loads(strip_comments(raw_content))
    except json.JSONDecodeError as exc:
        logging.error(
            "Invalid JSON in '%s': %s. Using defaults.", filepath, exc
        )
        return GameConfig()

    if not isinstance(parsed_json, dict):
        logging.error("Configuration root must be an object. Using defaults.")
        return GameConfig()

    safe_data: dict[str, Any] = {}

    for key in GameConfig.model_fields:
        if key not in parsed_json:
            continue

        if key == "level":
            safe_data[key] = _parse_levels(parsed_json[key])
            continue

        try:
            checked = GameConfig.model_validate({key: parsed_json[key]})
            safe_data[key] = getattr(checked, key)
        except ValidationError:
            logging.warning(
                "Invalid value for '%s'. Using the default value.", key
            )

    return GameConfig.model_validate(safe_data)
