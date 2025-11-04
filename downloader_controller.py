import threading
import requests
from downloader_model import VideoModel
from downloader_view import VideoView
from tkinter import  messagebox
class VideoController:
    """Controller: Handles user interactions and coordinates Model-View"""
    
    def __init__(self, root):
        self.model = VideoModel()
        self.view = VideoView(root)
        
        # Bind events
        self.view.load_btn.config(command=self.load_video)
        self.view.download_btn.config(command=self.start_download)
        self.view.format_combo.bind('<<ComboboxSelected>>', self.on_format_selected)
        self.view.root.bind('<Configure>', self.on_resize)
    
    def load_video(self):
        """Handle load video action."""
        url = self.model.sanitize_url(self.view.get_url())
        
        if not url:
            messagebox.showerror("Error", "Please paste a valid YouTube URL.")
            return
        
        self.view.set_status("Loading video info...", "yellow")
        self.view.set_button_state("load", "disabled")
        
        threading.Thread(target=self._load_video_thread, args=(url,), daemon=True).start()
    
    def _load_video_thread(self, url):
        """Background thread for loading video."""
        try:
            # Fetch video info
            self.model.fetch_video_info(url)
            
            # Process formats
            formats = self.model.process_formats()
            
            # Update view
            self.view.root.after(0, self._update_view_after_load, formats)
            
        except Exception as e:
            self.view.root.after(0, lambda: self.view.set_status(f"Error: {e}", "red"))
            self.view.root.after(0, lambda: self.view.set_button_state("load", "normal"))
    
    def _update_view_after_load(self, formats):
        """Update view after video is loaded."""
        # Set formats
        self.view.set_formats(formats)
        
        # Set video metadata
        metadata = self.model.get_video_metadata()
        self.view.set_video_info(metadata)
        
        # Load thumbnail
        thumb_url = self.model.get_thumbnail_url()
        if thumb_url:
            try:
                resp = requests.get(thumb_url)
                self.view.load_thumbnail(resp.content)
            except:
                pass
        
        self.view.set_status("✅ Video loaded successfully!", "#00FF99")
        self.view.set_button_state("load", "normal")
    
    def on_format_selected(self, event):
        """Handle format selection."""
        resolution = self.view.get_selected_resolution()
        if resolution:
            fmt = self.model.get_format_by_resolution(resolution)
            if fmt:
                self.view.set_format_details(fmt)
    
    def start_download(self):
        """Handle download action."""
        if not self.model.video_info:
            messagebox.showwarning("Load First", "Please load a video first.")
            return
        
        resolution = self.view.get_selected_resolution()
        if not resolution:
            messagebox.showwarning("No Resolution", "Select a resolution before downloading.")
            return
        
        if self.model.is_downloading:
            messagebox.showwarning("Downloading", "A download is already in progress.")
            return
        
        self.model.is_downloading = True
        self.view.set_button_state("download", "disabled", "Downloading...", "#555")
        
        threading.Thread(target=self._download_thread, args=(resolution,), daemon=True).start()
    
    def _download_thread(self, resolution):
        """Background thread for downloading."""
        try:
            self.view.root.after(0, lambda: self.view.set_status("Downloading...", "yellow"))
            
            self.model.download_video(resolution, self.progress_hook)
            
            metadata = self.model.get_video_metadata()
            success_msg = f"✅ Download Complete! Saved to {self.model.download_path}"
            
            self.view.root.after(0, lambda: self.view.set_status(success_msg, "#00FF99"))
            self.view.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Video downloaded successfully!\n\nTitle: {metadata['title']}\nSaved to: {self.model.download_path}"
            ))
            
        except Exception as e:
            self.view.root.after(0, lambda: self.view.set_status(f"Download failed: {e}", "red"))
            self.view.root.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n\n{str(e)}"))
        
        finally:
            self.model.is_downloading = False
            self.view.root.after(0, lambda: self.view.set_button_state("download", "normal", "Download Video", "#FFD700"))
            self.view.root.after(0, self.view.reset_progress)
    
    def progress_hook(self, d):
        """Handle download progress updates."""
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    percent = int((downloaded / total) * 100)
                    self.view.root.after(0, lambda: self.view.update_progress(percent))
                    
                    # Update status with speed and ETA
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    if speed:
                        speed_mb = speed / (1024 * 1024)
                        status_text = f"Downloading... Speed: {speed_mb:.2f} MB/s"
                        if eta:
                            status_text += f" | ETA: {eta}s"
                        self.view.root.after(0, lambda: self.view.set_status(status_text, "yellow"))
            except:
                pass
        elif d['status'] == 'finished':
            self.view.root.after(0, lambda: self.view.update_progress(100))
            self.view.root.after(0, lambda: self.view.set_status("Processing... Almost done!", "yellow"))
    
    def on_resize(self, event):
        """Handle window resize."""
        if event.widget == self.view.root and self.view.original_thumbnail_data:
            self.view.root.after(100, self.view.resize_thumbnail)
