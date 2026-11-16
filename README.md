*This project has been created as part of the 42 curriculum by abalfagi, aalkaff.*

# Pac-Man — Ghosts! More Ghosts!

A configurable Pac-Man game written in Python with Pygame, built for the 42 curriculum. It uses an externally supplied **A-Maze-ing** generator, ten or more levels, four autonomous ghosts, persistent highscores, and evaluation-friendly cheat controls.

## Description

The goal is to guide Pac-Man through a generated maze, collect every pacgum and super-pacgum, avoid dangerous ghosts, and finish all configured levels before running out of lives or time. Power pellets temporarily make the ghosts edible. The game keeps the player's score and remaining lives between levels, then offers name entry for the highscore table after victory or defeat.

The project emphasizes object-oriented design, modular components, configurable behavior, defensive input handling, pathfinding, graphical rendering, and reproducible testing.

**Gameplay flow:** Main Menu → Play → Victory or Game Over → Enter name / save score → Main Menu.

## Features

- At least **10 playable levels**, with configurable maze dimensions and individual time limits.
- A fixed-seed first level and generated mazes for later levels.
- Pac-Man movement in four directions using arrow keys or WASD; walls and maze boundaries block movement.
- Small pacgums, four corner super-pacgums, scoring, and temporary power mode.
- **Four ghosts**, each with a different pursuit probability: **100%, 85%, 70%, and 50%**.
- Ghost pursuit and escape decisions based on breadth-first-search (BFS) path distances, with no reverse turn unless forced.
- Collision handling after individual player/ghost steps; lives, respawn, a short **READY!** pause, and edible-ghost scoring.
- Score and remaining lives preserved during level transitions; a pause menu and level-specific countdown timers.
- Main menu, instructions, highscore table, game-over and victory screens, and an always-visible gameplay HUD.
- Persistent **Top 10** highscores saved as JSON, with validated names and graceful handling of corrupt files.
- Eight reviewer-friendly cheats, with on-screen feedback and support for keyboard layouts using physical key positions.
- Responsive maze/window sizing and cached maze rendering for smoother performance on larger levels.
- A PyInstaller build specification for distributing a standalone executable.

## Instructions

### Requirements

- **Python 3.12 or newer** (the current `pyproject.toml` requirement).
- A graphical desktop session capable of opening a Pygame/SDL window.
- [`uv`](https://docs.astral.sh/uv/) for dependency installation and the Makefile commands.
- `make` when using the Makefile shortcuts.

The project uses **Pygame**, **Pydantic**, and the provided `mazegenerator` wheel. The external wheel `mazegenerator-2.1.0-py3-none-any.whl` is included in the repository and is installed without modifying its source.

### Clone and install

```bash
git clone https://github.com/atAlkaff/42-pacman.git
cd 42-pacman
make install
```

`make install` runs `uv sync`, which resolves the dependencies specified in `pyproject.toml` and `uv.lock`.

### Run from source

```bash
make run
```

Equivalent explicit command:

```bash
uv run python pac-man.py config.json
```

The source entry point accepts **exactly one command-line argument**: a configuration JSON filename. For example:

```bash
uv run python pac-man.py my-config.json
```

When dependencies are installed in the active Python environment, the subject's direct command is also supported:

```bash
python3 pac-man.py config.json
```

The source program reports argument and configuration problems through logging rather than presenting an unhandled Python traceback.

### Makefile commands

| Command | Purpose |
| --- | --- |
| `make install` | Install/synchronize dependencies with `uv sync`. |
| `make run` | Start the game with `config.json`. |
| `make debug` | Run the entry point under Python's `pdb`. |
| `make clean` | Remove build output and common Python caches. |
| `make lint` | Run Flake8 and Mypy with the project-required flags. |
| `make lint-strict` | Run Flake8 and Mypy with `--strict`. |
| `make test` | Discover and run the `unittest` test suite. |
| `make package` | Build the standalone executable with PyInstaller. |

### Package and launch a standalone game

```bash
make package
```

The `pacman.spec` file produces a single executable named **`PacMan`** in `dist/` (or `PacMan.exe` when built on Windows). For example, on Linux:

```bash
./dist/PacMan
```

Unlike the source script, the **packaged executable can be launched without a command-line argument**. It uses an editable `config.json` located next to the executable, if one exists; otherwise, it uses the bundled configuration. Highscores from the packaged game are saved next to the executable rather than in the temporary extraction directory.

PyInstaller builds are **operating-system-specific**: produce the Windows build on Windows, and the Linux build on Linux. The packaged build is intended for distribution through an unlisted/free listing on a public game platform such as itch.io. The actual game-platform URL should be added to the repository once the upload is completed and verified.

### Controls

| Context | Input | Action |
| --- | --- | --- |
| Main menu | `↑` / `↓` or `W` / `S` | Move between menu options. |
| Main menu | `Enter` or `Space` | Select the highlighted option. |
| Main menu | `Esc` | Exit. |
| Gameplay | `↑` `↓` `←` `→` or `W` `A` `S` `D` | Move Pac-Man. |
| Gameplay | `Esc` | Pause. |
| Pause menu | `↑` / `↓` or `W` / `S` | Select Resume or Main Menu. |
| Pause menu | `Enter` or `Space` | Activate the selected option. |
| Pause menu | `Esc` | Resume. |
| Instructions / highscores | `Esc` or `Enter` | Return to the main menu. |
| Name entry | Letters, numbers, spaces | Enter a player name (up to 10 characters). |
| Name entry | `Backspace` | Delete the last character. |
| Name entry | `Enter` | Save the score and return to the menu. |
| Name entry | `Esc` | Skip saving and return to the menu. |

Menu navigation and gameplay movement use key codes and physical-key handling where appropriate, improving compatibility across different keyboard layouts. SDL text input is enabled only during name entry so desktop input methods do not interfere with gameplay keys.

### Cheat mode (for peer evaluation)

Press the **number key `1`–`8`**, the corresponding **`F1`–`F8`** key, or the matching numeric keypad key while playing. Function keys may require `Fn` on some laptops.

| Key | Cheat | Effect |
| --- | --- | --- |
| `1` / `F1` | Invincibility | Toggle protection from dangerous-ghost collisions. |
| `2` / `F2` | Skip level | Immediately advance to the next level or victory. |
| `3` / `F3` | Freeze ghosts | Toggle ghost movement on/off. |
| `4` / `F4` | Extra life | Add one life (up to the internal cap). |
| `5` / `F5` | Speed boost | Toggle double movement speed. |
| `6` / `F6` | Power mode | Make active ghosts edible temporarily. |
| `7` / `F7` | Add time | Add 60 seconds to the current level. |
| `8` / `F8` | Test time-out | Reduce the timer to at most five seconds. |

An on-screen message confirms each activation; persistent cheats are also identified in the HUD. These controls help reviewers test level progression, scoring, ghost collisions, and timeout behavior without completing every large maze manually.

## Configuration

Configuration is loaded from the file passed to `pac-man.py` and validated with Pydantic. It follows JSON syntax but also accepts **whole-line comments beginning with `#` or `//`**. Unrecognized keys are ignored. Missing, malformed, or out-of-range values produce a warning and a safe default or clamped value wherever possible.

### Game settings and defaults

| Key | Default | Description |
| --- | --- | --- |
| `highscore_filename` | `"highscores.json"` | JSON file used to load and persist the best scores. |
| `lives` | `3` | Initial player lives (minimum 1). |
| `points_per_pacgum` | `10` | Points awarded for a small pacgum. |
| `points_per_super_pacgum` | `50` | Points awarded for a super-pacgum. |
| `points_per_ghost` | `200` | Points awarded when eating an edible ghost. |
| `seed` | `42` | Fixed seed used for the first level. |
| `level_max_time` | `90` | Fallback time in seconds if a level has no `time_limit`. |
| `level` | Ten level entries | Ordered list of maze sizes and optional level time limits. |

Each level entry accepts:

| Key | Default | Description |
| --- | --- | --- |
| `width` | `21` | Source maze width, clamped to 3–60 cells. |
| `height` | `21` | Source maze height, clamped to 3–60 cells. |
| `time_limit` | `null` | Optional countdown in seconds (minimum 10); `null` uses `level_max_time`. |

If fewer than ten levels are provided, the parser repeats the configured level entries until it has ten. If the level list is missing or unusable, a safe ten-level sequence is generated. The existing `config.json` cycles through the following sizes and time limits:

| Levels | Source maze size | Time per level |
| --- | --- | --- |
| 1, 4, 7, 10 | 21 × 21 | 420 s (7 min) |
| 2, 5, 8 | 25 × 25 | 600 s (10 min) |
| 3, 6, 9 | 29 × 29 | 780 s (13 min) |

**Example commented configuration:**

```jsonc
# Pac-Man settings: whole-line # and // comments are accepted.
{
  "highscore_filename": "highscores.json",
  "lives": 3,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "seed": 42,
  "level_max_time": 90,
  "level": [
    {"width": 21, "height": 21, "time_limit": 420},
    {"width": 25, "height": 25, "time_limit": 600},
    {"width": 29, "height": 29, "time_limit": 780}
  ]
}
```

This abbreviated example is valid: the parser pads the level list to ten. See the repository's [`config.json`](./config.json) for the complete ten-level configuration. The rendered tile grid has dimensions **`(2 × width + 1) × (2 × height + 1)`**, so a source maze of 21 × 21 corresponds to 43 × 43 display tiles.

## Highscore

The `HighscoreSystem` class stores scores in the JSON file selected by `highscore_filename`. A JSON array of objects was chosen because it is **portable, human-readable, easy to inspect during a review, and does not require a separate database**.

Each record contains a player name and a non-negative integer score:

```json
[
  {"name": "PLAYER1", "score": 1250},
  {"name": "PLAYER2", "score": 900}
]
```

The system:

1. Loads the stored highscore file at startup, or starts with an empty list when it does not exist.
2. Accepts names made from ASCII letters (`A–Z`, `a–z`), digits, and spaces, with a maximum of **10 characters**. Empty/invalid names are normalized to `UNKNOWN`.
3. Rejects invalid scores and ignores malformed file entries with logging instead of crashing.
4. Sorts valid scores from highest to lowest and retains only the **top 10**. When scores tie, existing entries retain their relative order.
5. Lets the player enter a name after **Victory** or **Game Over**, then writes the updated table to JSON.
6. Displays a highscore preview on the main menu and the top-ten table in the Highscores screen.

When the game is packaged, the highscore path is resolved relative to the executable so results persist across launches.

## Maze Generation

Mazes are supplied by the assigned third-party **A-Maze-ing** Python package, installed from the provided wheel. The project **does not modify or reimplement** the external generator.

`MazeAdapter` provides the integration layer:

1. Calls `MazeGenerator(size=(width, height), perfect=False, seed=seed)`.
2. Checks the returned grid shape, directional wall-mask values, and consistency of shared walls.
3. Expands the source maze's directional wall representation into explicit wall and corridor tiles for the game.
4. Selects the closest open tile to the center as Pac-Man's spawn, including for even-sized source mazes.
5. Checks corridor reachability so the player can reach the corner power pellets and all retained collectibles.
6. Places small pacgums on reachable corridors and one super-pacgum in each of the four corners.
7. Surfaces generator failures clearly; later randomly generated levels can be retried when a candidate maze is unusable.

The **first level uses the configured fixed seed** to support reproducible behavior, while later levels use generated variations. Because the maze adapter is separate from the game engine, the assigned generator can be reinstalled for peer evaluation without changing the game logic.

## Implementation

### Player, scoring, and level progression

The player occupies a tile coordinate `(row, column)`. Each valid key press moves one tile, and holding a direction repeats moves at a timed interval. The maze model blocks wall and out-of-range moves. On entering a collectible tile, the item is removed and its configured score is awarded **only once**.

Collecting a super-pacgum awards its points and activates power mode for approximately **six seconds**. The player progresses when all collectibles are gone, carrying the current score and remaining lives into the next configured level. Completing the final level causes Victory. Running out of lives **or time** results in Game Over. The countdown stops while paused and during the brief respawn pause.

### Ghost AI and collisions

Each ghost has its own movement timer and a probability of choosing the best route. A BFS from Pac-Man's current position computes shortest walking distances along actual corridors. This distance map is cached until Pac-Man changes tile, then shared by the four ghosts:

- Dangerous ghosts prefer tiles **closer** to Pac-Man.
- Edible ghosts prefer tiles **farther** from Pac-Man.
- Ghosts avoid immediately reversing direction unless there is no alternative.
- Ghosts choose the best move with probabilities **100%, 85%, 70%, and 50%**, making some more predictable than others.
- Ghosts move more slowly while edible, allowing the player to catch them.

Collisions are checked after **every player or ghost tile step**. A dangerous ghost removes one life unless invincibility is active. The player and ghosts reset, followed by a short **READY!** pause of approximately **1.5 seconds**. When Pac-Man touches an edible ghost, the player gains the configured ghost score; that ghost returns to its original corner, stays out of play for approximately **five seconds**, then becomes dangerous again.

### Graphics and performance

`PygameRenderer` draws the maze, entities, menus, overlays, and messages. `HUD` displays score, remaining lives, level, time, and active cheats. The renderer caches the desktop display dimensions to avoid progressively shrinking windows during level changes. It also caches the rendered maze surface and erases only newly consumed pellets between frames, instead of redrawing all walls each frame.

### Defensive behavior

The configuration parser validates settings independently and substitutes defaults for invalid values. The maze adapter rejects inconsistent or unusable external generator output. The highscore loader tolerates missing or unreadable files and ignores malformed records. Game startup logs errors cleanly. Keyboard text-input handling is restricted to name-entry screens to avoid interfering with gameplay controls.

## General Software Architecture

The project uses a modular **model–view–controller (MVC)-inspired** structure, with separate utility components for configuration, maze integration, highscore persistence, and cheats.

```text
pac-man.py (CLI entry point)
    |
    +--> utils/config_parser.py ------> GameConfig / LevelConfig
    |
    +--> controllers/game_engine.py --> game loop, state transitions,
    |       |                          input, movement, collisions, AI,
    |       |                          scoring and level timers
    |       |
    |       +--> models/maze_state.py -> grid, collectibles, BFS distances
    |       +--> models/entities.py ---> Player and Ghost objects
    |       +--> controllers/cheat_manager.py
    |       +--> utils/highscore_system.py -> persistent JSON scores
    |       +--> utils/maze_adapter.py ----> assigned A-Maze-ing package
    |       |
    |       +--> views/pygame_renderer.py -> pygame rendering and menus
    |       +--> views/hud.py -----------> score / lives / level / time
    |
    +--> config.json -------------------> configurable game parameters
```

| Layer / module | Main responsibility |
| --- | --- |
| `pac-man.py` | Validate CLI usage, resolve packaged-file paths, and initialize the application. |
| `GameEngine` | Central state machine and main loop; input, progression, ghost movement, collisions, score updates, and timer control. |
| `Player`, `Ghost` | Entity coordinates, lives, score, ghost behavior, edible status, and respawn state. |
| `MazeState` | Playable tile grid, wall checks, collected items, level completion, and BFS distance map. |
| `MazeAdapter` | Convert and validate third-party A-Maze-ing output; choose spawn positions and place collectibles. |
| `GameConfig`, `LevelConfig` | Parse commented JSON and safely validate per-game and per-level settings. |
| `HighscoreSystem` | Load, validate, sort, and persist the ten highest scores. |
| `CheatManager` | Track persistent review cheats (invincibility, freeze, speed boost). |
| `PygameRenderer`, `HUD` | Window sizing, graphical entities and menus, overlays, and status display. |

## Testing and Quality Assurance

The repository includes Python `unittest` cases under [`tests/`](./tests/). The tests cover core behaviors such as movement, scoring, collectible consumption, and window resizing; the project should also be checked with integrated ghost, highscore, menu, and packaging scenarios during final evaluation.

Run the test suite:

```bash
make test
```

Run the required style and type checks:

```bash
make lint
```

The lint target executes the project's Flake8 and Mypy checks. The repository also contains `make lint-strict` for an optional stricter Mypy pass. Because the examiner may edit configuration values, useful manual review scenarios include missing or malformed configuration, minimum/maximum maze dimensions, fewer than ten levels, unreadable highscores, all eight cheats, and a clean launch of the packaged build without arguments.

## Project Management

Work was divided into coordinated milestones and tracked through the shared Git repository. The two contributors developed the base gameplay and the remaining game systems, then integrated and tested them together.

- **Afnan Balfagieh (`abalfagi`)**: external maze adapter, configuration parsing, player movement, pacgum collection and scoring, level progression, per-level timers, pause behavior, window-resizing fixes, and associated tests.
- **Ahmed Alkaff (`aalkaff`)**: ghost pathfinding and personalities, collisions and respawn, menus, name entry, highscore persistence, cheat features, maze spawn fix, rendering performance improvements, and packaging.
- **Shared work**: repository integration, code review, quality checks, gameplay verification, and peer-review preparation.

The project encountered and addressed keyboard-layout input problems, level-window resizing, invalid external/configuration data, even-sized maze spawn positions, and large-maze rendering performance.

See the dedicated [project management documentation](./project_management/) for the development stages, responsibilities, decisions, risks, and acceptance-test records. Project-management documents should be kept up to date with actual evidence before submission.

## Resources

### References and documentation

- [42 Pac-Man project subject](./PacMan.subject.pdf) — specification and evaluation requirements.
- [Python 3 documentation](https://docs.python.org/3/) — Python language and standard-library behavior.
- [Pygame documentation](https://www.pygame.org/docs/) — event handling, display, drawing, and keyboard controls.
- [Pydantic documentation](https://docs.pydantic.dev/latest/) — configuration models and validation.
- [Python `collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) — queue used by breadth-first search.
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) — unweighted shortest-path algorithm background.
- [`uv` documentation](https://docs.astral.sh/uv/) — dependency management and reproducible development environments.
- [PyInstaller documentation](https://pyinstaller.org/en/stable/) — executable packaging.
- [PEP 8](https://peps.python.org/pep-0008/) and [PEP 257](https://peps.python.org/pep-0257/) — coding style and docstring conventions.
- The supplied `mazegenerator-2.1.0-py3-none-any.whl` — assigned third-party maze-generation dependency, used as provided.

### AI assistance disclosure

ChatGPT was used as a development **assistance tool**, including explaining project requirements, discussing module design, suggesting or refining code and tests, troubleshooting movement/keyboard and display-resizing issues, reviewing lint/type-check commands, and drafting project documentation. Some implementation and test snippets were AI-assisted; the contributors remained responsible for selecting, understanding, adapting, and validating the code in their own project environment. AI was **not** used as the external maze generator: the assigned A-Maze-ing package is the maze source.

## Contributors

- **Afnan Balfagieh** — 42 login: `abalfagi`
- **Ahmed Alkaff** — 42 login: `aalkaff`

Repository: <https://github.com/atAlkaff/42-pacman>
