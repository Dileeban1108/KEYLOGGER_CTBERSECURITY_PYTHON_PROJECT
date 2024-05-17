import keyboard
import pyperclip
from datetime import datetime
import os
import time
import threading

class ClipboardMonitor:
    def __init__(self, interval=1):
        self.interval = interval
        self.previous_clipboard_content = pyperclip.paste()

    def save_clipboard_content(self, content):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # Adjusted to use a file-friendly format
        content_to_save = f"{now.date()} - {now.time()} - \n{content}\n"

        clipboard_dir = os.path.join(os.getcwd(), 'Logs')
        if not os.path.exists(clipboard_dir):
            os.makedirs(clipboard_dir)

        file_path = os.path.join(clipboard_dir, f"clipboard_{timestamp}.txt")
        with open(file_path, "w") as file:  # Changed to "w" to write to a new file
            file.write(content_to_save)
            file.write("\n")

    def start_monitoring(self):
        print("Clipboard monitoring started. Press 'Ctrl+Alt' to stop.")
        try:
            while True:
                clipboard_content = pyperclip.paste()
                if clipboard_content != self.previous_clipboard_content:
                    self.previous_clipboard_content = clipboard_content
                    self.save_clipboard_content(clipboard_content)
                    print("New clipboard content saved.")
                time.sleep(self.interval)
                if keyboard.is_pressed('ctrl')  and keyboard.is_pressed('alt'):
                    print("Clipboard monitoring stopped.")
                    break
        except KeyboardInterrupt:
            print("Clipboard monitoring stopped.")

if __name__ == "__main__":
    clipboard_monitor = ClipboardMonitor()
    clipboard_monitor_thread = threading.Thread(target=clipboard_monitor.start_monitoring)

    clipboard_monitor_thread.start()

    clipboard_monitor_thread.join()
