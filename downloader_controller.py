import threading
import requests
from io import BytesIO
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import os
import sys
import subprocess
import time

class VideoController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Thumbnail cache 
        self._thumb_cache = {}

        # Cached internet state (updated by monitor thread)
        self.internet_available = True
        self._start_internet_monitor()

        # Wire buttons
        self.view.load_btn.configure(command=self.load_video)
        self.view.download_btn.configure(command=self.download_video)
        self.view.history_btn.configure(command=self.show_history_popup)

        # Download state
        self._is_downloading = False

    # -----------------------
    # Internet monitor
    # -----------------------
    def _start_internet_monitor(self):
        def monitor():
            while True:
                try:
                    requests.get("https://www.google.com", timeout=3)
                    self.internet_available = True
                except:
                    self.internet_available = False
                time.sleep(5)  # check every 5 seconds
        t = threading.Thread(target=monitor, daemon=True)
        t.start()

    def check_internet(self):
        # fast check using cached value
        return self.internet_available

    # -----------------------
    # Thread-safe UI helpers
    # -----------------------
    def _ui(self, fn, *args, **kwargs):
        """Call fn(*args, **kwargs) safely on the Tk main thread."""
        self.view.root.after(0, lambda: fn(*args, **kwargs))

    # -----------------------
    # Load video info
    # -----------------------
    def load_video(self):
        def task():
            url = self.view.entry.get().strip()
            if not url:
                self._ui(self.view.show_message, "Error", "Please paste a YouTube URL.")
                return

            # quick offline check 
            if not self.check_internet():
                self._ui(self.view.show_message, "No Internet", "Cannot load video info while offline.")
                return

            self._ui(lambda: self.view.details_label.configure(text="Loading video info..."))

            try:
                with YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
            except Exception as e:
                self._ui(lambda: self.view.details_label.configure(text=""))
                self._ui(self.view.show_message, "Load Error", f"Enter a valid URL or try again.\n{str(e)}")
                return

            title = info.get("title", "Unknown Title")
            self._ui(lambda: self.view.video_title.configure(text=title))

            # Thumbnail 
            thumb_url = info.get("thumbnail")
            if thumb_url:
                if thumb_url in self._thumb_cache:
                    # apply cached image on UI thread
                    self._ui(self._apply_thumbnail, self._thumb_cache[thumb_url])
                else:
                    # download + cache in background
                    def thumb_task():
                        try:
                            img_data = requests.get(thumb_url, timeout=8).content
                            img = Image.open(BytesIO(img_data)).convert("RGBA")
                            img.thumbnail((300, 200), Image.LANCZOS)
                            tk_img = ImageTk.PhotoImage(img)
                            self._thumb_cache[thumb_url] = tk_img
                            self._ui(self._apply_thumbnail, tk_img)
                        except Exception:
                            self._ui(lambda: self.view.placeholder.configure(text="Thumbnail failed"))
                    threading.Thread(target=thumb_task, daemon=True).start()
            else:
                self._ui(lambda: self.view.placeholder.configure(text="No thumbnail"))

            # Formats / resolutions
            formats = info.get("formats", [])
            resolutions = sorted(
                set(f"{f.get('height')}p" for f in formats if f.get("height") and f.get("acodec") != "none"),
                key=lambda x: int(x.replace("p", "")) if x and x != "None" else 0
            )
            if not resolutions:
                resolutions = ["original"]
            # update UI
            self._ui(lambda: self.view.res_menu.configure(values=resolutions))
            self._ui(lambda: self.view.res_var.set(resolutions[-1]))
            self._ui(lambda: self.view.details_label.configure(text="Video info loaded."))

        threading.Thread(target=task, daemon=True).start()

    def _apply_thumbnail(self, tk_img):
        # apply the Tk image to the placeholder 
        try:
            self.view.placeholder.configure(image=tk_img, text="")
            self.view.placeholder.image = tk_img
        except Exception:
            pass

    # -----------------------
    # Downloading - FIXED PROGRESS BAR
    # -----------------------
    def download_video(self):
        if self._is_downloading:
            self._ui(self.view.show_message, "Info", "A download is already in progress.")
            return

        def task():
            self._is_downloading = True
            url = self.view.entry.get().strip()
            res = self.view.res_var.get()
            
            if not url:
                self._ui(self.view.show_message, "Error", "Load a video URL first.")
                self._is_downloading = False
                return

            if not self.check_internet():
                self._ui(self.view.show_message, "No Internet", "Cannot download while offline.")
                self._is_downloading = False
                return

            # Reset UI state
            self._ui(self.view.progress_bar.set, 0)
            self._ui(lambda: self.view.details_label.configure(text="Preparing download..."))

            # Get the selected resolution
            res = self.view.res_var.get()

            if isinstance(res, str) and res.lower() == "original":
                fmt = "best"
            else:
                try:
                    height = int(str(res).replace("p", ""))
                    # This format string is more likely to work
                    fmt = f"bestvideo[height={height}]+bestaudio/best[height={height}]/bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                except:
                    fmt = "best"
            
            # Force the system's Downloads folder
            download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(download_folder, exist_ok=True)

            # Progress tracking variables
            last_update_time = 0
            last_progress = 0

            def progress_hook(d):
                nonlocal last_update_time, last_progress
                
                if d['status'] == 'downloading':
                    # Get progress information
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    
                    if total_bytes and total_bytes > 0:
                        progress = downloaded_bytes / total_bytes
                        # Ensure progress doesn't go backwards
                        progress = max(progress, last_progress)
                        last_progress = progress
                        
                        # Update progress bar
                        self._ui(self.view.progress_bar.set, progress)
                        
                        # Calculate speed and ETA
                        speed = d.get('speed', 0)
                        if speed:
                            speed_kbps = speed / 1024
                        else:
                            speed_kbps = 0
                            
                        eta = d.get('eta', 0)
                        
                        # Update details 
                        current_time = time.time()
                        if current_time - last_update_time > 0.3:  # Update every 300ms
                            self._ui(lambda: self.view.details_label.configure(
                                text=f"Downloading {int(progress * 100)}% | {speed_kbps:.0f} KB/s | ETA: {eta}s"
                            ))
                            last_update_time = current_time
                    
                    else:
                        # No total size available - show indeterminate progress
                        speed = d.get('speed', 0)
                        if speed:
                            speed_kbps = speed / 1024
                        else:
                            speed_kbps = 0
                            
                        downloaded_mb = downloaded_bytes / (1024 * 1024)
                        self._ui(lambda: self.view.details_label.configure(
                            text=f"Downloading... {downloaded_mb:.1f} MB | {speed_kbps:.0f} KB/s"
                        ))
                
                elif d['status'] == 'finished':
                    self._ui(self.view.progress_bar.set, 1.0)
                    self._ui(lambda: self.view.details_label.configure(text="Processing video..."))

                elif d['status'] == 'error':
                    self._ui(lambda: self.view.details_label.configure(text="Download error occurred"))
                    self._is_downloading = False

            ydl_opts = {
                'format': fmt,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'merge_output_format': 'mp4',
                'noprogress': False,  # Ensure progress is reported
                'quiet': False,       # Set to False to see more debug info
                'no_warnings': False,
                "extractor_args": {"youtube": {"player_client": ["default"]}},
            }

            try:
                self._ui(lambda: self.view.details_label.configure(text="Starting download..."))
                
                with YoutubeDL(ydl_opts) as ydl:
                    # Extract info first to get filename
                    info = ydl.extract_info(url, download=False)
                    file_path = ydl.prepare_filename(info)
                    
                    # Now download
                    ydl.download([url])
                
                # Record in history
                try:
                    if hasattr(self.model, 'add_to_history'):
                        self.model.add_to_history(file_path)
                    elif hasattr(self.model, 'download_history'):
                        self.model.download_history.append(file_path)
                except Exception as e:
                    print(f"History error: {e}")
                
                # Success message
                self._ui(lambda: self.view.details_label.configure(text="Download completed successfully!"))
                self._ui(self.view.show_message, "Success", f"Video saved to:\n{file_path}")
                
                # Reset progress after delay
                def reset_ui():
                    self._ui(self.view.progress_bar.set, 0)
                    self._ui(lambda: self.view.details_label.configure(text=""))
                
                threading.Timer(2.0, reset_ui).start()
                
            except Exception as e:
                error_msg = str(e)
                self._ui(self.view.show_message, "Download Error", f"Download failed:\n{error_msg}")
                self._ui(lambda: self.view.details_label.configure(text="Download failed"))
                self._ui(self.view.progress_bar.set, 0)
                print(f"Download error: {error_msg}")  # Debug output
            
            finally:
                self._is_downloading = False

        # Start download in separate thread
        download_thread = threading.Thread(target=task, daemon=True)
        download_thread.start()

    # -----------------------
    # History popup 
    # -----------------------
    def show_history_popup(self):
        import customtkinter as ctk

        history = list(self.model.get_history() or [])
        if not history:
            self.view.show_message("History", "No videos downloaded yet.")
            return

        popup = ctk.CTkToplevel(self.view.root)
        popup.title("Download History")
        popup.transient(self.view.root)
        popup.configure(fg_color="#0E0C0C")

        # Center window
        popup_w, popup_h = 420, 360
        self.view.root.update_idletasks()
        root_x, root_y = self.view.root.winfo_x(), self.view.root.winfo_y()
        root_w, root_h = self.view.root.winfo_width(), self.view.root.winfo_height()
        pos_x = root_x + (root_w // 2) - (popup_w // 2)
        pos_y = root_y + (root_h // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{pos_x}+{pos_y}")

        # Minimal offline banner
        if not self.check_internet():
            banner = ctk.CTkLabel(popup, text="⚠️ No Internet Connection", text_color="#ff4d4d", font=("Arial", 13, "bold"))
            banner.pack(pady=(6, 4))

        # Scrollable area
        scroll_frame = ctk.CTkScrollableFrame(popup, width=400, height=240, fg_color="#141212")
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Limit items to most recent 30 to avoid overload
        MAX_ITEMS = 30
        recent = history[-MAX_ITEMS:]

        for i, path in enumerate(recent, start=max(1, len(history)-len(recent)+1)):
            file_name = os.path.basename(path)

            item_frame = ctk.CTkFrame(scroll_frame, fg_color="#1A1A1A")
            item_frame.pack(fill="x", pady=5, padx=5)

            label = ctk.CTkLabel(item_frame, text=f"{i}. {file_name}", anchor="w", text_color="white")
            label.pack(side="left", padx=10, pady=5)

            open_state = "normal" if os.path.exists(path) else "disabled"
            open_btn = ctk.CTkButton(item_frame, text="Open", width=50, state=open_state,
                                     command=lambda p=path: self.open_file_from_history(p))
            open_btn.pack(side="right", padx=6)

        # Reset & Close (use lightweight commands)
        reset_btn = ctk.CTkButton(popup, text="Reset History", fg_color="#9b2c2c",
                                  hover_color="#b33636", command=self.reset_history)
        reset_btn.pack(side="left", padx=12, pady=8)

        close_btn = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_btn.pack(side="right", padx=12, pady=8)

    # -----------------------
    # Helpers
    # -----------------------
    def open_file_from_history(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            self._ui(self.view.show_message, "Error", f"Unable to open file.\n{e}")

    def reset_history(self):
        # clear model history in a safe way
        try:
            if hasattr(self.model, "reset_history"):
                self.model.reset_history().clear()
                self.show_history_popup.destroy()
            else:
                # fallback
                if hasattr(self.model, "download_history"):
                    self.model.download_history.clear()
                    self.show_history_popup.destroy()
        except Exception:
            pass
        self._ui(self.view.show_message, "History Reset", "Your download history has been cleared.")