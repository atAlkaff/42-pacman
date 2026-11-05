"""Coordinate Pac-Man game states, levels, and rendering."""

import logging
import os
import random
from typing import List

import pygame

from controllers.cheat_manager import CheatManager
from models.entities import Ghost, Player
from models.maze_state import MazeState
from utils.config_parser import GameConfig
from utils.highscore_system import HighscoreSystem
from utils.maze_adapter import MazeAdapter
from views.hud import HUD
from views.pygame_renderer import PygameRenderer


class GameEngine:
    """Control the game loop and move between configured levels."""

    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    STATE_GAME_OVER = 3
    STATE_VICTORY = 4
    STATE_HIGHSCORES = 5
    STATE_INSTRUCTIONS = 6

    MENU_START = "Start Game"
    MENU_HIGHSCORES = "Highscores"
    MENU_INSTRUCTIONS = "Instructions"
    MENU_EXIT = "Exit"
    MENU_ITEMS = (MENU_START, MENU_HIGHSCORES, MENU_INSTRUCTIONS, MENU_EXIT)

    PAUSE_RESUME = "Resume"
    PAUSE_MAIN_MENU = "Main Menu"
    PAUSE_ITEMS = (PAUSE_RESUME, PAUSE_MAIN_MENU)

    # Number of highscores listed directly on the main menu.
    MENU_HIGHSCORE_PREVIEW = 5

    CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
    MENU_UP_KEYS = (pygame.K_UP, pygame.K_w)
    MENU_DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)

    INSTRUCTIONS = (
        "Eat every pacgum to clear the level.",
        "Big super-pacgums make ghosts edible for a short time.",
        "Eaten ghosts return to their corner and come back dangerous.",
        "A ghost touching you costs a life. Clear all levels to win.",
        "",
        "Move: arrow keys or WASD      Pause: ESC",
        "Menus: arrows/WS + ENTER      Back: ESC",
        "",
        "Cheats (for review): number keys 1-8 or F1-F8",
        "1 invincible    2 skip level    3 freeze ghosts",
        "4 extra life    5 speed boost    6 power mode",
        "7 add 60 seconds    8 test time-out (timer to 5 s)",
    )

    # Seconds between grid steps. Ghosts are a little slower than the
    # player, and slower still while edible, so they can be caught.
    PLAYER_MOVE_INTERVAL = 0.12
    GHOST_MOVE_INTERVAL = 0.16
    GHOST_EDIBLE_MOVE_INTERVAL = 0.28
    POWER_MODE_DURATION = 6.0
    GHOST_RESPAWN_DELAY = 5.0
    # Short "READY!" pause after losing a life.
    RESPAWN_PAUSE = 1.5
    # How often each ghost takes the smartest move (one per corner).
    # 1.0 always chases; lower values wander more.
    GHOST_CHASE_CHANCES = (1.0, 0.85, 0.7, 0.5)
    # Random mazes that fail validation are regenerated this many times.
    MAZE_ATTEMPTS = 5
    # Each cheat works with a number key, a keypad digit, and a function
    # key. Laptops often send brightness/volume for F1-F8 unless Fn is
    # held, so the number row is the reliable choice there.
    CHEAT_INVINCIBLE = "invincible"
    CHEAT_SKIP_LEVEL = "skip_level"
    CHEAT_FREEZE = "freeze"
    CHEAT_EXTRA_LIFE = "extra_life"
    CHEAT_SPEED = "speed"
    CHEAT_POWER = "power"
    CHEAT_ADD_TIME = "add_time"
    CHEAT_LOW_TIME = "low_time"
    CHEAT_KEYS: dict[int, str] = {
        pygame.K_1: CHEAT_INVINCIBLE, pygame.K_F1: CHEAT_INVINCIBLE,
        pygame.K_2: CHEAT_SKIP_LEVEL, pygame.K_F2: CHEAT_SKIP_LEVEL,
        pygame.K_3: CHEAT_FREEZE, pygame.K_F3: CHEAT_FREEZE,
        pygame.K_4: CHEAT_EXTRA_LIFE, pygame.K_F4: CHEAT_EXTRA_LIFE,
        pygame.K_5: CHEAT_SPEED, pygame.K_F5: CHEAT_SPEED,
        pygame.K_6: CHEAT_POWER, pygame.K_F6: CHEAT_POWER,
        pygame.K_7: CHEAT_ADD_TIME, pygame.K_F7: CHEAT_ADD_TIME,
        pygame.K_8: CHEAT_LOW_TIME, pygame.K_F8: CHEAT_LOW_TIME,
        pygame.K_KP1: CHEAT_INVINCIBLE, pygame.K_KP2: CHEAT_SKIP_LEVEL,
        pygame.K_KP3: CHEAT_FREEZE, pygame.K_KP4: CHEAT_EXTRA_LIFE,
        pygame.K_KP5: CHEAT_SPEED, pygame.K_KP6: CHEAT_POWER,
        pygame.K_KP7: CHEAT_ADD_TIME, pygame.K_KP8: CHEAT_LOW_TIME,
    }
    # Physical key positions (scancodes) of the number row. On AZERTY and
    # other layouts these keys type symbols such as '&' unless Shift is
    # held, so their key code is not K_1..K_8; the position is the same.
    CHEAT_SCANCODES: dict[int, str] = {
        pygame.KSCAN_1: CHEAT_INVINCIBLE,
        pygame.KSCAN_2: CHEAT_SKIP_LEVEL,
        pygame.KSCAN_3: CHEAT_FREEZE,
        pygame.KSCAN_4: CHEAT_EXTRA_LIFE,
        pygame.KSCAN_5: CHEAT_SPEED,
        pygame.KSCAN_6: CHEAT_POWER,
        pygame.KSCAN_7: CHEAT_ADD_TIME,
        pygame.KSCAN_8: CHEAT_LOW_TIME,
    }
    # Seconds a cheat confirmation stays on screen.
    TOAST_DURATION = 2.0
    # The speed cheat divides the player's step interval by this factor.
    SPEED_BOOST_FACTOR = 2.0
    # Seconds added by the add-time cheat.
    ADD_TIME_CHEAT = 60.0
    # Seconds left after the low-time cheat, which lets a reviewer check
    # the time-out (game over) without waiting for the whole level timer.
    LOW_TIME_CHEAT = 5.0
    MAX_LIVES = 99
    # Physical WASD positions map to the same directions, so the keys work
    # on layouts such as AZERTY where that position types Z, Q, S, D.
    MOVE_SCANCODES: dict[int, int] = {
        pygame.KSCAN_W: pygame.K_w,
        pygame.KSCAN_A: pygame.K_a,
        pygame.KSCAN_S: pygame.K_s,
        pygame.KSCAN_D: pygame.K_d,
    }
    # Short on-screen confirmation of the last cheat used.
    _toast_text: str = ""
    _toast_time: float = 0.0
    # Set PACMAN_DEBUG_KEYS=1 to log every keyboard event in the terminal.
    DEBUG_KEYS_ENV = "PACMAN_DEBUG_KEYS"
    _debug_keys: bool = False
    MOVE_KEYS: dict[int, tuple[int, int]] = {
        pygame.K_UP: (-1, 0),
        pygame.K_w: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_s: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_a: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_d: (0, 1),
    }

    def __init__(
        self,
        config: GameConfig,
        renderer: PygameRenderer,
        adapter: MazeAdapter,
    ) -> None:
        """Initialize game state without starting the game loop."""
        self.config = config
        self.renderer = renderer
        self.adapter = adapter
        self.hud = HUD(
            renderer.screen,
            renderer.height - renderer.HUD_HEIGHT,
            renderer.width,
        )
        self.cheat_manager = CheatManager()

        self.current_state = self.STATE_MENU
        self.level = 1
        self.time_left = float(config.level_max_time)
        self.clock = pygame.time.Clock()

        self.player: Player | None = None
        self.ghosts: List[Ghost] = []
        self.maze: MazeState | None = None

        # Pressing a direction moves once immediately. Holding it
        # repeats moves at a frame-rate-independent interval.
        self._held_move_keys: list[int] = []
        self._move_elapsed = 0.0

        # Ghost decisions use their own generator: the maze package reseeds
        # the global random module whenever a maze is generated.
        self._rng = random.Random()
        self._respawn_pause = 0.0

        # Loaded once at start-up; saved at the end of every game.
        self.highscores = HighscoreSystem(config.highscore_filename)
        self.menu_index = 0
        self.pause_index = 0
        self.name_input = ""
        self._running = True
        self._debug_keys = os.environ.get(self.DEBUG_KEYS_ENV, "") not in (
            "", "0"
        )

    def _init_level(self) -> None:
        """Initialize a configured level, preserving score and lives."""
        if not 1 <= self.level <= len(self.config.level):
            raise ValueError(f"Level {self.level} is not configured")

        level_settings = self.config.level[self.level - 1]
        seed = self.config.seed if self.level == 1 else 0

        # Keep the originally supplied generator backend, but use this
        # level's dimensions instead of fixed dimensions from level 1.
        self.adapter = MazeAdapter(
            width=level_settings.width,
            height=level_settings.height,
            backend=self.adapter.backend,
        )
        grid = self._generate_grid(seed)
        self.maze = MazeState(grid)

        # Resize for the new maze and bind the HUD to the new surface.
        self._refresh_level_display()

        current_score = self.player.score if self.player else 0
        current_lives = self.player.lives if self.player else self.config.lives

        center_r = self.maze.height // 2
        center_c = self.maze.width // 2
        self.player = Player(center_r, center_c, current_lives)
        self.player.score = current_score

        corners = (
            (1, 1),
            (1, self.maze.width - 2),
            (self.maze.height - 2, 1),
            (self.maze.height - 2, self.maze.width - 2),
        )
        self.ghosts = [
            Ghost(r, c, chance)
            for (r, c), chance in zip(corners, self.GHOST_CHASE_CHANCES)
        ]
        self._respawn_pause = 0.0
        self.time_left = float(
            level_settings.time_limit
            if level_settings.time_limit is not None
            else self.config.level_max_time
        )
        self._held_move_keys.clear()
        self._move_elapsed = 0.0

    def _generate_grid(self, seed: int) -> list[list[int]]:
        """Generate a level grid, retrying random mazes that are unusable.

        A fixed seed always yields the same maze, so it is tried once.

        Raises:
            ValueError: If no playable maze could be generated.
        """
        attempts = 1 if seed != 0 else self.MAZE_ATTEMPTS
        last_error: ValueError | None = None
        for attempt in range(1, attempts + 1):
            try:
                return self.adapter.generate_maze(seed=seed)
            except ValueError as exc:
                last_error = exc
                logging.warning(
                    "Maze generation attempt %d failed: %s", attempt, exc
                )
        raise ValueError(
            f"Could not generate a playable maze for level {self.level}: "
            f"{last_error}"
        )

    def _refresh_level_display(self) -> None:
        """Resize once per level and refresh the HUD display surface."""
        if self.maze is None:
            return

        self.renderer.resize_grid(self.maze.width, self.maze.height)
        self.hud = HUD(
            self.renderer.screen,
            self.renderer.height - self.renderer.HUD_HEIGHT,
            self.renderer.width,
        )

    def _advance_level(self) -> None:
        """Move to the next configured level or stop at victory."""
        if self.level >= len(self.config.level):
            self._end_game(self.STATE_VICTORY)
            return

        self.level += 1
        self._init_level()

    def _draw_play_field(self) -> None:
        """Draw the current level when player and maze are initialized."""
        if self.maze is None or self.player is None:
            return

        self.renderer.draw_maze(self.maze)
        self.renderer.draw_entities(self.player, self.ghosts)
        cheats = self.cheat_manager.active_labels()
        self.hud.draw(
            self.player.score,
            self.player.lives,
            self.level,
            max(0, int(self.time_left)),
            "  ".join(cheats),
        )

    def run(self) -> None:
        """Process events, update the game, and render each frame."""
        self._running = True
        # Keys go straight to the game; text input is only for name entry.
        self._set_text_input(False)
        while self._running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if self._debug_keys:
                    self._log_key_event(event)
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    self._handle_input(event)

            if not self._running:
                break

            if self.current_state == self.STATE_PLAYING:
                self._update_playing(dt)
            self._toast_time = max(0.0, self._toast_time - dt)

            self._draw()
            self.renderer.update_display()

    def _draw(self) -> None:
        """Render the screen that matches the current state."""
        self.renderer.clear_screen()
        state = self.current_state

        if state == self.STATE_PLAYING:
            self._draw_play_field()
            if self._toast_time > 0:
                self.renderer.draw_toast(self._toast_text)
            if self._respawn_pause > 0 and self.player is not None:
                self.renderer.draw_centered_message(
                    "READY!", f"Lives left: {self.player.lives}"
                )
        elif state == self.STATE_PAUSED:
            self._draw_play_field()
            self.renderer.draw_overlay()
            self.renderer.draw_menu(
                "PAUSED",
                self.PAUSE_ITEMS,
                self.pause_index,
                ("ESC to resume",),
            )
        elif state == self.STATE_MENU:
            lines = ["Highscores:"] + self._highscore_lines(
                self.MENU_HIGHSCORE_PREVIEW
            )
            self.renderer.draw_menu(
                "PAC-MAN", self.MENU_ITEMS, self.menu_index, lines
            )
        elif state == self.STATE_HIGHSCORES:
            self.renderer.draw_menu(
                "HIGHSCORES",
                lines=self._highscore_lines(HighscoreSystem.MAX_ENTRIES)
                + ["", "ESC or ENTER to go back"],
            )
        elif state == self.STATE_INSTRUCTIONS:
            self.renderer.draw_menu(
                "HOW TO PLAY",
                lines=self.INSTRUCTIONS + ("", "ESC or ENTER to go back"),
            )
        elif state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
            score = self.player.score if self.player else 0
            if state == self.STATE_VICTORY:
                title = "VICTORY!"
                message = "Congratulations, you cleared every level!"
            else:
                title = "GAME OVER"
                message = "Better luck next time."
            cursor = "_" if len(self.name_input) < (
                HighscoreSystem.MAX_NAME_LENGTH
            ) else ""
            self.renderer.draw_menu(
                title,
                lines=(
                    message,
                    f"Final score: {score}",
                    "",
                    "Enter your name for the highscores:",
                    f"[ {self.name_input}{cursor} ]",
                    "Letters, digits and spaces, max 10",
                    "",
                    "ENTER to save    ESC to skip",
                ),
            )

    def _highscore_lines(self, count: int) -> list[str]:
        """Format the best ``count`` highscores as numbered lines."""
        scores = self.highscores.top_scores()[:count]
        if not scores:
            return ["No highscores yet"]
        return [
            f"{rank}. {name} - {score} pts"
            for rank, (name, score) in enumerate(scores, start=1)
        ]

    def _handle_input(self, event: pygame.event.Event) -> None:
        """Send keyboard events to the handler of the current screen."""
        if event.type == pygame.KEYUP:
            # Release a held direction so Pac-Man stops moving.
            move_key = self._move_key(event)
            if move_key in self._held_move_keys:
                self._held_move_keys.remove(move_key)
            if not self._held_move_keys:
                self._move_elapsed = 0.0
            return

        if event.type == pygame.TEXTINPUT:
            if self.current_state in (
                self.STATE_GAME_OVER, self.STATE_VICTORY
            ):
                self._type_name(event.text)
            return

        if event.type != pygame.KEYDOWN:
            return

        state = self.current_state
        if state == self.STATE_MENU:
            self._handle_menu_key(event.key)
        elif state == self.STATE_PLAYING:
            self._handle_playing_key(event)
        elif state == self.STATE_PAUSED:
            self._handle_pause_key(event.key)
        elif state in (self.STATE_HIGHSCORES, self.STATE_INSTRUCTIONS):
            if event.key == pygame.K_ESCAPE or event.key in self.CONFIRM_KEYS:
                self.current_state = self.STATE_MENU
        elif state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
            self._handle_name_entry(event)

    def _handle_menu_key(self, key: int) -> None:
        """Navigate the main menu and run the chosen entry."""
        if key in self.MENU_UP_KEYS:
            self.menu_index = (self.menu_index - 1) % len(self.MENU_ITEMS)
        elif key in self.MENU_DOWN_KEYS:
            self.menu_index = (self.menu_index + 1) % len(self.MENU_ITEMS)
        elif key == pygame.K_ESCAPE:
            self._running = False
        elif key in self.CONFIRM_KEYS:
            choice = self.MENU_ITEMS[self.menu_index]
            if choice == self.MENU_START:
                self._start_new_game()
            elif choice == self.MENU_HIGHSCORES:
                self.current_state = self.STATE_HIGHSCORES
            elif choice == self.MENU_INSTRUCTIONS:
                self.current_state = self.STATE_INSTRUCTIONS
            elif choice == self.MENU_EXIT:
                self._running = False

    def _start_new_game(self) -> None:
        """Reset score, lives and level, then start level 1."""
        self.level = 1
        self.player = None  # A new game resets score and lives.
        self._init_level()
        self.current_state = self.STATE_PLAYING

    def _move_key(self, event: pygame.event.Event) -> int | None:
        """Return the MOVE_KEYS entry for this key event, if any.

        The key code is tried first (arrows, WASD as typed); otherwise the
        physical WASD position is used, whatever the keyboard layout.
        """
        if event.key in self.MOVE_KEYS:
            return int(event.key)
        return self.MOVE_SCANCODES.get(getattr(event, "scancode", -1))

    def _cheat_for(self, event: pygame.event.Event) -> str | None:
        """Return the cheat bound to this key event, if any."""
        if event.key in self.CHEAT_KEYS:
            return self.CHEAT_KEYS[event.key]
        return self.CHEAT_SCANCODES.get(getattr(event, "scancode", -1))

    def _handle_playing_key(self, event: pygame.event.Event) -> None:
        """Pause, cheats, and movement keys during a level."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.STATE_PAUSED
            self.pause_index = 0
            self._held_move_keys.clear()
            self._move_elapsed = 0.0
            return

        cheat = self._cheat_for(event)
        if cheat is not None:
            self._apply_cheat(cheat)
            return

        move_key = self._move_key(event)
        if move_key is not None and move_key not in self._held_move_keys:
            self._held_move_keys.append(move_key)
            self._move_player_one_tile()
            self._move_elapsed = 0.0

    def _notify(self, message: str) -> None:
        """Confirm a cheat on screen and in the terminal."""
        logging.info("Cheat: %s", message)
        self._toast_text = message
        self._toast_time = self.TOAST_DURATION

    @staticmethod
    def _on_off(active: bool) -> str:
        """Format a toggle state for messages."""
        return "ON" if active else "OFF"

    def _apply_cheat(self, cheat: str) -> None:
        """Run one cheat action (see CHEAT_KEYS for the key bindings)."""
        manager = self.cheat_manager
        if cheat == self.CHEAT_INVINCIBLE:
            manager.toggle_invincibility()
            self._notify(
                f"Invincibility {self._on_off(manager.invincibility_active)}"
            )
        elif cheat == self.CHEAT_SKIP_LEVEL:
            self._notify(f"Skipped level {self.level}")
            self._advance_level()
        elif cheat == self.CHEAT_FREEZE:
            manager.toggle_ghost_freeze()
            self._notify(
                f"Ghost freeze {self._on_off(manager.ghosts_frozen)}"
            )
        elif cheat == self.CHEAT_EXTRA_LIFE:
            if self.player is not None:
                self.player.lives = min(self.MAX_LIVES, self.player.lives + 1)
                self._notify(f"Extra life (lives: {self.player.lives})")
        elif cheat == self.CHEAT_SPEED:
            manager.toggle_speed_boost()
            self._notify(
                f"Speed boost {self._on_off(manager.speed_boost_active)}"
            )
        elif cheat == self.CHEAT_POWER:
            self._activate_power_mode()
            self._notify("Power mode: ghosts are edible")
        elif cheat == self.CHEAT_ADD_TIME:
            self.time_left += self.ADD_TIME_CHEAT
            self._notify(f"+{int(self.ADD_TIME_CHEAT)} seconds")
        elif cheat == self.CHEAT_LOW_TIME:
            self.time_left = min(self.time_left, self.LOW_TIME_CHEAT)
            self._notify(
                f"Time-out test: {int(self.LOW_TIME_CHEAT)} seconds left"
            )

    def _handle_pause_key(self, key: int) -> None:
        """Resume, or abandon the game and return to the main menu."""
        if key == pygame.K_ESCAPE:
            self.current_state = self.STATE_PLAYING
        elif key in self.MENU_UP_KEYS or key in self.MENU_DOWN_KEYS:
            self.pause_index = (self.pause_index + 1) % len(self.PAUSE_ITEMS)
        elif key in self.CONFIRM_KEYS:
            if self.PAUSE_ITEMS[self.pause_index] == self.PAUSE_RESUME:
                self.current_state = self.STATE_PLAYING
            else:
                self.current_state = self.STATE_MENU
                self.menu_index = 0

    @staticmethod
    def _set_text_input(enabled: bool) -> None:
        """Turn SDL text input (and the system input method) on or off.

        pygame enables text input by default, which sends ordinary keys
        through the desktop input method first (IBus on Ubuntu). The input
        method can keep a key press, and then the game never gets a KEYDOWN
        for keys like 1-8 or WASD. Text input is therefore only enabled
        while the player types a name.
        """
        try:
            if enabled:
                pygame.key.start_text_input()
            else:
                pygame.key.stop_text_input()
        except pygame.error:
            pass  # No display (e.g. in tests): nothing to configure.

    @staticmethod
    def _log_key_event(event: pygame.event.Event) -> None:
        """Print a keyboard event, to diagnose keys that seem ignored."""
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            logging.info(
                "%s key=%s (%d) scancode=%s unicode=%r",
                "KEYDOWN" if event.type == pygame.KEYDOWN else "KEYUP",
                pygame.key.name(event.key),
                event.key,
                getattr(event, "scancode", "?"),
                getattr(event, "unicode", ""),
            )
        elif event.type == pygame.TEXTINPUT:
            logging.info("TEXTINPUT text=%r", event.text)

    def _end_game(self, state: int) -> None:
        """Show the game-over or victory screen and start name entry."""
        self.current_state = state
        self.name_input = ""
        self._held_move_keys.clear()
        self._move_elapsed = 0.0
        self._set_text_input(True)

    def _leave_name_entry(self) -> None:
        """Return to the main menu and stop text input again."""
        self._set_text_input(False)
        self.current_state = self.STATE_MENU
        self.menu_index = 0

    def _handle_name_entry(self, event: pygame.event.Event) -> None:
        """Save the name with ENTER, skip with ESC, delete with BACKSPACE.

        The characters themselves arrive as TEXTINPUT events (see
        ``_type_name``), which also works with the system input method.
        """
        key = event.key
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            score = self.player.score if self.player else 0
            self.highscores.save_score(self.name_input, score)
            self._leave_name_entry()
        elif key == pygame.K_ESCAPE:
            self._leave_name_entry()
        elif key == pygame.K_BACKSPACE:
            self.name_input = self.name_input[:-1]

    def _type_name(self, text: str) -> None:
        """Append typed characters that are allowed in highscore names."""
        for char in text:
            if len(self.name_input) >= HighscoreSystem.MAX_NAME_LENGTH:
                break
            if HighscoreSystem.is_valid_name_char(char):
                self.name_input += char

    def _move_player_one_tile(self) -> bool:
        """Move Pac-Man one cell, but never through walls or boundaries."""
        if (
            self.current_state != self.STATE_PLAYING
            or self.player is None
            or self.maze is None
            or not self._held_move_keys
            or self._respawn_pause > 0
        ):
            return False

        direction_key = self._held_move_keys[-1]
        dr, dc = self.MOVE_KEYS[direction_key]
        new_r = self.player.r + dr
        new_c = self.player.c + dc
        if self.maze.is_wall(new_r, new_c):
            return False

        self.player.r = new_r
        self.player.c = new_c
        self.player.dr = dr
        self.player.dc = dc
        self._consume_current_tile()
        self._check_ghost_collisions()
        return True

    def _consume_current_tile(self) -> None:
        """Collect one maze item and update the score only once."""
        if self.player is None or self.maze is None:
            return

        item = self.maze.consume_item(self.player.r, self.player.c)
        if item == MazeState.PACGUM:
            self.player.score += self.config.points_per_pacgum
        elif item == MazeState.SUPER_PACGUM:
            self.player.score += self.config.points_per_super_pacgum
            self._activate_power_mode()

    def _activate_power_mode(self) -> None:
        """Make every ghost that is in play edible for a short time."""
        for ghost in self.ghosts:
            ghost.set_edible(self.POWER_MODE_DURATION)

    def _player_move_interval(self) -> float:
        """Seconds between player steps, shorter with the speed cheat."""
        if self.cheat_manager.speed_boost_active:
            return self.PLAYER_MOVE_INTERVAL / self.SPEED_BOOST_FACTOR
        return self.PLAYER_MOVE_INTERVAL

    def _update_player_movement(self, dt: float) -> None:
        """Repeat movement while a direction key is held."""
        if not self._held_move_keys:
            self._move_elapsed = 0.0
            return

        interval = self._player_move_interval()
        self._move_elapsed += max(0.0, dt)
        while self._move_elapsed >= interval:
            self._move_elapsed -= interval
            self._move_player_one_tile()
            if self.current_state != self.STATE_PLAYING:
                return

    def _update_ghosts(self, dt: float) -> None:
        """Move every active ghost one step when its interval has passed."""
        if (
            self.player is None
            or self.maze is None
            or self.cheat_manager.ghosts_frozen
        ):
            return

        distances: dict[tuple[int, int], int] | None = None
        for ghost in self.ghosts:
            if ghost.is_eaten:
                continue
            interval = (
                self.GHOST_EDIBLE_MOVE_INTERVAL
                if ghost.is_edible else self.GHOST_MOVE_INTERVAL
            )
            ghost.move_elapsed += max(0.0, dt)
            if ghost.move_elapsed < interval:
                continue
            # At most one step per frame; drop any leftover lag.
            ghost.move_elapsed = min(ghost.move_elapsed - interval, interval)

            if distances is None:
                # One search from the player serves all ghosts this frame.
                distances = self.maze.distances_from(
                    self.player.r, self.player.c
                )
            dr, dc = ghost.choose_direction(
                self.maze.open_moves(ghost.r, ghost.c), distances, self._rng
            )
            ghost.r += dr
            ghost.c += dc
            ghost.dr, ghost.dc = dr, dc

            self._check_ghost_collisions()
            if self.current_state != self.STATE_PLAYING:
                return
            if self._respawn_pause > 0:
                return  # Positions were reset; skip the rest of this frame.

    def _check_ghost_collisions(self) -> None:
        """Resolve the player sharing a tile with any ghost.

        Moves are made one tile at a time and checked after each step, so a
        player and a ghost can never pass through each other unnoticed.
        """
        if self.player is None or self._respawn_pause > 0:
            return

        for ghost in self.ghosts:
            if ghost.is_eaten:
                continue
            if (ghost.r, ghost.c) != (self.player.r, self.player.c):
                continue
            if ghost.is_edible:
                ghost.get_eaten(self.GHOST_RESPAWN_DELAY)
                self.player.score += self.config.points_per_ghost
            elif not self.cheat_manager.invincibility_active:
                self._lose_life()
                return

    def _lose_life(self) -> None:
        """Remove a life, then respawn everyone or end the game."""
        if self.player is None:
            return

        self.player.lose_life()
        self._held_move_keys.clear()
        self._move_elapsed = 0.0
        if self.player.lives <= 0:
            self._end_game(self.STATE_GAME_OVER)
            return

        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset()
        self._respawn_pause = self.RESPAWN_PAUSE

    def _update_playing(self, dt: float) -> None:
        """Advance timers, the player, the ghosts, and win/loss checks."""
        if self.player is None or self.maze is None:
            return

        if self._respawn_pause > 0:
            # Everything waits (including the level timer) after a death.
            self._respawn_pause = max(0.0, self._respawn_pause - dt)
            self._move_elapsed = 0.0
            return

        self.time_left -= dt
        if self.time_left <= 0 or self.player.lives <= 0:
            # Running out of time ends the game (our choice in the subject).
            self.time_left = max(0.0, self.time_left)
            self._end_game(self.STATE_GAME_OVER)
            return

        for ghost in self.ghosts:
            ghost.update_timer(dt)

        self._update_player_movement(dt)
        if self.current_state != self.STATE_PLAYING:
            return
        if self.maze.is_completed():
            self._advance_level()
            return

        self._update_ghosts(dt)
