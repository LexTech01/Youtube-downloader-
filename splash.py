# splash.py
import tkinter as tk
from itertools import count
from PIL import Image, ImageTk, ImageSequence

def show_splash(root, gif_path="images/splash.gif", duration=4000):
    """
    Show splash inside the given CTk window (root)
    """
    # Create overlay label
    overlay = tk.Label(root, bg='white')
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Load GIF frames
    gif = Image.open(gif_path)
    frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGBA')
        frame = frame.resize((850,950), Image.LANCZOS)
        frames.append(ImageTk.PhotoImage(frame))

    frame_count = len(frames)

    # Animate GIF
    def animate(counter=count()):
        frame = frames[next(counter) % frame_count]
        overlay.config(image=frame)
        root.after(50, animate)

    animate()

    # Fade out overlay
    def fade_out(alpha=1.0):
        alpha -= 0.02
        if alpha > 0:
            overlay.configure(bg='white')
            overlay.update()
            root.after(50, lambda: fade_out(alpha))
        else:
            overlay.destroy()

    # Start fade out after duration
    root.after(duration, fade_out)
