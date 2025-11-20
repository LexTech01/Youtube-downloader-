import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)
ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("dark")

class VideoView:
    def __init__(self, root):
        self.root = root
        self.root.title("WinBix Youtube Videos Downloader")
        self.root.geometry("850x950")
        self.root.minsize(800, 930)
        self.root.configure(fg_color="#5C899D")

        # Title
        self.title_label = ctk.CTkLabel(root, text="WinBix Youtube Videos Downloader",
                                        font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.pack(pady=70)

        # Main frame
        self.frame = ctk.CTkLabel(root, corner_radius=80, fg_color="#FFFCEF", height=650, width=650)
        self.frame.place(relx=0.5, rely=0.55, anchor="center")

        # Thumbnail
        self.placeholder = ctk.CTkLabel(self.frame, corner_radius=20, text="No Video Loaded",text_color="white",
                                        fg_color="#0A0707", bg_color="#FFFCEF")
        self.placeholder.place(relx=0.28, rely=0.05, relwidth=0.45, relheight=0.35)

        # Entry field
        self.entry = ctk.CTkEntry(self.frame, width=15, fg_color="#000000", bg_color="#FAFAFA", corner_radius=10,text_color="white")
        self.entry.place(relx=0.1, rely=0.64, relwidth=0.62)

        self.label = ctk.CTkLabel(self.frame, text="Paste Url Here:", text_color="black",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        self.label.place(relx=0.168, rely=0.583, relwidth=0.2)

        # Buttons
        self.download_btn = ctk.CTkButton(self.frame, text='DOWNLOAD VIDEO', bg_color="#FFFCEF",
                                          corner_radius=15, border_width=2)
        self.download_btn.place(relx=0.48, rely=0.7, relwidth=0.42, relheight=0.07)

        self.load_btn = ctk.CTkButton(self.frame, text='LOAD', bg_color="#FFFCEF",
                                      corner_radius=10, border_width=2)
        self.load_btn.place(relx=0.774, rely=0.64, relwidth=0.12)

        # Resolution
        self.res_var = ctk.StringVar(value="Resolution")
        self.res_menu = ctk.CTkOptionMenu(self.frame, values="select", variable=self.res_var)
        self.res_menu.place(relx=0.1, rely=0.7, relwidth=0.2)

        # Progress & labels
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=300, height=20, progress_color="#5C899D")
        self.progress_bar.place(relx=0.1, rely=0.8, relwidth=0.8, relheight=0.05)
        self.progress_bar.set(0)

        self.video_title = ctk.CTkLabel(self.frame, text="", text_color="black",
                                        font=ctk.CTkFont(size=12, weight="bold"),
                                        wraplength=250, justify="center")
        self.video_title.place(relx=0.28, rely=0.42, relwidth=0.45, relheight=0.08)

        self.details_label = ctk.CTkLabel(self.frame, text="", text_color="black",
                                          font=ctk.CTkFont(size=11))
        self.details_label.place(relx=0.1, rely=0.87, relwidth=0.8, relheight=0.06)

        # History Button
        self.history_btn = ctk.CTkButton(root, text="Download History", width=630, height=40, corner_radius=20)
        self.history_btn.pack(side="bottom", pady=40)
    
    # Popup message
    def show_message(self, title, message):
        popup = ctk.CTkToplevel(self.root)
        popup.title(title)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(fg_color="#110F0F",)
        popup.attributes("-alpha", 0.9)

        # Center
        self.root.update_idletasks()
        root_x, root_y = self.root.winfo_x(), self.root.winfo_y()
        root_w, root_h = self.root.winfo_width(), self.root.winfo_height()
        popup_w, popup_h = 420, 170
        pos_x = root_x + (root_w // 2) - (popup_w // 2)
        pos_y = root_y + (root_h // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{pos_x}+{pos_y}")

        lbl = ctk.CTkLabel(popup, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        lbl.place(relx=0.05, rely=0.08, relwidth=0.9, relheight=0.22)

        msg_lbl = ctk.CTkLabel(popup, text=message, wraplength=380, justify="left",text_color="white")
        msg_lbl.place(relx=0.05, rely=0.32, relwidth=0.9, relheight=0.4)

        ok_btn = ctk.CTkButton(popup, text="OK", command=popup.destroy,
                               fg_color="#ffcc00", text_color="black")
        ok_btn.place(relx=0.38, rely=0.76, relwidth=0.24, relheight=0.14)
