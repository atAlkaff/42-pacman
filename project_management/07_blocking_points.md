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
- **Time lost:** 2 days

### BP2 – Even maze sizes crashed the game

- **When:** found 2026-11-05, before the defense.
- **Impact:** a reviewer changing the maze width to 20 would have seen the
  game quit immediately.
- **Resolution:** the player spawns on the open tile nearest the center;
  tests now cover many sizes.
  
## Lessons learned

- Test on the lab machines early;
- Check the config edge cases the reviewer can change;
- Keep the docs updated during the project instead of at the end.
