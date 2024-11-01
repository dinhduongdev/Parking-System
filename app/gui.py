import tkinter as tk
import tkinter.font as tkFont
from tkinter import scrolledtext
from PIL import Image, ImageTk
import cv2
from threading import Thread
from app.camera import CameraIn, BLACK_IMG
import threading


class CameraPanel(tk.Frame):

    def __init__(self, parent, url, title):
        super().__init__(parent)
        self.camera_thread = CameraIn(url, title)
        self.process_thread = threading.Thread(
            target=self.camera_thread.start, daemon=True
        )
        self.display_thread = threading.Thread(target=self.display, daemon=True)
        self.delay_ms = int(self.camera_thread.delay * 1000)

        self.canvas = tk.Canvas(self, width=480, height=480)
        self.canvas.pack()

        self.checkbox_var = tk.BooleanVar(value=True)
        self.checkbox = tk.Checkbutton(
            self,
            text=f"Display {title}",
            variable=self.checkbox_var,
            command=self.toggle_display,
        )
        self.checkbox.pack()

        self.label_text_var = tk.StringVar()
        self.log_text = tk.Label(
            self,
            textvariable=self.label_text_var,
            width=50,
            height=10,
            font=("Arial", 25, "bold"),
        )
        self.log_text.pack()

    def display(self):
        if self.camera_thread.img is None:
            img = BLACK_IMG
        else:
            img = self.camera_thread.img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Get original image dimensions
            original_height, original_width = img.shape[:2]
            # Calculate the aspect ratio
            ratio = min(480 / original_width, 480 / original_height)
            # Scale the image to fit within the canvas while maintaining aspect ratio
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            img = cv2.resize(img, (new_width, new_height))

        img = ImageTk.PhotoImage(Image.fromarray(img))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img
        if self.camera_thread.detected_plates != "":
            self.label_text_var.set(self.camera_thread.detected_plates)
            self.camera_thread.detected_plates = ""
            self.camera_thread.resume()
        self.after(self.delay_ms, self.display)

    def toggle_display(self):
        if self.checkbox_var.get():
            self.camera_thread.resume()
        else:
            self.camera_thread.pause()

    def stop(self):
        self.camera_thread.stop()
        self.process_thread.join()
        self.display_thread.join()

    def run(self):
        self.process_thread.start()
        self.display_thread.start()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Camera App")
        self.wm_state("zoomed")

        self.panel1 = CameraPanel(self, 0, "Camera 1")
        self.panel1.pack(side=tk.LEFT, padx=10, pady=10)

        # self.panel2 = CameraPanel(self, "https://192.168.1.11:8080/video", "Camera 2")
        # self.panel2.pack(side=tk.RIGHT, padx=10, pady=10)

        in_panel_thread = Thread(target=self.panel1.run, daemon=True)
        # out_panel_thread = Thread(target=self.panel2.run, daemon=True)
        in_panel_thread.start()
        # out_panel_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.panel1.stop()
        # self.panel2.stop()
        self.destroy()
