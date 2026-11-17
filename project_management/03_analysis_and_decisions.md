# Project Analysis and Decisions

## 1. Analysis of the subject

TODO: a short summary, in your own words, of what the subject requires and
what you judged to be the hardest parts at the start. Suggested points:

- Using another group's maze package without modifying it.
- Never crashing, even when the reviewer edits the config during the defense.
- Ghost behaviour that is interesting but simple to explain.
- Packaging for a public game platform.

## 2. Decision log

One entry per significant decision. The reasons recorded below are the
ones given when each change was made. Fill in `Decided by` and `Date`, and
correct anything that does not match how your team decided.

### D1 – Pygame for graphics

- **Context:** the subject asks for "MLX or similar".
- **Decision:** Pygame.
- **Why:** TODO
- **Alternatives considered:** TODO
- **Decided by / date:** TODO

### D2 – Pydantic to validate the configuration

- **Context:** invalid values must be clamped or replaced by defaults with a
  clear message, and unknown keys ignored.
- **Decision:** one Pydantic model per game and per level. Each key is
  validated separately, so one bad value does not discard the whole file.
- **Why:** declarative ranges and defaults; less hand-written checking code.
- **Decided by / date:** TODO

### D3 – Model–view–controller structure

- **Decision:** models (`Player`, `Ghost`, `MazeState`) hold state only,
  views only draw, and `GameEngine` connects input, rules, and drawing.
- **Why:** game rules can be unit-tested without opening a window.
- **Decided by / date:** TODO

### D4 – Ghost AI: BFS walking distance plus a per-ghost chase probability

- **Decision:** a breadth-first search from the player gives the walking
  distance to every tile. Each ghost takes the best move with probability
  100 / 85 / 70 / 50 %, otherwise a random move, and never reverses unless
  it is forced to.
- **Why:** straight-line (Euclidean) distance sent ghosts into walls; BFS
  follows the real corridors. The probabilities give four personalities
  with one simple rule.
- **Alternatives considered:** Euclidean distance (the first version); the
  four distinct arcade targeting rules (more complex to explain).
- **Decided by / date:** TODO

### D5 – Collisions checked after every single tile step

- **Decision:** everything moves one tile at a time, and collisions are
  checked after each step of the player or of any ghost.
- **Why:** a player and a ghost can never pass through each other, so no
  extra "swap" detection is needed.
- **Decided by / date:** TODO

### D6 – Eaten ghosts return dangerous (arcade behaviour)

- **Context:** a ghost eaten early in power mode returns while the others
  are still edible. This was first reported as a bug.
- **Decision:** keep the arcade behaviour, and explain it on the
  Instructions screen.
- **Alternative considered:** the returning ghost rejoins power mode for
  the time left.
- **Decided by / date:** TODO

### D7 – Running out of time ends the game

- **Context:** the subject leaves this choice to us.
- **Decision:** game over, followed by name entry.
- **Why:** TODO
- **Decided by / date:** TODO

### D8 – Maze sizes clamped to 3–60; fewer than 10 levels are padded

- **Decision:** out-of-range sizes are clamped with a warning; a level list
  shorter than 10 is filled by repeating the configured levels.
- **Why:** above 60 the tiles are too small to play on a 1080p screen; the
  subject requires at least 10 levels.
- **Decided by / date:** TODO

### D9 – Cheats on number keys 1–8 as well as F1–F8

- **Context:** on lab keyboards F1–F8 control brightness and volume unless
  Fn is held.
- **Decision:** number row, keypad, and function keys all work, matched by
  physical key position so other keyboard layouts (such as AZERTY) work too.
- **Decided by / date:** TODO

### D10 – Packaged build starts without a command-line argument

- **Context:** a game platform launches the game without arguments.
- **Decision:** the packaged build only uses the `config.json` next to the
  executable (or the bundled copy) and saves highscores next to the
  executable. Running from source still requires exactly one argument.
- **Decided by / date:** TODO

TODO: add any other decision your team made (for example the highscore
file format, uv as the package manager, the choice of itch.io).
