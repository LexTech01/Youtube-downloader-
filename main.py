# main.py
import tkinter as tk
from downloader_controller import VideoController

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoController(root)
    root.mainloop()
