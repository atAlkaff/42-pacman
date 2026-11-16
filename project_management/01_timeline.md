# Timeline

## Planned schedule

TODO: replace the dates below with the plan you made at the start of the
project. If you did not write a plan at the start, say so honestly and
present this as the plan you followed from a given date.

```mermaid
gantt
    title Pac-Man – planned schedule
    dateFormat YYYY-MM-DD
    axisFormat %d %b

    section Setup
    Read subject, split work           :p1, 2026-10-13, 2d
    Repository, uv, Makefile, lint     :p2, after p1, 3d

    section Core
    Config parser                      :p3, 2026-10-18, 5d
    Maze adapter (A-Maze-ing package)  :p4, 2026-10-18, 7d
    Player movement and pacgums        :p5, after p4, 5d

    section Gameplay
    Ghost AI and collisions            :p6, TODO-DATE, 5d
    Levels, timers, progression        :p7, TODO-DATE, 4d
    Highscores and name entry          :p8, TODO-DATE, 3d
    Menus, pause, HUD                  :p9, TODO-DATE, 4d
    Cheat mode                         :p10, TODO-DATE, 2d

    section Delivery
    Packaging and itch.io upload       :p11, TODO-DATE, 3d
    README and project management      :p12, TODO-DATE, 4d
    Acceptance testing                 :p13, TODO-DATE, 4d
    Submission                         :milestone, TODO-DATE, 0d
```

> GitHub renders `mermaid` blocks as a chart. A `TODO-DATE` breaks the
> chart until it is replaced with a real date (`YYYY-MM-DD`).

## Planned vs actual

The "Actual" column comes from the git history (`git log --date=short`).

| Milestone | Planned | Actual | Difference / reason |
| --- | --- | --- | --- |
| Project initialized | TODO | 2026-10-13 | |
| uv setup, flake8, PyInstaller spec | TODO | 2026-10-18 | |
| First maze adapter and bare-bones game | TODO | 2026-10-18 | |
| Assigned A-Maze-ing package imported | TODO | 2026-10-24 | TODO: date the package was assigned |
| Config parser, movement, scoring, levels, timers, pause | TODO | 2026-10-25 → 2026-11-01 | |
| Ghost AI, collisions, lives | TODO | 2026-11-05 | |
| Menus, name entry, highscores, cheats | TODO | 2026-11-05 | |
| Keyboard-layout bug fixed on lab machines | – (unplanned) | 2026-11-05 | See 07_blocking_points.md |
| Lint, packaging, config hardening, performance | TODO | 2026-11-05 | |
| README | TODO | 2026-11-16 | |
| Project management documents | TODO | TODO | |
| itch.io upload | TODO | TODO | |
| Submission | TODO | TODO | |

## Comments on the schedule

TODO: 3–5 sentences. Where were you ahead or behind? Why? What did you
change in the plan because of it? (For example: gameplay features landed
in one large integration on 2026-11-05; the documentation started after the
code was complete.)
