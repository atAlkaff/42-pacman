"""Persistent top-10 highscore table stored as a JSON file."""

import json
import logging
import re
from typing import Any


class HighscoreSystem:
    """
    Persistent highscore system robust to file errors.

    Scores are kept in a JSON list of ``{"name": str, "score": int}``
    objects, sorted from best to worst. Any unreadable file or malformed
    entry is ignored with a warning instead of crashing the game.
    """

    MAX_ENTRIES = 10
    MAX_NAME_LENGTH = 10
    DEFAULT_NAME = "UNKNOWN"

    def __init__(self, filename: str) -> None:
        """Load existing highscores from ``filename`` (if any)."""
        self.filename = filename
        self.scores: list[dict[str, Any]] = self._load_scores()

    @classmethod
    def is_valid_name_char(cls, char: str) -> bool:
        """Return True for characters allowed in names (A-Z, a-z, 0-9, ' ')."""
        return len(char) == 1 and char.isascii() and (
            char.isalnum() or char == " "
        )

    @classmethod
    def clean_name(cls, player_name: str) -> str:
        """Keep allowed characters only, at most 10, never empty."""
        clean = re.sub(r"[^a-zA-Z0-9 ]", "", player_name)
        clean = clean.strip()[:cls.MAX_NAME_LENGTH].strip()
        return clean or cls.DEFAULT_NAME

    @staticmethod
    def _is_valid_score(score: object) -> bool:
        """Scores are non-negative integers (booleans are rejected)."""
        return (
            isinstance(score, int)
            and not isinstance(score, bool)
            and score >= 0
        )

    def _load_scores(self) -> list[dict[str, Any]]:
        """Loads highscores, catching errors cleanly to avoid tracebacks."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logging.info(
                "No highscore file '%s' yet. Starting a new table.",
                self.filename,
            )
            return []
        except (OSError, UnicodeDecodeError, ValueError) as e:
            # ValueError also covers json.JSONDecodeError.
            logging.warning(
                "Cannot read highscore file '%s' (%s). Starting empty.",
                self.filename,
                e,
            )
            return []

        if not isinstance(data, list):
            logging.warning("Highscore file is not a list. Starting empty.")
            return []

        scores: list[dict[str, Any]] = []
        for entry in data:
            if (
                isinstance(entry, dict)
                and isinstance(entry.get("name"), str)
                and self._is_valid_score(entry.get("score"))
            ):
                scores.append({
                    "name": self.clean_name(entry["name"]),
                    "score": entry["score"],
                })
            else:
                logging.warning("Ignoring invalid highscore entry: %r", entry)

        scores.sort(key=lambda item: item["score"], reverse=True)
        return scores[:self.MAX_ENTRIES]

    def top_scores(self) -> list[tuple[str, int]]:
        """Return the table as ``(name, score)`` pairs, best first."""
        return [(item["name"], item["score"]) for item in self.scores]

    def save_score(self, player_name: str, score: int) -> bool:
        """
        Validates the player name, adds the score, and persists the top 10.

        Returns:
            True if the table was written to disk, False otherwise.
        """
        if not self._is_valid_score(score):
            logging.warning("Ignoring invalid score %r.", score)
            return False

        self.scores.append({"name": self.clean_name(player_name),
                            "score": score})
        # Stable sort: an equal new score goes after the older ones.
        self.scores.sort(key=lambda item: item["score"], reverse=True)
        self.scores = self.scores[:self.MAX_ENTRIES]

        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=4)
        except (OSError, TypeError, ValueError) as e:
            logging.error("Failed to save highscores: %s", e)
            return False
        return True
