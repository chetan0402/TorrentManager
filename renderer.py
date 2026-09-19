from pyray import *  # pyright: ignore[reportWildcardImportFromLibrary]

import time

from models import *

THRESHOLD_PRESS = 50


class App:
    state: State
    last_pressed: dict[KeyboardKey, int] = {}
    search = ""
    prev_search = "moew"
    selected = -1
    filtered: list[tuple[str, str]] = []

    def __init__(self) -> None:
        set_config_flags(ConfigFlags.FLAG_WINDOW_UNDECORATED)
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

            for key in self.state.keybinds:
                time_rn = time.time_ns() // 1000000
                if (
                    is_key_down(key)
                    and self.last_pressed[key] + THRESHOLD_PRESS < time_rn
                ):
                    self.last_pressed[key] = time_rn
                    self.state.keybinds[key]()

            if self.prev_search != self.search:
                self.filtered = []
                for key, label in self.state.opts:
                    if label.lower().__contains__(self.search.lower()):
                        self.filtered.append((key, label))
                self.prev_search = self.search

            begin_drawing()
            clear_background(Color(30, 45, 50))
            draw_text_ex(self.FONT, self.search, Vector2(5, 5), 20, 0, WHITE)
            i = 0
            for _, label in self.filtered:
                draw_text_ex(
                    self.FONT, label, Vector2(5, 5 + 20 + i * 20), 20, 0, WHITE
                )
                i = i + 1

            if i > 0:
                self.selected = int(clamp(self.selected, 0, i - 1))

            draw_rectangle(
                5,
                5 + 20 * (self.selected + 1),
                get_monitor_width(0),
                20,
                color_alpha(WHITE, 0.2),
            )
            end_drawing()

    def set_state(self, state: State) -> None:
        self.state = state
        for key in self.state.keybinds:
            self.last_pressed[key] = 0

        def backspace():
            self.search = self.search[:-1]

        def down():
            self.selected = self.selected + 1

        def up():
            self.selected = self.selected - 1

        def enter():
            self.state.opts_handler(self.filtered[self.selected][0])

        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_BACKSPACE)] = backspace
        self.last_pressed[KeyboardKey(KeyboardKey.KEY_BACKSPACE)] = 0

        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_DOWN)] = down
        self.last_pressed[KeyboardKey(KeyboardKey.KEY_DOWN)] = 0

        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_UP)] = up
        self.last_pressed[KeyboardKey(KeyboardKey.KEY_UP)] = 0

        self.state.keybinds[KeyboardKey(KeyboardKey.KEY_ENTER)] = enter
        self.last_pressed[KeyboardKey(KeyboardKey.KEY_ENTER)] = 0

    def __del__(self) -> None:
        close_window()


if __name__ == "__main__":
    import main

    app = App()

    def callback(key: str) -> None:
        print(key)

    state = State([], callback, {})
    for t in main.get_torrents():
        state.opts.append((t.hash, t.name))

    app.set_state(state)
    app.start()
