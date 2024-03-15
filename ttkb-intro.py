import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from PIL import Image, ImageTk

def start_recording():
    print("Recording started...")  # Placeholder for your recording logic

# Initialize your Tkinter window
root = ttkb.Window(themename='litera')

# Load and resize the image using Pillow
original_img = Image.open(r'C:\Users\richa\Downloads\TTS_DC\tkinter\800px-Auto_Racing_Red_Circle.svg.png')
# Use Image.Resampling.LANCZOS for high-quality downsampling
resized_img = original_img.resize((50, 50), Image.Resampling.LANCZOS)

# Convert the resized image to a format suitable for Tkinter
record_img = ImageTk.PhotoImage(resized_img)

# Create a button with the resized image
style = ttk.Style()
style.configure('NoFocus.TButton', highlightthickness=0)
btn_record = ttk.Button(root, image=record_img, command=start_recording)
btn_record['takefocus'] = 0
btn_record.pack(pady=20, padx=20)

root.mainloop()
