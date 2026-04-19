import tkinter as tk
from tkinter import scrolledtext
import sys
import pytesseract
from PIL import ImageGrab
import time
import cv2
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import config
import os
import threading
import mouse_drag

smtp_server = config.smtp_server
smtp_port = config.smtp_port
imap_server = config.imap_server
imap_port = config.imap_port
email_user = config.email_user
email_password = config.email_password
receiver_email = config.receiver_email
email_subject = config.email_subject
pytesseract.pytesseract.tesseract_cmd = config.tesseract
img_path = config.output_img_path
bbox = []


class ConsoleRedirect:
    # Redirects print() output to a Tkinter Text widget.

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass  # Needed for Python's stdout interface


def main():
    root = tk.Tk()
    root.title("Screen Sentry")

    # --- Input Fields ---
    tk.Label(root, text="Email:").grid(row=0, column=0, sticky="e")
    entry1 = tk.Entry(root, width=30)
    entry1.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Seconds:").grid(row=1, column=0, sticky="e")
    entry2 = tk.Entry(root, width=30)
    entry2.grid(row=1, column=1, padx=5, pady=5)

    start_button = tk.Button(root, text="Start", command=start_screen_capture)
    start_button.grid(row=2, column=0, pady=5)
    end_button = tk.Button(root, text="End", command=end_monitor)
    end_button.grid(row=2, column=1, pady=5)

    # --- Console Output Text Box ---
    console_box = scrolledtext.ScrolledText(
        root, width=60, height=15, wrap=tk.WORD)
    console_box.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    # Redirect stdout to the text widget
    sys.stdout = ConsoleRedirect(console_box)

    print("Console initialized. All print() output will appear here.")

    root.mainloop()


def start_thread():
    t = threading.Thread(target=monitor)
    t.start()


def start_screen_capture():
    print("Screen capture mode activated. Drag anywhere on the screen.")
    mouse_drag.ScreenCaptureOverlay(on_complete=on_capture_complete)


def on_capture_complete(left, top, right, bottom):
    bbox.clear()
    bbox.extend([left, top, right, bottom])
    print("Monitoring:", bbox)
    start_thread()


def end_monitor():
    end_monitor.has_been_called = True


def email_content(client_email, image_path, body):
    message = MIMEMultipart()
    message['Subject'] = email_subject
    message['From'] = email_user
    message['To'] = client_email
    message.attach(MIMEText(body, 'html'))
    with open(image_path, 'rb') as img:
        msg_image = MIMEImage(
            img.read(), name=os.path.basename(image_path))
        message.attach(msg_image)
    body = message.as_bytes()
    return body


def send_email(client_email, email_content):
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(email_user, email_password)
        server.sendmail(email_user, client_email, email_content)
        print("EMAIL SENT SUCCESSFULLY")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()
    pass


def preprocess_img(img):
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    return thresh


def extract_text(processed_img):
    return pytesseract.image_to_string(processed_img)


def monitor():
    previous_text = ""
    end_monitor.has_been_called = False
    while True:
        if end_monitor.has_been_called:
            print("|=========================STOPPED==========================|")
            break
        img = ImageGrab.grab(bbox)
        processed_img = preprocess_img(img)
        current_text = extract_text(processed_img)
        if current_text != previous_text:
            img.save(img_path)
        if current_text != previous_text:
            print("|======================SCREEN CHANGED======================|")
            message = email_content(
                receiver_email, img_path, current_text)
            send_email(receiver_email, message)
            print(current_text)
            previous_text = current_text
        time.sleep(10)


if __name__ == "__main__":
    main()
