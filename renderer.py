from pyray import *  # pyright: ignore[reportWildcardImportFromLibrary]

import time
from typing import Literal

from models import *

THRESHOLD_FIRST_INPUT = 500
THRESHOLD_REPEAT_INPUT = 50


class App:
    state: State
    last_pressed: dict[KeyboardKey, tuple[int, Literal["first", "repeat"]]] = {}
    search = ""
    prev_search = None
    selected = -1
    opt_selected: str = ""
    filtered: list[tuple[str, str]] = []

    def __init__(self) -> None:
        set_config_flags(
            ConfigFlags.FLAG_WINDOW_UNDECORATED | ConfigFlags.FLAG_WINDOW_TRANSPARENT
        )
        init_window(1, 1, "")
        self.FONT = load_font_ex("RobotoMonoNerdFont-Medium.ttf", 20, None, 0)
        h, w = get_monitor_height(0), get_monitor_width(0)
        set_window_size(w, h - 26)
        set_window_position(0, 26)
        set_target_fps(60)

    def start(self) -> None:
        while not window_should_close():
            key = get_char_pressed()
            while key > 0:
                self.search += chr(key)
                key = get_char_pressed()

            if self.prev_search != self.search:
                self.filtered = []
                for key, label in self.state.opts:
                    if label.lower().__contains__(self.search.lower()):
                        self.filtered.append((key, label))
                self.prev_search = self.search

            self.selected = int(clamp(self.selected, 0, len(self.filtered) - 1))
            if len(self.filtered) > 0:
                self.opt_selected = self.filtered[self.selected][0]
            else:
                self.opt_selected = ""

            for key in self.state.keybinds:
                time_rn = time.time_ns() // 1000000
                if is_key_pressed(key):
                    self.last_pressed[key] = (time_rn, "first")
                    self.state.keybinds[key](self.opt_selected)
                elif is_key_down(key):
                    if (
                        self.last_pressed[key][1] == "first"
                        and self.last_pressed[key][0] + THRESHOLD_FIRST_INPUT < time_rn
                    ) or (
                        self.last_pressed[key][1] == "repeat"
                        and self.last_pressed[key][0] + THRESHOLD_REPEAT_INPUT < time_rn
                    ):
                        self.last_pressed[key] = (time_rn, "repeat")
                        self.state.keybinds[key](self.opt_selected)

            begin_drawing()
            clear_background(Color(30, 45, 50, 200))
            draw_text_ex(self.FONT, self.search, Vector2(5, 5), 20, 0, WHITE)
            for i, t in enumerate(self.filtered):
                _, label = t
                draw_text_ex(
                    self.FONT, label, Vector2(5, 5 + 20 + i * 20), 20, 0, WHITE
                )

            draw_rectangle(
                5,
                5 + 20 * (int(clamp(self.selected, 0, len(self.filtered) - 1)) + 1),
                get_monitor_width(0),
                20,
                color_alpha(WHITE, 0.2),
            )
            end_drawing()

    def set_state(self, state: State) -> None:
        self.state = state
        self.search = ""
        self.prev_search = None
        self.selected = -1

        def backspace(_):
            self.search = self.search[:-1]

        def down(_):
            self.selected = self.selected + 1

        def up(_):
            self.selected = self.selected - 1

        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_BACKSPACE)] = backspace
        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_DOWN)] = down
        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_UP)] = up

        for key in self.state.keybinds:
            self.last_pressed[key] = (time.time_ns() // 1000000, "first")

    def set_opts(self, opts: list[tuple[str, str]]) -> None:
        self.state.opts = opts
        self.prev_search = None

    def __del__(self) -> None:
        close_window()
