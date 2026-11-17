# Progress Tracking

One row per week (or per meeting). Compare what was planned for the period
with what was actually done, and explain any gap.

| Week | Planned for the week | Actually done | Status | Notes / evidence |
| --- | --- | --- | --- | --- |
| 2026-10-13 → 10-19 | TODO | Repository created; uv, flake8, Makefile; first maze adapter; bare-bones game; PyInstaller spec | TODO | Commits `9ec8a66` → `38fed5b` |
| 2026-10-20 → 10-26 | TODO | Dummy config; highscore system moved to `utils`; assigned A-Maze-ing package imported; config parser, player movement, scoring (abalfagi) | TODO | Commits `805a610` → `2e91eaa` |
| 2026-10-27 → 11-02 | TODO | Level progression, timers, pause, window-resize fix and their tests (abalfagi) | TODO | Commit `cea2f5e` |
| 2026-11-03 → 11-09 | TODO | Entry point wired to the engine; ghost AI, collisions, lives; menus; name entry; highscores; cheats; keyboard fix; lint; packaging; config hardening; performance | TODO | Pull requests #1–#4 |
| 2026-11-10 → 11-16 | TODO | README written | TODO | Commit `338d47f` |
| TODO | TODO | Project management documents | TODO | |
| TODO | TODO | itch.io upload and final acceptance tests | TODO | |

**Status values:** ✅ on track · ⚠️ late · ❌ blocked · ➕ ahead

## Feature checklist (subject requirements)

| Requirement (subject section) | Status | Where |
| --- | --- | --- |
| Run as `python3 pac-man.py config.json`, exactly one argument (V.1) | ✅ | `pac-man.py` |
| Commented JSON config, robust defaults, unknown keys ignored (V.2, V.3) | ✅ | `src/utils/config_parser.py` |
| Assigned A-Maze-ing package used as-is, `PERFECT=False` (V.4) | ✅ | `src/utils/maze_adapter.py` |
| Persistent top-10 highscores, name rules (V.5) | ✅ | `src/utils/highscore_system.py` |
| Level structure: corner super-pacgums and ghosts, central spawn (VI.1) | ✅ | `src/utils/maze_adapter.py`, `game_engine.py` |
| Player rules: movement, lives, respawn, scoring (VI.2) | ✅ | `src/controllers/game_engine.py` |
| Ghosts: chase, flee, respawn (VI.3) | ✅ | `src/models/entities.py` |
| Cheat mode (VI.5) | ✅ | `game_engine.py`, `cheat_manager.py` |
| ≥ 10 levels with time limits, pause (VI.7) | ✅ | `config.json`, `config_parser.py` |
| Main menu, HUD, pause menu, game-over and victory screens (VI.8) | ✅ | `game_engine.py`, `src/views/` |
| Makefile rules, flake8, mypy (III) | ✅ | `Makefile`, `.flake8`, `pyproject.toml` |
| Packaged game on a public platform (VII) | TODO | `pacman.spec`, itch.io link |
| README with required sections (IX) | ✅ draft | `README.md` |
| Project management folder (VIII) | 🚧 in progress | this folder |
