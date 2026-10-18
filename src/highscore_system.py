import json
import logging
import re
from typing import List, Dict, Any


class HighscoreSystem:
    """
    Persistent highscore system robust to file errors.
    """
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.scores: List[Dict[str, Any]] = self._load_scores()

    def _load_scores(self) -> List[Dict[str, Any]]:
        """Loads highscores, catching errors cleanly to avoid tracebacks."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Highscore file error ({e}). "
                            f"Initializing empty list.")
        return []

    def save_score(self, player_name: str, score: int) -> None:
        """
        Validates the player name, adds the score, and persists the top 10.
        """
        if score < 0:
            return  # Handle scores (non-negative integers)

        # Handle player names (max 10 characters, alphanumeric and spaces only)
        clean_name = re.sub(r'[^a-zA-Z0-9 ]', '', player_name)[:10]
        if not clean_name.strip():
            clean_name = "UNKNOWN"

        self.scores.append({"name": clean_name, "score": score})
        # Keep the top 10 highscores[cite: 10]
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save highscores: {e}")
