import threading
import requests
from io import BytesIO
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import os
import sys
import subprocess

class VideoController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.load_btn.configure(command=self.load_video)
        self.view.download_btn.configure(command=self.download_video)
        self.view.history_btn.configure(command=self.show_history_popup)

    # Load video info
    def load_video(self):
        def task():
            url = self.view.entry.get().strip()
            if not url:
                self.view.show_message("Error", "Please paste a YouTube URL.")
                return
            self.view.details_label.configure(text="Loading video info...")
        
            try:
                with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
            except Exception as e:
                self.view.show_message("Load Error", f"Enter a valid url ")
                self.view.details_label.configure(text="", )
                return

            title = info.get("title", "Unknown Title")
            self.view.video_title.configure(text=title)

            thumb_url = info.get("thumbnail")
            if thumb_url:
                try:
                    img_data = requests.get(thumb_url, timeout=8).content
                    img = Image.open(BytesIO(img_data)).convert("RGBA")
                    img.thumbnail((300, 200))
                    tk_img = ImageTk.PhotoImage(img)
                    self.view.placeholder.configure(image=tk_img, text="")
                    self.view.placeholder.image = tk_img
                except:
                    self.view.placeholder.configure(text="Thumbnail failed")

            formats = info.get("formats", [])
            resolutions = sorted(
                set(f"{f.get('height')}p" for f in formats if f.get("height") and f.get("acodec") != "none"),
                key=lambda x: int(x.replace("p", ""))
            )
            if not resolutions:
                resolutions = ["original"]
            self.view.res_menu.configure(values=resolutions)
            self.view.res_var.set(resolutions[-1])
            self.view.details_label.configure(text="Video info loaded.")

        threading.Thread(target=task, daemon=True).start()

    # Download video
    def download_video(self):
        def task():
            url = self.view.entry.get().strip()
            res = self.view.res_var.get()
            if not url:
                self.view.show_message("Error", "Paste a video URL first.")
                return
            self.view.details_label.configure(text="Preparing download...")

            if res.lower() == "original":
                fmt = "bestvideo+bestaudio/best"
            else:
                try:
                    height = int(res.replace("p", ""))
                    fmt = f"bestvideo[height<={height}]+bestaudio/best"
                except:
                    fmt = "bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "quiet": True,
                "outtmpl": os.path.join(self.model.DOWNLOAD_DIR, "%(title)s.%(ext)s"),
                "progress_hooks": []
            }

            def hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    done = d.get("downloaded_bytes", 0)
                    frac = done / total if total else 0
                    speed = int((d.get("speed") or 0) / 1024)
                    eta = d.get("eta", 0)
                    self.view.progress_bar.set(frac)
                    self.view.details_label.configure(
                        text=f"Downloading {int(frac*100)}% | {speed} KB/s | ETA {eta}s"
                    )
                elif d["status"] == "finished":
                    self.view.progress_bar.set(1)
                    self.view.details_label.configure(text="Finalizing...")

            ydl_opts["progress_hooks"].append(hook)

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url)
                file_path = ydl.prepare_filename(info)
                self.model.add_to_history(file_path)
                self.view.show_message("Success", "Video saved to Downloads folder.")
                self.view.details_label.configure(text="Download complete.")
            except Exception as e:
                self.view.show_message("Error", f"Download failed:\n{e}")
                self.view.details_label.configure(text="")

        threading.Thread(target=task, daemon=True).start()

    # Show download history
    def show_history_popup(self):
        history = self.model.get_history()
        if not history:
            self.view.show_message("History", "No videos downloaded yet.")
            return
        import customtkinter as ctk
        popup = ctk.CTkToplevel(self.view.root)
        popup.title("Download History")
        popup.transient(self.view.root)
        popup.grab_set()
        popup.configure(fg_color="#0E0C0C")

        # Size and center
        popup_w, popup_h = 400, 300
        self.view.root.update_idletasks()
        root_x, root_y = self.view.root.winfo_x(), self.view.root.winfo_y()
        root_w, root_h = self.view.root.winfo_width(), self.view.root.winfo_height()
        pos_x = root_x + (root_w // 2) - (popup_w // 2)
        pos_y = root_y + (root_h // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{pos_x}+{pos_y}")

        history_text = "\n".join(f"{i+1}. {os.path.basename(v)}" for i, v in enumerate(history))
        history_lbl = ctk.CTkLabel(popup, text=history_text, justify="left", anchor="nw", wraplength=380,text_color="white")
        history_lbl.pack(padx=10, pady=10, fill="both", expand=True)

        # Click to play
        def on_click(event):
            index = int(event.y // 20)
            if 0 <= index < len(history):
                try:
                    if os.name == "nt":
                        os.startfile(history[index])
                    elif sys.platform == "darwin":
                        subprocess.call(["open", history[index]])
                    else:
                        subprocess.call(["xdg-open", history[index]])
                except Exception as e:
                    self.view.show_message("Error", f"Unable to play video")

        history_lbl.bind("<Button-1>", on_click)
        popup_text= ctk.CTkLabel(popup,text="Click on history/n to play video")
        popup_text.place(anchor="s")


        

        # Close
        close_btn = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=10)

