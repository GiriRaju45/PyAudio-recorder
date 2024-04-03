import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import pandas as pd
import wave
import pyaudio
import tkinter.filedialog as fd
import shutil
import os
import sys
from tkinter import messagebox
from pydub import AudioSegment
from PIL import Image, ImageTk
from utils.detect_silence import trim_silence  


base_dir = 'data'
my_styles = ["Select Style", "FEAR","PROPER NOUN","Happy","HAPPY","Sad","SAD","Disgust","DISGUST","BOOK","BB","WIKI","Surprise","SURPRISE","DIGI","ALEXA","NEWS","Anger","ANGER","INDIC","SANGRAH","CONV","UMANG"]
my_languages = ["Select Language",'DEMO','ASM', 'BEN', 'BRX', 'DOI', 'GUJ', 'HIN', 'KAN', 'KAS', 'KOK', 'MAI', 'MAL', 'MAR', 'MNI', 'NEP', 'ORI', 'PAN', 'SAN', 'SAT', 'SND', 'TAM', 'TEL', 'URD']
my_speakers = ["Select Speaker", 'Male','Female']
audio_types = ['48khz', '8khz']

class AudioRecorderApp:
    def __init__(self,master):
        self.master = master
        self.master.title('Audio Recorder App')
        self.count = 0
        self.duration = 0
        self.audio_recorder = AudioRecorder()
        self.current_index = 0
        self.data = None
        self.setup_menu()
        self.create_widgets()
        self.update_ui_with_sentence()
        
    def setup_menu(self):
        self.menubar = tk.Menu(self.master)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Select and Save CSV", command=self.select_and_save_csv)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Load CSV", command=self.load_csv)
        self.menubar.add_cascade(menu=self.filemenu, label="File")
        
        self.optionsmenu = tk.Menu(self.menubar, tearoff=0)
        self.optionsmenu.add_command(label="Select Date and Options", command=self.show_date_and_options_ui)
        self.menubar.add_cascade(menu=self.optionsmenu, label="Options")
        self.master.config(menu=self.menubar)
        
    def setup_date_selection(self):
        self.my_date = ttkb.DateEntry(self.master, bootstyle="superhero")
        self.my_date.pack(pady=20)
    
    def setup_dropdowns(self):
        self.style_var = tk.StringVar()
        self.styles_dropdown = ttk.Combobox(self.master, textvariable=self.style_var, values=my_styles)
        self.styles_dropdown.pack(pady=20)
        self.styles_dropdown.set('Select Style')

        self.language_var = tk.StringVar()
        self.languages_dropdown = ttk.Combobox(self.master, textvariable=self.language_var, values=my_languages)
        self.languages_dropdown.pack(pady=20)
        self.languages_dropdown.set('Select Language')
        
        self.speaker_var = tk.StringVar()
        self.speakers_dropdown = ttk.Combobox(self.master, textvariable=self.speaker_var, values=my_speakers)
        self.speakers_dropdown.pack(pady=20)
        self.speakers_dropdown.set('Select Speaker')
        
        self.microphone_var = tk.StringVar()
        self.microphones_dropdown = ttk.Combobox(self.master, textvariable=self.microphone_var, state='readonly')
        self.microphones_dropdown.pack(pady=20)
        self.microphones_dropdown.set('Select Microphone')
        
        self.update_microphone_dropdown()
        
        self.submit_btn = tk.Button(self.master, text="Submit", command=self.on_submit)
        self.submit_btn.pack(pady=20)
    
    def show_date_and_options_ui(self):
        self.setup_date_selection()
        self.setup_dropdowns() 
        
    def make_directory(self):
        language = self.language_var.get()
        style =self.style_var.get()
        speaker = self.speaker_var.get()
        self.current_date = self.my_date.entry.get().replace("/", "-")
        if language == 'Select Language' or style == 'Select Style' or speaker == 'Select Speaker':
            messagebox.showerror("ERROR!!", "Please select a valid option.")
        else:
            self.audio_dir = os.path.join(base_dir,language,speaker,style,self.current_date)
            os.makedirs(self.audio_dir, exist_ok=True)
            print(self.audio_dir)
            messagebox.showinfo("Success", "Directory Created")
    
    def on_submit(self):
        self.make_directory()
        
    def update_microphone_dropdown(self):
        # Get device info for each input device (microphone)
        self.pyaudio_instance = pyaudio.PyAudio()
        self.num_devices = self.pyaudio_instance.get_device_count()
        microphone_options = ['Select Microphone']
        for i in range(self.num_devices):
            device_info = self.pyaudio_instance.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                microphone_name = device_info['name']
                microphone_options.append(f"Microphone {i}: {microphone_name}")
        
        self.microphone_dropdown['values'] = microphone_options    

    def create_widgets(self):
        self.master.minsize(width=1536, height=480)  # Set the minimum size of the window

        main_frame = ttk.Frame(self.master)
        main_frame.pack(expand=True)
        
        self.audio_count = ttk.Label(main_frame, text=f"Audio Count: {self.count}", font=('Times New Roman', 18, 'bold'), width=24, bootstyle="success")
        self.audio_count.pack(pady=(20,0))

        self.audio_duration = ttk.Label(main_frame, text=f"Total Duration: {self.duration} minutes", font=('Times New Roman', 18, 'bold'), width=24, bootstyle="success")
        self.audio_duration.pack(pady=(20,0))

        self.text_id = ttk.Entry(main_frame, font=('Times New Roman', 18, 'bold'), width=24, bootstyle="success")
        self.text_id.bind('<Return>', self.load_entry_from_id)
        self.text_id.pack(pady=(16, 0))  # Padding only at the top

        bold_font = ('Arial Unicode MS', 22)  # Using 'Arial Unicode MS' for better Unicode character support
        self.text_sentence = tk.Text(main_frame, height=3, width=65, wrap="word", font=bold_font, spacing3=22)
        self.text_sentence.tag_configure("center", justify='center')
        self.text_sentence.pack(pady=20, padx=10)  # Padding on sides for the Text widget
        self.text_sentence.insert("1.0", "Please use the load CSV option in the File menu to display the sentence.")
        style = ttk.Style()
        style.configure('NoBorder.TButton', borderwidth=0, highlightthickness=0)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=0)
        
        def resource_path(relative_path):
            """ Get the absolute path to the resource, works for dev and for PyInstaller """
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        def create_button_with_image(frame, image_path, command, style=None):
            original_img = Image.open(image_path)
            if command in {self.play_audio,self.previous_sentence,self.next_sentence}:
                resized_img = original_img.resize((90, 50), Image.Resampling.LANCZOS)
            else:
                resized_img = original_img.resize((60, 60), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(resized_img)
            button = ttk.Button(frame, image=img, command=command, style=style)
            button.image = img  
            return button

        self.btn_play = create_button_with_image(buttons_frame, resource_path('static_files/play3.jpg'), self.play_audio, style='NoBorder.TButton')
        self.btn_stop = create_button_with_image(buttons_frame, resource_path('static_files/stop.png'), self.stop_recording_or_playing, style='NoBorder.TButton')
        self.btn_record = create_button_with_image(buttons_frame, resource_path('static_files/record1.jpg'), self.start_recording, style='NoBorder.TButton')
        self.btn_save = create_button_with_image(buttons_frame, resource_path('static_files/save1.png'), self.save_audio, style='NoBorder.TButton')
        self.btn_previous = create_button_with_image(buttons_frame, resource_path('static_files/prev1.jpg'), self.previous_sentence, style='NoBorder.TButton')
        self.btn_next = create_button_with_image(buttons_frame, resource_path('static_files/next1.jpg'), self.next_sentence, style='NoBorder.TButton')

        self.btn_play.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_stop.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_record.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_save.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_previous.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_next.pack(side=tk.LEFT, padx=32, pady=5)