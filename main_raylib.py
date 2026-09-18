from pyray import *

init_window(800, 200, "Test")
h, w = get_monitor_height(0), get_monitor_width(0)
set_window_size(w, h - 26)
set_window_position(0, 26)
set_window_state(ConfigFlags.FLAG_WINDOW_UNDECORATED)
while not window_should_close():
    begin_drawing()
    draw_text("Hello", 0, 0, 24, WHITE)
    end_drawing()

close_window()
