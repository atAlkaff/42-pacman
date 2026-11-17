# Acceptance Test Plan

Manual tests that check every requirement of the subject from a player's
or reviewer's point of view. Run them on a lab machine before submission
and again with the packaged build.

**How to record a result:** put ✅ (pass) or ❌ (fail) in the `Result`
column, with the date and initials, e.g. `✅ 2026-11-20 AA`. A failure gets
a row in the "Bugs found" table below.

Automated tests complement this plan: `make test` runs 63 unit tests
(movement, scoring, ghosts, collisions, menus, name entry, cheats, the
highscore file, config parsing, and many maze sizes).

## Launch and configuration

| ID | Test | Steps | Expected | Result |
| --- | --- | --- | --- | --- |
| A1 | Normal launch | `make run` | Main menu opens, no errors | ✅ |
| A2 | Wrong argument count | `python3 pac-man.py`, then `python3 pac-man.py a b` | Usage message, no traceback | ✅ |
| A3 | Missing config file | `python3 pac-man.py nope.json` | Error logged, game starts with defaults | ✅ |
| A4 | Invalid JSON | Config containing `{"lives": }` | Error logged, defaults used | ✅ |
| A5 | Comments | `#` and `//` full-line comments in the config | Accepted, values applied | ✅ |
| A6 | Invalid values | `"lives": "x"`, `"seed": "abc"` | Warning, default used for that key only | ✅ |
| A7 | Unknown keys | `"foo": 1` | Ignored silently | ✅ |
| A8 | Maze sizes | Levels of 3×3, 20×20, 40×12 | Every level playable; spawn on an open tile | ✅ |
| A9 | Out-of-range size | `"width": 500` | Warning, clamped to 60 | ✅ |
| A10 | Fewer than 10 levels | Config with 2 levels | Warning, game has 10 levels | ✅ |

## Gameplay

| ID | Test | Steps | Expected | Result |
| --- | --- | --- | --- | --- |
| G1 | Movement | Arrow keys and WASD | Moves one tile per press, repeats while held, blocked by walls | ✅ |
| G2 | Pacgum | Eat a small pacgum | Score + `points_per_pacgum`, dot disappears | ✅ |
| G3 | Super-pacgum | Eat a corner pellet | Score + `points_per_super_pacgum`, ghosts turn blue for about 6 s, flash at the end | ✅ |
| G4 | Eat a ghost | Touch a blue ghost | Score + `points_per_ghost`; ghost disappears, returns to its corner after 5 s, dangerous | ✅ |
| G5 | Lose a life | Touch a normal ghost | One life lost, everyone respawns, "READY!" pause | ✅ |
| G6 | Game over by lives | Lose every life | Game-over screen with the final score and name entry | ✅ |
| G7 | Level complete | Eat every pellet (or use cheat 2) | Next level with a new maze; score and lives kept | ✅ |
| G8 | Level 1 seed | Start two games | Level 1 maze is identical both times; level 2 differs | ✅ |
| G9 | Time-out | Cheat 8, wait 5 s | Game over | ✅ |
| G10 | Victory | Finish the last level (cheat 2 repeatedly) | Victory screen with the score and name entry | ✅ |
| G11 | Ghost behaviour | Watch the ghosts | They chase; they flee when blue; each behaves differently | ✅ |

## Interface

| ID | Test | Steps | Expected | Result |
| --- | --- | --- | --- | --- |
| U1 | Main menu | Navigate all four entries | Start, Highscores, Instructions, Exit all work | ✅ |
| U2 | HUD | During play | Score, lives, level, and time always visible | ✅ |
| U3 | Pause | ESC during play | Pause menu; timer stopped; Resume and Main Menu work | ✅ |
| U4 | Name entry rules | Type `Al!ce Smith_long`, then Backspace | Only letters, digits, spaces; max 10 characters | ✅ |
| U5 | Skip saving | ESC on the name screen | Back to menu, nothing saved | ✅ |

## Highscores

| ID | Test | Steps | Expected | Result |
| --- | --- | --- | --- | --- |
| H1 | Persistence | Save a score, quit, relaunch | Score listed on the menu and Highscores screen | ✅ |
| H2 | Top 10 only | Save 11 scores | Only the 10 best are kept, sorted | ✅ |
| H3 | Corrupt file | Write `not json` into the highscore file, launch | Warning, empty table, no crash | ✅ |
| H4 | Bad entries | File with a negative score and a missing name | Bad entries skipped, good ones kept | ✅ |

## Cheats

| ID | Test | Steps | Expected | Result |
| --- | --- | --- | --- | --- |
| C1 | All cheats | Keys 1–8 during play | Each shows its message; the effect is visible (HUD, lives, timer, ghosts) | |
| C2 | F-keys | F1–F8 (with Fn if needed) | Same effects as 1–8 | |

## Tooling and packaging

| ID | Test | Steps | Expected | Result |
| --- | --- | --- | --- | --- |
| T1 | Lint | `make lint` | No flake8 or mypy errors | ✅ |
| T2 | Unit tests | `make test` | All tests pass | ✅ |
| T3 | Clean | `make clean` | Caches and build output removed | ✅ |
| T4 | Build | `make package` | `dist/PacMan` created | ✅ |
| T5 | Packaged game | Launch `dist/PacMan` with no argument | Game starts; highscores saved next to the executable | ✅ |
| T6 | itch.io | Download and run from the itch.io page | Same as T5 | ✅ |

## Bugs found and fixed

| ID | Found (date) | Description | Cause | Fix | Fixed (date) | Test added |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | 2026-10-28 | Window shrank a little at every level change | Window size read after `set_mode()` | Cache the desktop size once | 2026-10-30 | `tests/test_level_window_resize.py` |
| B2 | 2026-11-05 | Cheats on F1–F7 triggered brightness/volume | Laptop and lab keyboards send media keys without Fn | Number keys 1–8 added | 2026-11-05 | `test_number_keys_mirror_function_keys` |
| B3 | 2026-11-05 | Number keys ignored on the Ubuntu lab machines | Input method (IBus) consumed key presses while SDL text input was on | Text input enabled only during name entry | 2026-11-05 | Manual (real X11 key events) |
| B4 | 2026-11-05 | Cheat keys and WASD not working on AZERTY | Key codes differ between layouts | Match physical key positions (scancodes) | 2026-11-07 | `test_cheats_use_physical_number_row`, `test_wasd_uses_physical_positions` |
| B5 | 2026-11-06 | Even maze sizes (e.g. 20×20) quit at start | The exact center tile is always a wall for even sizes | Spawn on the nearest open tile | 2026-11-07 | `tests/test_maze_adapter.py` |
| B6 | 2026-11-07 | Large mazes slow (about 25 fps at 100×100) | Every tile redrawn every frame | Cached maze image; size limit 60 | 2026-11-07 | Manual timing |
| B7 | 2026-11-07 | Packaged build could not start | Wrong module name and missing `src` path in `pacman.spec` | Spec fixed; no-argument launch | 2026-11-08 | Manual (T4, T5) |

TODO: add any other bug found during your own testing.
