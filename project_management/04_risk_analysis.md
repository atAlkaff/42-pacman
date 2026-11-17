# Risk Analysis

**Likelihood / impact:** Low · Medium · High.
**Status:** Open · Mitigated · Occurred (and handled) · Closed.

| ID | Risk | Likelihood | Impact | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| R1 | The assigned maze package has a different interface or bugs | Medium | High | All access goes through `MazeAdapter`, which validates the generator output and reports failures cleanly; random mazes are retried up to 5 times | Mitigated |
| R2 | The reviewer edits the config during the defense and the game crashes | High | High | Each key validated separately; sizes clamped to 3–60; levels padded to 10; tests try many sizes and broken configs | Occurred (even sizes crashed) → fixed; Mitigated |
| R3 | Unhandled exception shows a traceback (counts as non-functional) | Medium | High | Catch-all in `pac-man.py`; robust highscore loading; errors logged in one clear line | Mitigated |
| R4 | Keyboard differences between our machines and the lab machines | Medium | Medium | Cheats on several keys; physical-key matching; text input only during name entry; `PACMAN_DEBUG_KEYS=1` diagnostic mode | Occurred → fixed |
| R5 | Large mazes run too slowly | Medium | Medium | Cached maze image; distance map reused until the player moves; size limit of 60 | Mitigated |
| R6 | The packaged build does not work on the platform | Medium | High | Spec fixed and tested by launching the built executable without arguments | Mitigated – TODO: confirm on itch.io |
| R7 | `make lint` fails at the defense | Medium | High | `.flake8` and mypy settings committed; lint run before every merge | Mitigated |
| R8 | A team member cannot explain AI-generated code at the defense | TODO | High | TODO: e.g. code walkthrough sessions, each person explains the other's parts | TODO |
| R9 | Not enough time before the deadline | TODO | High | TODO | TODO |
| R10 | Work lost or overwritten when merging | Low | Medium | Pull requests on GitHub; TODO: describe your review rule | TODO |

TODO: add the risks you identified at the start of the project, even the
ones that never happened, and note when each one was identified.
