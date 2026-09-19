from pyray import *  # pyright: ignore[reportWildcardImportFromLibrary]

import time

import main
from models import *

THRESHOLD_PRESS = 50


class App:
    state = State({},{})
    last_pressed: dict[KeyboardKey, int] = {}
    search = ""

    def __init__(self) -> None:
        init_window(1, 1, "")
        self.FONT = load_font_ex("RobotoMonoNerdFont-Medium.ttf", 20, None, 0)
        h, w = get_monitor_height(0), get_monitor_width(0)
        set_window_size(w, h - 26)
        set_window_position(0, 26)
        set_window_state(ConfigFlags.FLAG_WINDOW_UNDECORATED)

    def start(self)->None:
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

            begin_drawing()
            clear_background(Color(30, 45, 50))
            draw_text_ex(self.FONT, self.search, Vector2(5, 5), 20, 0, WHITE)
            i = 0
            for label in self.state.opts:
                if label.lower().__contains__(self.search.lower()):
                    draw_text_ex(self.FONT, label, Vector2(5, 5 + 20 + i * 20), 20, 0, WHITE)
                    i=i+1
            end_drawing()

    def set_state(self,state: State)->None:
        self.state=state
        for key in self.state.keybinds:
            self.last_pressed[key]=0

    def __del__(self) -> None:
        close_window()


if __name__ == "__main__":
    app=App()
    state=State({},{})
    for t in main.get_torrents():
        state.opts[t.name]=t.hash

    def remove_char():
        app.search=app.search[:-1]

    state.keybinds[KeyboardKey(KeyboardKey.KEY_BACKSPACE)]=remove_char

    app.set_state(state)
    app.start()
