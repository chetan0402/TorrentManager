from pyray import *  # pyright: ignore[reportWildcardImportFromLibrary]

search = ""

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

    begin_drawing()
    clear_background(Color(30, 45, 50))
    draw_text(search, 5, 5, 24, WHITE)
    end_drawing()

close_window()
