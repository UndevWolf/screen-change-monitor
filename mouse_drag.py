import tkinter as tk


class ScreenCaptureOverlay:
    def __init__(self, on_complete=None):
        self.on_complete = on_complete

        # Create fullscreen overlay
        self.overlay = tk.Toplevel()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.configure(bg="black")

        # Canvas for drawing
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Track drag
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def on_mouse_down(self, event):
        self.start_x = self.overlay.winfo_pointerx()
        self.start_y = self.overlay.winfo_pointery()

        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=1
        )

    def on_mouse_drag(self, event):
        cur_x = self.overlay.winfo_pointerx()
        cur_y = self.overlay.winfo_pointery()

        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        end_x = self.overlay.winfo_pointerx()
        end_y = self.overlay.winfo_pointery()

        left = min(self.start_x, end_x)
        right = max(self.start_x, end_x)
        top = min(self.start_y, end_y)
        bottom = max(self.start_y, end_y)

        if self.on_complete:
            self.on_complete(left, top, right, bottom)

        self.overlay.destroy()
        return [left, right, top, bottom]
