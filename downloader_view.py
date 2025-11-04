import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
class VideoView:
    """View: Handles UI components and display"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        self.root.config(bg="#101010")
        
        # Variables
        self.selected_format = tk.StringVar(value="Select Resolution")
        self.thumbnail_image = None
        self.original_thumbnail_data = None
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        """Configure ttk styles."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton",
                            font=("Segoe UI", 11, "bold"),
                            background="#FFD700",
                            foreground="black",
                            padding=8)
        self.style.map("TButton",
                      background=[("active", "#FFC300"), ("disabled", "#555")])
        
        self.style.configure("TCombobox",
                            fieldbackground="#FFD700",
                            background="#FFD700",
                            foreground="black",
                            arrowcolor="black",
                            borderwidth=0)
        
        self.style.configure("TProgressbar",
                            troughcolor="#1e1e1e",
                            background="#FFD700",
                            thickness=20)
    
    def add_hover_effect(self, widget, color_enter, color_leave):
        """Add hover effect to buttons."""
        def on_enter(e): 
            if widget['state'] != 'disabled':
                widget.config(bg=color_enter)
        def on_leave(e): 
            if widget['state'] != 'disabled':
                widget.config(bg=color_leave)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_widgets(self):
        """Create all GUI components."""
        
        # LEFT HEADER FRAME
        header_frame = tk.Frame(self.root, bg="#040227", width=250)
        header_frame.grid(row=0, column=0, sticky="ns")
        header_frame.grid_propagate(False)
        
        self.title_label = tk.Label(
            header_frame,
            text="YOUTUBE\nVIDEO\nDOWNLOADER",
            bg="#040227",
            fg="#00C3DD",
            justify="left",
            font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(pady=40, padx=10)
        
        # RIGHT CONTENT FRAME
        self.content_frame = tk.Frame(self.root, bg="#101010")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(2, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # URL Section
        tk.Label(
            self.content_frame,
            text="Paste YouTube URL Below",
            bg="#101010",
            fg="white",
            font=("Segoe UI", 13)
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.url_entry = tk.Entry(
            self.content_frame,
            font=("Segoe UI", 11),
            bd=3,
            relief="flat"
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        self.load_btn = tk.Button(
            self.content_frame,
            text="Load Video",
            bg="#FFD700",
            fg="black",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        )
        self.load_btn.grid(row=1, column=1, sticky="e", padx=(10, 0), pady=(0, 15))
        self.add_hover_effect(self.load_btn, "#FFC300", "#FFD700")
        
        # Thumbnail Frame
        self.thumbnail_frame = tk.Frame(self.content_frame, bg="#1e1e1e")
        self.thumbnail_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        self.thumbnail_frame.grid_rowconfigure(0, weight=1)
        self.thumbnail_frame.grid_columnconfigure(0, weight=1)
        
        self.thumbnail_label = tk.Label(
            self.thumbnail_frame,
            bg="#1e1e1e",
            text="No Video Loaded",
            fg="gray",
            font=("Segoe UI", 12)
        )
        self.thumbnail_label.grid(row=0, column=0, sticky="nsew")
        
        # Video Info Label
        self.video_info_label = tk.Label(
            self.content_frame,
            text="",
            bg="#101010",
            fg="white",
            font=("Segoe UI", 10),
            wraplength=500,
            justify="left"
        )
        self.video_info_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Selection Frame
        selection_frame = tk.Frame(self.content_frame, bg="#101010")
        selection_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(1, weight=1)
        
        # Resolution Dropdown
        res_frame = tk.Frame(selection_frame, bg="#101010")
        res_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        tk.Label(
            res_frame,
            text="Resolution & Format:",
            bg="#101010",
            fg="white",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 5))
        
        self.format_combo = ttk.Combobox(
            res_frame,
            textvariable=self.selected_format,
            state="readonly",
            font=("Segoe UI", 10),
            width=25
        )
        self.format_combo.pack(fill="x", ipady=8)
        
        # Format Info Label
        format_frame = tk.Frame(selection_frame, bg="#101010")
        format_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        tk.Label(
            format_frame,
            text="Format Details:",
            bg="#101010",
            fg="white",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 5))
        
        self.format_info_label = tk.Label(
            format_frame,
            text="No format selected",
            bg="#1e1e1e",
            fg="#FFD700",
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=10,
            justify="left"
        )
        self.format_info_label.pack(fill="both", expand=True)
        
        # Download Button
        self.download_btn = tk.Button(
            self.content_frame,
            text="Download Video",
            bg="#FFD700",
            fg="black",
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
            height=2
        )
        self.download_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.add_hover_effect(self.download_btn, "#FFC300", "#FFD700")
        
        # Progress Frame
        progress_frame = tk.Frame(self.content_frame, bg="#101010")
        progress_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.progress_label = tk.Label(
            progress_frame,
            text="0%",
            bg="#101010",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=5
        )
        self.progress_label.grid(row=0, column=1)
        
        # Status Label
        self.status_label = tk.Label(
            self.content_frame,
            text="Ready to download videos",
            bg="#101010",
            fg="white",
            font=("Segoe UI", 10),
            wraplength=500,
            justify="left"
        )
        self.status_label.grid(row=7, column=0, columnspan=2, sticky="w")
    
    def get_url(self):
        """Get URL from entry."""
        return self.url_entry.get()
    
    def get_selected_resolution(self):
        """Get selected resolution."""
        selected = self.selected_format.get()
        if selected and selected != "Select Resolution":
            return int(selected.split("p")[0])
        return None
    
    def set_status(self, message, color="white"):
        """Update status label."""
        self.status_label.config(text=message, fg=color)
    
    def set_video_info(self, metadata):
        """Display video metadata."""
        info_text = f"Title: {metadata['title']}\n"
        info_text += f"Author: {metadata['uploader']}\n"
        info_text += f"Duration: {metadata['duration']}"
        self.video_info_label.config(text=info_text)
    
    def set_formats(self, formats):
        """Populate format dropdown."""
        format_options = []
        for fmt in formats:
            size_str = f"{fmt['filesize_mb']:.1f} MB" if fmt['filesize_mb'] > 0 else "Unknown size"
            option = f"{fmt['height']}p - {fmt['ext']} ({size_str})"
            format_options.append(option)
        
        self.format_combo['values'] = format_options
        self.format_combo.set("Select Resolution")
    
    def set_format_details(self, fmt):
        """Display format details."""
        format_text = f"Extension: {fmt['ext']}\n"
        format_text += f"Video: {fmt['vcodec']}\n"
        format_text += f"Audio: {fmt['acodec']}\n"
        
        if fmt['filesize_mb'] > 0:
            format_text += f"Size: {fmt['filesize_mb']:.2f} MB\n"
        else:
            format_text += "Size: Unknown\n"
        
        if fmt['fps']:
            format_text += f"FPS: {fmt['fps']}"
        
        self.format_info_label.config(text=format_text)
    
    def load_thumbnail(self, thumb_data):
        """Load and display thumbnail."""
        try:
            self.original_thumbnail_data = thumb_data
            img = Image.open(BytesIO(thumb_data))
            img = img.resize((480, 270), Image.Resampling.LANCZOS)
            self.thumbnail_image = ImageTk.PhotoImage(img)
            self.thumbnail_label.config(image=self.thumbnail_image, text="")
        except:
            self.thumbnail_label.config(text="Thumbnail not available")
    
    def resize_thumbnail(self):
        """Resize thumbnail to fit frame."""
        if self.original_thumbnail_data:
            try:
                frame_width = self.thumbnail_frame.winfo_width()
                frame_height = self.thumbnail_frame.winfo_height()
                
                if frame_width > 100 and frame_height > 100:
                    img = Image.open(BytesIO(self.original_thumbnail_data))
                    
                    img_width, img_height = img.size
                    aspect = img_width / img_height
                    
                    if frame_width / frame_height > aspect:
                        new_height = frame_height - 20
                        new_width = int(new_height * aspect)
                    else:
                        new_width = frame_width - 20
                        new_height = int(new_width / aspect)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.thumbnail_image = ImageTk.PhotoImage(img)
                    self.thumbnail_label.config(image=self.thumbnail_image, text="")
            except:
                pass
    
    def update_progress(self, percent):
        """Update progress bar."""
        self.progress_bar['value'] = percent
        self.progress_label.config(text=f"{percent}%")
    
    def reset_progress(self):
        """Reset progress bar."""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
    
    def set_button_state(self, button_name, state, text=None, bg=None):
        """Set button state."""
        button = getattr(self, f"{button_name}_btn", None)
        if button:
            button.config(state=state)
            if text:
                button.config(text=text)
            if bg:
                button.config(bg=bg)
