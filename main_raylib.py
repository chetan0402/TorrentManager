from pyray import *  # pyright: ignore[reportWildcardImportFromLibrary]

import time

import main

THRESHOLD_PRESS = 50

search = ""
torrents = main.get_torrents()
last_backspace_pressed = 0

init_window(800, 200, "Test")
h, w = get_monitor_height(0), get_monitor_width(0)
set_window_size(w, h - 26)
set_window_position(0, 26)
set_window_state(ConfigFlags.FLAG_WINDOW_UNDECORATED)
while not window_should_close():
    key = get_char_pressed()
    while key > 0:
        search += chr(key)
        key = get_char_pressed()

    time_rn = time.time_ns() // 1000000
    if last_backspace_pressed + THRESHOLD_PRESS < time_rn and is_key_down(
        KeyboardKey.KEY_BACKSPACE
    ):
        search = search[:-1]
        last_backspace_pressed = time_rn

    begin_drawing()
    clear_background(Color(30, 45, 50))
    draw_text(search, 5, 5, 20, WHITE)
    i = 0
    for torrent in torrents:
        if torrent.name.lower().__contains__(search):
            draw_text(torrent.name[:100], 5, 5 + 20 + i * 20, 20, WHITE)
            i = i + 1
    end_drawing()

close_window()
