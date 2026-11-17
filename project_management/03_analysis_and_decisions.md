# Project Analysis and Decisions

## 1. Analysis of the subject

The subject asks for a complete, playable Pac-Man game in Python, built with object-oriented code and a modular architecture, and published on a public game platform. Beyond the gameplay itself, it sets strict quality rules: the program takes exactly one configuration file, must never crash or show a traceback, and must pass flake8 and mypy. The configuration is commented JSON that the reviewer will change during the defense, so every value can be missing or invalid. We therefore treated robustness as a feature in its own right, as important as the gameplay.

We identified three main difficulties at the start. First, the mazes must come from another group’s A-Maze-ing package, used without changes, so we could not control its format or its bugs. We needed an adapter layer that converts its wall data into our tile grid and checks everything it returns. Second, the ghosts had to chase and flee convincingly while staying simple enough to explain at the defense. Third, the game had to work on machines we did not control: the lab computers, a reviewer’s keyboard layout, and the game platform’s launcher.

These points shaped how we split the work and in which order we built it. The configuration parser and maze adapter came first, because every other part depends on them. Gameplay, the menus and highscores came next, and packaging and documentation last. We separated game state, drawing and control into different modules, so that most of the rules could be tested automatically without opening a window. Running out of time and the behaviour of eaten ghosts were left to us by the subject; we chose game over and the arcade rule, as recorded in the decision log below.

## 2. Decision log

### D1 – Pygame for graphics

- **Context:** the subject asks for "MLX or similar".
- **Decision:** Pygame
- **Why:** Simplicity and large developer ecosystem
- **Alternatives considered:** MLX, Pyglet, Raylib
- **Decided by / date:** aalkaff, 2026-10-14

### D2 – Pydantic to validate the configuration

- **Context:** invalid values must be clamped or replaced by defaults with a
  clear message, and unknown keys ignored.
- **Decision:** one Pydantic model per game and per level. Each key is
  validated separately, so one bad value does not discard the whole file.
- **Why:** declarative ranges and defaults; less hand-written checking code.
- **Decided by / date:** aalkaff, 2026-10-14

### D3 – Model–view–controller structure

- **Decision:** models (`Player`, `Ghost`, `MazeState`) hold state only,
  views only draw, and `GameEngine` connects input, rules, and drawing.
- **Why:** game rules can be unit-tested without opening a window.
- **Decided by / date:** aalkaff, 2026-10-16

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
- **Decided by / date:** aalkaff, 2026-11-04

### D5 – Collisions checked after every single tile step

- **Decision:** everything moves one tile at a time, and collisions are
  checked after each step of the player or of any ghost.
- **Why:** a player and a ghost can never pass through each other, so no
  extra "swap" detection is needed.
- **Decided by / date:** aalkaff, 2026-11-04

### D6 – Eaten ghosts return dangerous (arcade behaviour)

- **Context:** a ghost eaten early in power mode returns while the others
  are still edible. This was first reported as a bug.
- **Decision:** keep the arcade behaviour, and explain it on the
  Instructions screen.
- **Alternative considered:** the returning ghost rejoins power mode for
  the time left.
- **Decided by / date:** abalfagi, 2026-10-28

### D7 – Running out of time ends the game

- **Context:** the subject leaves this choice to us.
- **Decision:** game over, followed by name entry.
- **Why:** although not used in the original 1980 game, time limits have historically been used in Pacman games.
- **Decided by / date:** abalfagi, 2026-10-26

### D8 – Maze sizes clamped to 3–60; fewer than 10 levels are padded

- **Decision:** out-of-range sizes are clamped with a warning; a level list
  shorter than 10 is filled by repeating the configured levels.
- **Why:** above 60 the tiles are too small to play on a 1080p screen; the
  subject requires at least 10 levels.
- **Decided by / date:** aalkaff, 2026-11-08

### D9 – Cheats on number keys 1–8 as well as F1–F8

- **Context:** on lab keyboards F1–F8 control brightness and volume unless
  Fn is held.
- **Decision:** number row, keypad, and function keys all work, matched by
  physical key position so other keyboard layouts (such as AZERTY) work too.
- **Decided by / date:** aalkaff, 2026-11-07


