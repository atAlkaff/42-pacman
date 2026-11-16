# Team Organization

## Members

| Name | 42 login | Main responsibilities |
| --- | --- | --- |
| Afnan Balfagieh | abalfagi | TODO (README lists: maze adapter, configuration parsing, player movement, pacgums and scoring, level progression, timers, pause, window-resize fixes, related tests, README) |
| Ahmed Alkaff | aalkaff | TODO (README lists: ghost pathfinding and personalities, collisions and respawn, menus, name entry, highscores, cheats, maze spawn fix, rendering performance, packaging) |

## Who did what

| Area | Owner | Reviewer | Evidence |
| --- | --- | --- | --- |
| Project setup (uv, Makefile, flake8, spec) | TODO | TODO | Commits from 2026-10-13 to 10-18 |
| Maze adapter | TODO | TODO | `src/utils/maze_adapter.py` |
| Config parser | TODO | TODO | `src/utils/config_parser.py`, `tests/test_config_parser.py` |
| Player movement and scoring | TODO | TODO | `tests/test_player_movement.py`, `tests/test_pacgum_scoring.py` |
| Ghost AI, collisions, lives | TODO | TODO | Pull request #1, `tests/test_ghosts.py` |
| Menus, name entry, highscores, cheats | TODO | TODO | Pull requests #2–#3, `tests/test_menus_and_highscores.py` |
| Lint, packaging, config hardening, performance | TODO | TODO | Pull request #4 |
| README | abalfagi | TODO | `README.md` |
| Project management | TODO | TODO | this folder |
| itch.io release | TODO | TODO | TODO: link |

## How we worked

- **Communication:** TODO (e.g. daily messages, meetings twice a week)
- **Task tracking:** TODO (e.g. GitHub issues, a Kanban board – add a link or screenshot)
- **Branches and reviews:** feature branches merged into `main` through
  pull requests. TODO: who reviews, and what is checked before merging
  (`make lint`, `make test`, a manual run).
- **How decisions were made:** TODO (e.g. discussed in a meeting, the
  owner of the area decides, disagreements settled by …). See
  `03_analysis_and_decisions.md`.
- **How issues were handled:** TODO (e.g. reported as a GitHub issue,
  reproduced, fixed with a test). See `07_blocking_points.md`.

## Use of AI tools

The subject asks for this to be documented in the README. Keep this
section consistent with the README's "AI assistance disclosure".

| Tool | Used for | Parts of the project |
| --- | --- | --- |
| Claude Code | Implementing and testing features; diagnosing bugs | Entry-point wiring, ghost AI, collisions and lives, menus, name entry, highscore hardening, cheats, keyboard-layout fixes, config clamping and padding, even-size maze spawn, rendering performance, packaging, lint configuration, and most of the tests (pull requests #1–#4) |
| TODO (e.g. ChatGPT) | TODO | TODO |

**How we made sure we understand the AI-generated code:** TODO (e.g. code
walkthroughs, rewriting parts, explaining each module to each other).
