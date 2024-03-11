import gi
import pyautogui
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener
from Xlib import display
from pynput import keyboard

# Global variable to keep track of typed text
typed_text = ""
# Variable to track if the Super key is pressed
super_key_pressed = False

# Function to get the current cursor position
def get_cursor_position():
    data = display.Display().screen().root.query_pointer()._data
    return data["root_x"], data["root_y"]

# Function to create an overlay window with GTK+
def create_overlay_window():
    window = Gtk.Window(type=Gtk.WindowType.POPUP)
    window.set_default_size(100, 20)
    window.set_keep_above(True)
    window.set_decorated(False)
    window.set_app_paintable(True)
    window.set_opacity(0.8)
    screen = window.get_screen()
    visual = screen.get_rgba_visual()
    if visual and screen.is_composited():
        window.set_visual(visual)
    label = Gtk.Label()
    window.add(label)
    window.show_all()
    return window, label

# Function to update the overlay window position and text
def update_window(window, label, text):
    x, y = get_cursor_position()
    GLib.idle_add(window.move, x + 20, y - 10)
    GLib.idle_add(label.set_text, text)

# Callback for key press events
def on_key_press(key):
    global typed_text, super_key_pressed
    try:
        if key == Key.space:
            typed_text += " "
        elif key == Key.cmd:  # Captures the Super key press
            super_key_pressed = True
        # Correctly check for 'Tab' key press along with 'Super'
        elif key == Key.tab and super_key_pressed:
            # Simulate typing the memory content and clear it
            pyautogui.typewrite(typed_text)
            typed_text = ""  # Clear memory after typing
        else:
            if hasattr(key, 'char'):
                typed_text += key.char
    except AttributeError:
        # Handle special keys here if needed
        pass
    # Do not update window with the typed text here to avoid duplicating actions

# Callback for key release events
def on_key_release(key):
    global super_key_pressed
    if key == Key.cmd:  # Captures the Super key release
        super_key_pressed = False

# Callback for mouse move events
def on_move(x, y):
    global typed_text
    # Optionally reset typed text on mouse move or keep it for typing upon next "Super+Tab"
    # typed_text = ""
    # Update window to show default text or current memory
    update_window(window, label, "Typing..." if typed_text == "" else typed_text)

if __name__ == "__main__":
    window, label = create_overlay_window()

    # Start listening to keyboard and mouse events
    keyboard_listener = KeyboardListener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = MouseListener(on_move=on_move)

    keyboard_listener.start()
    mouse_listener.start()

    # GTK main loop
    Gtk.main()
