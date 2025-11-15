import customtkinter as ctk
from downloader_model import VideoModel
from downloader_view import VideoView
from downloader_controller import VideoController

if __name__ == "__main__":
    root = ctk.CTk()
    model = VideoModel()
    view = VideoView(root)
    controller = VideoController(model, view)
    root.mainloop()
