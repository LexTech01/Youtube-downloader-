import customtkinter as ctk
from downloader_model import VideoModel
from downloader_view import VideoView
from downloader_controller import VideoController
from splash import show_splash  # Import splash overlay

if __name__ == "__main__":
   
    root = ctk.CTk()
    # Initialize your view, model, controller
    model = VideoModel()
    view = VideoView(root)
    controller = VideoController(model, view)
    show_splash(root, "images/splash.gif", duration=3000)
   
    

    root.mainloop()
