# Team Organization

## Members

| Name | 42 login | Main responsibilities |
| --- | --- | --- |
| Afnan Balfagieh | abalfagi | Maze adapter, configuration parsing, player movement, pacgums and scoring, level progression, timers, pause, window-resize fixes, related tests, README |
| Ahmed Alkaff | aalkaff | ghost pathfinding and personalities, collisions and respawn, menus, name entry, highscores, cheats, maze spawn fix, rendering performance, packaging |

## Who did what

| Area | Owner | Reviewer |
| --- | --- | --- | --- |
| Project setup (uv, Makefile, flake8, spec) | aalkaff | abalfagi |
| Maze adapter | abalfagi | aalkaff |
| Config parser | abalfagi | aalkaff |
| Player movement and scoring | abalfagi | aalkaff |
| Ghost AI, collisions, lives | aalkaff | abalfagi |
| Menus, name entry, highscores, cheats | aalkaff | abalfagi |
| Lint, packaging, config hardening, performance | aalkaff | abalfagi |
| README | abalfagi | aalkaff |
| Project management | aalkaff | abalfagi |
| itch.io release | aalkaff | abalfagi |

## How we worked

- **Communication:** Whatsapp Messages, Google Meet, and in person meetings at 42 campus
- **Task tracking:** Regular status updates and meetings.
- **Branches and reviews:** feature branches merged into `main` through
  pull requests.
- **How decisions were made:** Discussed in meetings, the
  owner of the area decides. See
  `03_analysis_and_decisions.md`.
- **How issues were handled:** Reproduced, discussed, fixed with a test. See `07_blocking_points.md`.
