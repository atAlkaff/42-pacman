# Blocking Points and Conflicts

Problems that stopped or slowed the project, and disagreements inside the
team, with how each was resolved.

## Technical blocking points

### BP1 – Cheat keys did not work on the lab computers

- **When:** 2026-11-05
- **Impact:** the cheat mode, required for the peer review, appeared broken.
- **Investigation:** keys were sent through the real game loop in a test
  run; then a debug mode (`PACMAN_DEBUG_KEYS=1`) logged every key event.
- **Causes found:** F1–F7 send media keys on lab keyboards; on Ubuntu, the
  input method (IBus) can consume key presses while SDL text input is on.
- **Resolution:** cheats on number keys and keypad as well; matching by
  physical key position; text input enabled only during name entry.
- **Time lost:** TODO

### BP2 – Even maze sizes crashed the game

- **When:** found 2026-11-05, before the defense.
- **Impact:** a reviewer changing the maze width to 20 would have seen the
  game quit immediately.
- **Resolution:** the player spawns on the open tile nearest the center;
  tests now cover many sizes.

### BP3 – TODO

TODO: add other technical blocking points (for example obtaining the
assigned maze package, its interface, environment or uv problems).

## Team conflicts and disagreements

| Date | Topic | Positions | How it was resolved |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

TODO: if there were no conflicts, say how you avoided them (for example
clear ownership of modules and reviews through pull requests).

## Lessons learned

TODO: 3–5 points. For example: test on the lab machines early; check the
config edge cases the reviewer can change; keep the docs updated during
the project instead of at the end.
