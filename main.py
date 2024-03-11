import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener
from Xlib import display
from pynput import keyboard
import pyautogui
import requests
import json
import time
import threading

# Global variable for the timer 
update_timer = None
typed_text = ""
super_key_pressed = False
last_sent_prompt = 'none'
suggestion = 'suggestion'
last_keypress_time = time.time() 

def get_suggestion_from_llm(prompt):
    url = 'http://localhost:11434/api/generate'
    data = {
        "model": "solar:10.7b-text-v1-q4_0",
        "prompt": "complete the following sentence: \n\n"+prompt,
        "stream": False,
        "options": {"num_predict": 10}
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    json_response = response.json()
    return json_response["response"]

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
    global last_sent_prompt, suggestion
    if check_file_content() == 'go':
        if text != last_sent_prompt:
            last_sent_prompt = text
            suggestion = get_suggestion_from_llm(text) 
    else:
        suggestion = ''

    x, y = get_cursor_position()
    GLib.idle_add(window.move, x + 20, y - 10)
    GLib.idle_add(label.set_text, suggestion)

# Function to check the content of the external file
def check_file_content():
    with open('/home/lunkwill/projects/type_friend/type_friend_state.txt', 'r') as file:
        content = file.read().strip()
    return content



# Callback for key press events
def on_key_press(key):
    global typed_text, super_key_pressed, suggestion, last_keypress_time, update_timer
    # Check the content of the external file
    if check_file_content() == 'go':
        try:
            if key == Key.space:
                typed_text += " "
            elif key == Key.backspace:
                typed_text = typed_text[:-1]
            elif key == Key.insert:  # This block captures the Super key press
                pyautogui.typewrite(suggestion)
            else:
                typed_text += key.char
        except AttributeError:
            # Special keys (e.g., enter, etc.) can be handled here
            pass
        # Cancel the existing timer if it exists
        if update_timer is not None:
            update_timer.cancel()
        # Start a new timer that will call update_window after 1 second
        update_timer = threading.Timer(1, update_window, args=(window, label, typed_text))
        update_timer.start()
    else:
        update_window(window, label, "")

# Function to update the overlay window position and text
def update_window(window, label, text):
    global last_sent_prompt, suggestion
    if check_file_content() == 'go':
        if text != last_sent_prompt:
            last_sent_prompt = text
            suggestion = get_suggestion_from_llm(text) 
    else:
        suggestion = ''

    x, y = get_cursor_position()
    GLib.idle_add(window.move, x + 20, y - 10)
    GLib.idle_add(label.set_text, suggestion)


# Callback for key release events
def on_key_release(key):
    global super_key_pressed
    # Check the content of the external file
    if check_file_content() == 'go':
        if key == Key.cmd:  # This block captures the Super key release
            super_key_pressed = False
    else:
        update_window(window, label, "")

# Callback for mouse move events
def on_move(x, y):
    global typed_text
    # Check the content of the external file
    if check_file_content() == 'go':
        update_window(window, label, typed_text)
    else:
        update_window(window, label, "")

if __name__ == "__main__":
    window, label = create_overlay_window()

    # Start listening to keyboard and mouse events with key release included
    with KeyboardListener(on_press=on_key_press, on_release=on_key_release) as keyboard_listener, MouseListener(on_move=on_move) as mouse_listener:
        Gtk.main()
