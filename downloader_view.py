import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

root= tk.Tk()
root.title("Youtube Downloader")
#root.resizable(False,False)
root.geometry("700x800")

#backgroung
img = Image.open("images/bg3.jpg")
img = img.resize((600,800))
img_photo = ImageTk.PhotoImage(img)

label = tk.Label(root,image=img_photo)
label.place(x=50,y=0,relwidth=1, relheight=1)


label = tk.Label(root)
label.place(x=0,y=0,relwidth=0.34, relheight=1)

#header
heading = tk.Label(bg="#040227",fg="#00C3DD",text="YOUTUBE\nDOWNLOADER",font="arial 24 bold",justify="left")
heading.place(x=0,y=0)

#Entrybox
entry_box= tk.Entry(width=50,)


root.mainloop()