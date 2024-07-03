import tkinter as tk
from tkinter import *
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import pandas as pd
import numpy as np
import time 
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyaudio
import tkinter.filedialog as fd
import shutil
import os 
import requests
import threading
import sys
import cProfile
from tkinter import messagebox
from pydub import AudioSegment
import subprocess
from PIL import Image, ImageTk
#import multiprocessing
import pyglet
import wave
import pyinstrument
from memory_profiler import profile


from utils.detect_silence import trim_silence  
from utils.manual_trim import trim_audio

base_dir = 'data'
my_styles = ["Select Style", "FEAR","PROPER NOUN","Happy","HAPPY","Sad","SAD","Disgust","DISGUST","BOOK","BB","WIKI","Surprise","SURPRISE","DIGI","ALEXA","NEWS","Anger","ANGER","INDIC","SANGRAH","CONV","UMANG"]
my_languages = ["Select Language",'DEMO','ASM', 'BEN', 'BRX', 'DOI', 'GUJ', 'HIN', 'KAN', 'KAS', 'KOK', 'MAI', 'MAL', 'MAR', 'MNI', 'NEP', 'ORI', 'PAN', 'SAN', 'SAT', 'SND', 'TAM', 'TEL', 'URD']
my_speakers = ["Select Speaker", 'Male','Female']
audio_types = ['48khz', '8khz']
    
class AudioRecorder:
    def __init__(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.format = pyaudio.paInt16  # Defined as a class attribute for reuse
        self.channels = 1
        self.rate_48000 = 48000
        self.rate_8000 = 8000
        self.frames_per_buffer = 512 
        self.rec_data = None
        self.frames_48000 = []
        self.frames_8000 = []
        self.is_recording = False
        self.stream = None

    def start_recording(self, device_index_48k=None, device_index_8k = None):
        self.stream_48000 = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate_48000,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index_48k,
        )
        self.stream_8000 = self.pyaudio_instance.open(format=self.format,
            channels=self.channels,
            rate=self.rate_8000,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index_8k,)
        
        self.is_recording = True
        self.recording_thread_48000 = threading.Thread(target=self._record_loop, args=(self.stream_48000, self.frames_48000, self.rate_48000))
        self.recording_thread_8000 = threading.Thread(target=self._record_loop, args=(self.stream_8000, self.frames_8000, self.rate_8000))
        self.recording_thread_48000.start()
        self.recording_thread_8000.start()
        
        


    def _record_loop(self, stream, frames, rate):
        while self.is_recording:
            try:
                data = stream.read(self.frames_per_buffer, exception_on_overflow=False)
                ##print(data)
                frames.append(data)

            except:
                KeyboardInterrupt
                #print('Keyboard Interupt')
                return
            ##print(data)
            
    def stop_recording(self):
        if self.is_recording: 
            self.is_recording = False   
            self.recording_thread_48000.join()  
            self.recording_thread_8000.join()

            self.stream_48000.stop_stream()
            self.stream_8000.stop_stream()
            self.stream_48000.close()
            self.stream_8000.close()
            
    def save_recording(self, filename, audio_dir):
        if not self.frames_48000 or not self.frames_8000:
            #print("No audio to save.")
            return
        self.audio_dir_48khz = os.path.join(audio_dir, '48khz')
        self.audio_dir_8khz = os.path.join(audio_dir, '8khz')
        os.makedirs(self.audio_dir_8khz, exist_ok= True)
        os.makedirs(self.audio_dir_48khz, exist_ok=True)    

        self.audio_segment_48000 = self._create_audio_segment(self.frames_48000, 48000)
        self.audio_segment_8000 = self._create_audio_segment(self.frames_8000, 8000)

        trimmed_wav_48k, duration_48k = trim_silence(self.audio_segment_48000)
        output_filename_48k = os.path.join(self.audio_dir_48khz, f"{filename}")
        trimmed_wav_48k.export(output_filename_48k, format='wav')
        trimmed_wav_8k, duration_8k = trim_silence(self.audio_segment_8000)
        output_filename_8k = os.path.join(self.audio_dir_8khz, f"{filename}")
        trimmed_wav_8k.export(output_filename_8k, format = 'wav')

        return duration_48k

    def _create_audio_segment(self, frames, rate):
        buffer = b''.join(frames)
        return AudioSegment(buffer, sample_width=self.pyaudio_instance.get_sample_size(self.format),
                            channels=self.channels, frame_rate=rate)

    def record(self, data):
        self.frames.append(data)
    
#################################################################################
class Extra(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Second Display') 

#################################################################################   

class CustomProgressBar(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.canvas = tk.Canvas(self, width=1204, height=50, highlightthickness=0)
        self.canvas.pack(side='top', fill='x', padx= 5)

        # Draw the scale with numbers from -50 to 0
        for i in range(-50, 1, 2):  # Step by 2 to display every other number
            if i == -50:
                x = 1
                i = ''
            else:
                x = (i + 50) * 1200 / 50
            self.canvas.create_text(x, 30, text=str(i), anchor='n', fill = '#B8B8B8')#'#FA5252')


        
        self.progress = ttk.Progressbar(self, orient="horizontal", length=1200, mode="determinate", maximum= 50)
        self.progress.pack(side= 'bottom', expand=False, ipady=25)

        db_style = ttk.Style()
        #db_style.theme_use('default')
        db_style.configure('green.Horizontal.TProgressbar', foreground='green', background='green')
        db_style.configure('yellow.Horizontal.TProgressbar', foreground='yellow', background='yellow')
        db_style.configure('red.Horizontal.TProgressbar', foreground='red', background='red')

    def update_color(self, x):
        x = max(-50, x)
        value = 50 - abs(x)
        # #print(value)
        if 0 <= value <= 22:
            self.progress['style'] = 'green.Horizontal.TProgressbar'
        elif 22 < value <= 38:
            self.progress['style'] = 'yellow.Horizontal.TProgressbar'
        elif 38 < value <= 50:
            self.progress['style'] = 'red.Horizontal.TProgressbar'

    def reset_progress(self):
        self.update_color(-50)
        self.update()
        self.progress['value'] = 0.0

#########################################################################
class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Audio Recorder App')
        self.count = 0
        self.duration = 0
        self.audio_recorder = AudioRecorder()
        self.db_level = CustomProgressBar(self.master)
        self.db_level.pack(side= 'bottom')
        self.db_pyaud_instance = pyaudio.PyAudio()
        self.db_stream = None
        self.current_index = 0 # Keep track of the current sentence
        self.data = None # Load your CSV data here
        self.setup_menu()
        self.screen_width = self.master.winfo_screenwidth()
        # self.create_gui() 
        self.create_widgets()
        self.update_ui_with_sentence()  # Add this line to load the first sentence on startu
        self.audio_dir = ''
        self.play_start_time = 0
        self.paused_position = 0
        self.playback_frame = None
        self.flag = 1
        self.save_aud = False
        self.trimmed_audio = None
        self.trimmed_audio_48k = None
        self.trimmed_audio_8k = None
        
      #  self.master.after(100, self.update_db_level())

    def setup_menu(self):
        # Create menu
        # Add a menu bar for CSV handling
        self.menubar = tk.Menu(self.master)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)        
        self.filemenu.add_command(label="Select and Save CSV", command=self.select_and_save_csv)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Load CSV", command=self.load_csv)
        self.menubar.add_cascade(menu=self.filemenu, label="File")
        
        self.master.config(menu=self.menubar)   


    def show_date_and_options_ui(self):
        self.setup_date_selection()
        self.setup_dropdowns() 
            
    
    def make_directory(self):
        now = datetime.datetime.now()
        self.unique_id = now.strftime("%Y%m%d%H%M%S")
        language = self.language_var.get()
        style =self.style_var.get()
        speaker = self.speaker_var.get()
        self.current_date = self.my_date.entry.get().replace("/", "-")
        if language == 'Select Language' or style == 'Select Style' or speaker == 'Select Speaker':
            self.popup_message("ERROR!! Please select a valid option to create the folder")
        else:
            self.audio_dir = os.path.join(base_dir,language,speaker,style,self.unique_id)
            os.makedirs(self.audio_dir, exist_ok=True)
            #print(self.audio_dir)
            self.popup_message("Success! Directory Created")
            #self.master.after(2000, success_message.destroy)
            
    def on_submit(self):
        self.make_directory()
        # self.create_gui() 

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
        
        # Update dropdown options
        self.microphone_dropdown['values'] = microphone_options
        self.microphone_dropdown_8k['values'] = microphone_options

    def create_second_window(self):
        global second_window
        second_window = Extra()
        if hasattr(self, 'second_window') and second_window.winfo_exists():
            second_window.lift()  
            return
        
        second_window.protocol("WM_DELETE_WINDOW", self.on_secondary_window_close)
        self.toggle_window_btn.config(text="Close Window2")
        display_frame=ttk.Frame(second_window)
        display_frame.pack(pady=20,padx=20)
        self.display_text_id=ttk.Entry(display_frame, font=('Times New Roman', 18, 'bold'), width=24, bootstyle="danger")
        self.display_text_id.pack(pady=(16, 0))
        self.display_text_id.insert(0, self.text_id.get())
        self.display_text_sentence = tk.Text(display_frame, height=3, width=65, wrap="word", font=('Arial Unicode MS', 20), spacing1=10, spacing2=10, spacing3=10)
        self.display_text_sentence.pack(pady=20, padx=10) 
        self.display_text_sentence.insert("1.0", self.text_sentence.get("1.0", tk.END)) 
        self.text_id.bind('<KeyRelease>', self.sync_text_id)
        self.display_text_id.bind('<KeyRelease>', self.sync_display_text_id)
        self.text_sentence.bind('<KeyRelease>', self.sync_text_sentence)
        self.display_text_sentence.bind('<KeyRelease>', self.sync_display_text_sentence)
       
    def toggle_secondary_window(self):
        if self.flag == 1:
            self.create_second_window()
            self.flag = 0
            self.toggle_window_btn.config(text="Close Window2")
        else:
            second_window.destroy()
            self.flag = 1
            self.toggle_window_btn.config(text="Open Window2")
    
    def on_secondary_window_close(self):
        second_window.destroy()
        self.flag = 1
        self.toggle_window_btn.config(text="Open Window2")
        
    def sync_text_id(self, event=None):
        self.display_text_id.delete(0, tk.END)
        self.display_text_id.insert(0, self.text_id.get())
    
    def sync_display_text_id(self, event=None):
        self.text_id.delete(0, tk.END)
        self.text_id.insert(0, self.display_text_id.get())

    def sync_text_sentence(self, event=None):
        self.display_text_sentence.delete("1.0", tk.END)
        self.display_text_sentence.insert("1.0", self.text_sentence.get("1.0", tk.END))

    def sync_display_text_sentence(self, event=None):
        self.text_sentence.delete("1.0", tk.END)
        self.text_sentence.insert("1.0", self.display_text_sentence.get("1.0", tk.END))

    def remove_focus(self, event = None):
        #print('function called..')
        self.text_sentence.focus_set()
        #self.text_sentence.focus_get
    def root_focus(self, event = None):
        self.master.focus_set()
        
    def open_directory(self):
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(self.audio_recorder.audio_dir_48khz)
            elif os.name == 'posix':  # For Linux, macOS
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', self.audio_recorder.audio_dir_48khz])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open the directory: {e}")

    def create_gui(self):
        # Create a button to open the directory
        open_dir_button = ttk.Button(self.master, text="Open Directory", command=lambda: self.open_directory)
        button_x_position = self.screen_width/2 + 500
        open_dir_button.place(x=button_x_position,y=150)

    def check_focus_and_act(self,event):
            focused_widget = self.master.focus_get()
            if focused_widget == self.text_id:
                # print("Focus is on text_id widget")
                # Handle left/right arrow key when focus is on text_id
                pass
            elif focused_widget == self.text_sentence:
                # print("Focus is on text_sentence widget")
                # Handle left/right arrow key when focus is on text_sentence
                pass
            else:
                if event.keysym == 'Left':
                    self.previous_sentence()
                elif event.keysym == 'Right':
                    self.next_sentence()

    def default_copy(self, event, widget):
        widget.event_generate('<<Copy>>')

    def default_paste(self, event, widget):
        widget.event_generate('<<Paste>>')

    def default_undo(self, event, widget):
        widget.event_generate('<<Undo>>')

    def create_widgets(self): 
              
        self.master.minsize(width=1536, height=480)  # Set the minimum size of the window

        drop_frame = ttk.Frame(self.master)
        drop_frame.pack(pady =(0,10))

        self.my_date = ttkb.DateEntry(drop_frame, bootstyle="flatly")
        self.my_date.pack(pady=(40, 0), padx = 30, side = tk.LEFT)

        self.style_var = tk.StringVar()
        self.styles_dropdown = ttk.Combobox(drop_frame, textvariable=self.style_var, values=my_styles)
        self.styles_dropdown.pack(pady= (40, 0), padx = 10, side = tk.LEFT)
        self.styles_dropdown.set('Select Style')
        
        # Languages Dropdown
        self.language_var = tk.StringVar()
        self.languages_dropdown = ttk.Combobox(drop_frame, textvariable=self.language_var, values=my_languages)
        self.languages_dropdown.pack(pady=(40, 0), padx = 10, side = tk.LEFT)
        self.languages_dropdown.set('Select Language')
        
        # Speaker Dropdown
        self.speaker_var = tk.StringVar()
        self.speakers_dropdown = ttk.Combobox(drop_frame, textvariable=self.speaker_var, values=my_speakers)
        self.speakers_dropdown.pack(pady=(40, 0), padx = 10, side = tk.LEFT)
        self.speakers_dropdown.set('Select Speaker')

        # Microphone Dropdown
        self.microphone_var = tk.StringVar()
        self.microphone_dropdown = ttk.Combobox(drop_frame, textvariable=self.microphone_var, state='readonly')
        self.microphone_dropdown.pack(pady=(40, 0), padx = 10, side = tk.LEFT)
        self.microphone_dropdown.set('Select 48000 Hz - Microphone')

        self.microphone_var_n = tk.StringVar()
        self.microphone_dropdown_8k = ttk.Combobox(drop_frame, textvariable=self.microphone_var_n, state='readonly')
        self.microphone_dropdown_8k.pack(pady=(40, 0), padx = 10, side = tk.LEFT)
        self.microphone_dropdown_8k.set('Select 8000 Hz - Microphone')
        self.update_microphone_dropdown()

        # Add a submit button
        self.submit_btn = tk.Button(drop_frame, text="Submit", command=self.on_submit)
        self.submit_btn.pack(pady=(40, 0), padx = 10, side = tk.LEFT)

        main_frame = ttk.Frame(self.master)
        main_frame.pack(pady= (30, 0),expand=False)

        self.audio_count = ttk.Label(main_frame, text=f"Audio Count: {self.count}", font=('Times New Roman', 18, 'bold'), width=24, bootstyle="success", foreground= '#FA5252')
        self.audio_count.pack()

        self.total_aud_duration = ttk.Label(main_frame, text=f"Total Duration: {self.duration} minutes", font=('Times New Roman', 18, 'bold'), width=24, bootstyle="success", foreground= '#FA5252')
        self.total_aud_duration.pack()

        self.text_id = ttk.Entry(main_frame, font=('Times New Roman', 18, 'bold'), width=24, bootstyle="danger")
        self.text_id.bind('<Return>', self.load_entry_from_id)
        self.text_id.pack(pady=(16, 0))  # Padding only at the top

        bold_font = ('Arial Unicode MS', 27, 'bold')  # Using 'Arial Unicode MS' for better Unicode character support
        self.text_sentence = tk.Text(main_frame, height=3, width=60, wrap="word", font=bold_font, spacing1=10, spacing2=10, spacing3=10)
        self.text_sentence.tag_configure("center", justify='center')
        self.text_sentence.pack(pady=20, padx=10)  # Padding on sides for the Text widget
        self.text_sentence.insert("1.0", "Please use the load CSV option in the File menu to display the sentence.")
        style = ttk.Style()
        style.configure('NoBorder.TButton', borderwidth=0, highlightthickness=0)
        style.map('NoBorder.TButton', foreground = [('disabled','#0D2740'), (('active', 'blue'))])      
        
        open_dir_button = ttk.Button(self.master, text="Open Directory", command=self.open_directory)
        dir_button_x_position = self.screen_width/2 + 400
        open_dir_button.place(x=dir_button_x_position,y=150)

        # Frame for buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=0, expand= True)
        sec_buttons_frame = ttk.Frame(main_frame)
        sec_buttons_frame.pack(pady=2, expand= True)
 
#######################################################################################################################################
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
                resized_img = original_img.resize((60, 50), Image.Resampling.LANCZOS)
            else:
                resized_img = original_img.resize((60, 60), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(resized_img)
            button = ttk.Button(frame, image=img, command=command, style=style)
            button.image = img  
            return button
        
      
        
        self.toggle_window_btn = ttk.Button(self.master, text="Open Window2", command=self.toggle_secondary_window, style='NoBorder.TButton')
        #self.toggle_window_btn.pack(side='left', pady=(0, 50), padx= (20,0))
        self.toggle_window_btn.place(x = 20, y=150)
        self.btn_play = create_button_with_image(buttons_frame, resource_path('static_files/icons8-play-button-100.png'), self.play_audio_file, style='NoBorder.TButton')
        self.btn_stop = create_button_with_image(buttons_frame, resource_path('static_files/icons8-stop-100.png'), self.stop_recording_or_playing, style='NoBorder.TButton')
        self.btn_record = create_button_with_image(buttons_frame, resource_path('static_files/icons8-microphone-100.png'), self.start_recording, style='NoBorder.TButton')
        self.btn_save = create_button_with_image(buttons_frame, resource_path('static_files/icons8-save-button-100.png'), self.save_audio, style='NoBorder.TButton')
        self.btn_previous = create_button_with_image(buttons_frame, resource_path('static_files/icons8-previous-96-2.png'), self.previous_sentence, style='NoBorder.TButton')
        self.btn_next = create_button_with_image(buttons_frame, resource_path('static_files/icons8-last-100.png'), self.next_sentence, style='NoBorder.TButton')
       
        self.btn_previous.pack(side=tk.LEFT, padx=32,pady = 2)
        self.btn_play.pack(side=tk.LEFT, padx=32,pady = 2)
        self.btn_record.pack(side=tk.LEFT, padx=32,pady = 2)
        self.btn_stop.pack(side=tk.LEFT, padx=32,pady = 2)
        self.btn_save.pack(side=tk.LEFT, padx=32,pady = 2)
        self.btn_next.pack(side=tk.LEFT, padx=32,pady = 2)
        self.master.bind("<Control-s>", lambda event: self.save_audio())
        self.master.bind("<Control-n>", lambda event: self.next_sentence())
        self.master.bind("<Control-p>", lambda event: self.play_audio_file())
        self.master.bind('<Button-2>', self.root_focus)
        self.master.bind("<Left>", lambda event: self.check_focus_and_act(event))
        self.master.bind("<Right>", lambda event: self.check_focus_and_act(event))

        self.text_id.bind('<Control-c>', lambda event: self.default_copy(event, self.text_id))
        self.text_id.bind('<Control-v>', lambda event: self.default_paste(event, self.text_id))
        self.text_id.bind('<Control-z>', lambda event: self.default_undo(event, self.text_id))

        self.text_sentence.bind('<Control-c>', lambda event: self.default_copy(event, self.text_sentence))
        self.text_sentence.bind('<Control-v>', lambda event: self.default_paste(event, self.text_sentence))
        self.text_sentence.bind('<Control-z>', lambda event: self.default_undo(event, self.text_sentence))
    


    def rec_indication(self, image_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
            
        image_path= os.path.join(base_path, image_path)
        original_img = Image.open(image_path)
    
        resized_img = original_img.resize((60, 50), Image.Resampling.LANCZOS)
        button_x_position = self.screen_width/2 - 300
        img = ImageTk.PhotoImage(resized_img)
        button = ttk.Button(self.master, image=img, style= 'NoBorder.TButton')
        button.image = img  
        button.place(x=button_x_position, y=150)

########################################################################################################################################
    def save_text_to_csv(self):
        updated_text = self.text_sentence.get("1.0", "end-1c").strip()
        if self.data is not None and 0 <= self.current_index < len(self.data):
            self.data.loc[self.current_index, 'Sentence'] = updated_text
            self.data.to_csv(self.csvpath, index=False)
            
            
            self.data.at[self.current_index, 'Sentence'] = updated_text
            filename = f"{self.current_date}_{self.current_language}_{self.current_speaker}_{self.current_style}.csv"
            save_path = os.path.join(self.audio_dir, filename)
            self.data.to_csv(save_path, index=False)
            print(f"Data saved successfully to {save_path}.")
        else:
            print("No data loaded or index out of range.")
            
      
    def load_entry_from_id(self, event=None):
        entered_id = self.text_id.get().strip()          
        matching_index = self.data.index[self.data['ID']==entered_id].tolist()
        
        if matching_index and self.current_index != matching_index:
            self.current_index = matching_index[0]
            self.update_ui_with_sentence()
            if self.playback_frame is not None:
               self.playback_frame.destroy()
            self.audio_recorder.frames_48000 = []
            self.audio_recorder.frames_8000 = []
        elif matching_index == self.current_index:
            pass
        else:
            #print("ID not found.")
            self.popup_message('ID not found. Please enter a valid ID', destroy_duration= 2000)
        self.play_audio_file()
        
    
    def update_ui_with_row(self, row):
        self.text_sentence.delete("1.0", tk.END)
        self.text_sentence.insert("1.0", str(row['Sentence']))
        self.current_style = row['style']
        self.current_category = row['category']
        self.current_speaker = row['speaker']
        self.current_language = row['language']

    def update_ui_with_sentence(self): 
        if self.data is not None and not self.data.empty and 0 <= self.current_index < len(self.data):
            # Fetching current row based on self.current_index
            current_row = self.data.iloc[self.current_index]

            # Updating the UI elements
            self.text_id.delete(0, tk.END)
            self.text_id.insert(0, str(current_row['ID']))
            # Update the Sentence Text widget
            # Apply the center alignment tag to the entire content of the Text widget
            self.text_sentence.tag_add("center", "1.0", "end")
            self.text_sentence.delete("1.0", tk.END)  # Clear existing content
            self.text_sentence.insert("1.0", str(current_row['Sentence']))  # Insert new content

            # Storing style, category, speaker, and language for backend use
            self.current_style = current_row['style']
            self.current_category = current_row['category']
            self.current_speaker = current_row['speaker']
            self.current_language = current_row['language']
        else:
            self.text_id.delete(0, tk.END)
            self.text_sentence.delete("1.0", tk.END)
            self.text_sentence.insert("1.0", "Please load a CSV file to display entries.")

        if hasattr(self, 'display_text_sentence'):
            self.display_text_id.delete(0, tk.END)
            self.display_text_id.insert(0, str(current_row['ID']))
            self.display_text_sentence.delete("1.0", tk.END)
            self.display_text_sentence.insert("1.0", str(current_row['Sentence']))

    def select_and_save_csv(self):
        filepath = fd.askopenfilename(filetypes=[("Upload TRANSCRIPT", "*.csv")])
        if not filepath:
            return
        target_folder = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.basename(filepath)
        self.target_path = os.path.join(target_folder, filename)
        shutil.copy(filepath, self.target_path)

        #print(f"File saved to {self.target_path}")
        
    def load_csv(self):
        self.csvpath = fd.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.csvpath:
            self.data = pd.read_csv(self.csvpath)
            self.current_index = 0
            self.update_ui_with_sentence()

    def play_audio(self):
        id = self.text_id.get().strip()
        filename = os.path.join(self.audio_dir,f"{id}.wav")
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Audio file {filename} does not exists.")
            self.master.after(2000, self.destroy_messagebox)
            return
        threading.Thread(target=self.play_audio_file, args=(filename,)).start()
        
    def play_audio_file(self):
        id = self.text_id.get().strip()
        filename = os.path.join(self.audio_dir, '48khz',f"{id}.wav")
        if os.path.exists(filename):
            self.popup_message('Loading Audio', 1000) 
            self.playback_seekbar(audio_file_name= filename, audio_file_name_8k= filename.replace('48khz', '8khz'))  
        elif self.audio_recorder.frames_48000 != []:
            self.playback_seekbar()
        else:
            self.popup_message('No audio to play!', 1000)
            if self.playback_frame is not None:
               self.playback_frame.destroy()

    def start_recording(self, event=None):
        
        self.save_aud = False
        self.rec_indication('static_files/red.png')
        self.audio_recorder.frames_48000=[]
        self.audio_recorder.frames_8000=[]
        
        if self.audio_dir == '':
            self.popup_message('ERROR!! please select the style, language and speak to create the respective folder before starting to  record', destroy_duration= 4000)
        else:
            index_48k = int(self.microphone_dropdown.get().split(' ')[1].replace(':', ''))
            index_8k = int(self.microphone_dropdown.get().split(' ')[1].replace(':', ''))
            self.popup_message('Recording started!!')
            self.audio_recorder.start_recording(device_index_48k= index_48k, device_index_8k= index_8k)
            #print(self.audio_recorder.is_recording)
            self.db_stream =  self.db_pyaud_instance.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=48000,
                                input=True,
                                frames_per_buffer=512,
                                input_device_index= index_48k)
            
            self.update_db_value = self.master.after(75, self.update_db_level)


    def update_db_level(self):
        #self.db_level.delete('progress')
         if self.audio_recorder.is_recording:
            try:
                data = self.db_stream.read(512, exception_on_overflow=False)
                seg = AudioSegment(b''.join([data]), sample_width=2, channels=1, frame_rate=48000)
                #print(len(seg))
                
                #print(seg.dBFS)
                db_value = seg.dBFS
                if db_value == -np.inf:
                    db_value = -50
                value = 50 - abs(db_value)
                self.db_level.update_color(db_value)
                self.db_level.progress['value'] = value
                # Schedule the next update after 100ms
                #time.sleep(0.1)
                #self.db_level.delete('progress')
                self.update_db_value = self.master.after(75, self.update_db_level)
                
            except Exception as e:

                print("Error while updating DB level:", e)
    
    def stop_recording_or_playing(self , event = None):
        self.rec_indication('static_files/orange.png')
        self.audio_recorder.stop_recording()
        if self.db_stream.is_active():
            self.db_stream.stop_stream()
        self.db_stream.close()
        # Cancel further updates to the progress bar
        self.master.after_cancel(self.update_db_value)
        self.popup_message('Recording stopped')
        self.db_level.reset_progress()
        self.playback_seekbar()    

    def save_audio(self):
        self.save_aud = True
        self.rec_indication('static_files/green.png')
        self.save_text_to_csv()
        id = self.text_id.get()
        sentence = self.text_sentence.get("1.0", "end-1c")
        filename = f"{id}.wav" 

        if (self.trimmed_audio is not None) and (self.trimmed_audio_8k is not None):
            audio_duration = self.trimmed_audio.duration_seconds*1000 #converting seconds to milli-seconds
            self.audio_dir_48khz = os.path.join(self.audio_dir, '48khz')
            self.audio_dir_8khz = os.path.join(self.audio_dir, '8khz')
            os.makedirs(self.audio_dir_8khz, exist_ok= True)
            os.makedirs(self.audio_dir_48khz, exist_ok=True)    

            # trimmed_wav_48k, duration_48k = trim_silence(self.audio_segment_48000)
            output_filename_48k = os.path.join(self.audio_dir_48khz, f"{filename}")
            self.trimmed_audio.export(output_filename_48k, format='wav')
            # trimmed_wav_8k, duration_8k = trim_silence(self.audio_recorder.audio_segment_8000)
            output_filename_8k = os.path.join(self.audio_dir_8khz, f"{filename}")
            self.trimmed_audio_8k.export(output_filename_8k, format = 'wav')
        else:
            audio_duration = self.audio_recorder.save_recording(filename, self.audio_dir)
        if audio_duration is None:
            self.popup_message('No audio to save..', 2000)
            return
        else:
            self.rec_indication('static_files/green.png')
            file_path_48khz = os.path.join(self.audio_dir,'48khz', filename)
            file_path_8khz = os.path.join(self.audio_dir,'8khz', filename)

        data = {               
            "easy_id": self.current_date,
            "Sentence": sentence,
            "speaker": self.current_speaker,
            "language": self.current_language,
            "style": self.current_style,
            "category": self.current_category,
            "data_id": id
        }
        
        files = {
            'audio_file_48khz': (filename, open(file_path_48khz,'rb'), 'audio/wav')
            #'audio_file_8khz': (filename, open(file_path_8khz,'rb'), 'audio/wav')
        }
        response = requests.post('http://tts-dc-prod.centralindia.cloudapp.azure.com:8094/audio_upload', files=files,data=data)
        files['audio_file_48khz'][1].close()
        #files['audio_file_8khz'][1].close()
        print(audio_duration)
        if response.ok:
            self.count += 1
            print(audio_duration)
            added_seconds = audio_duration / 1000
            self.duration += added_seconds
            print('added_seconds: ', added_seconds)
            print("Successfully uploaded the audio file and metadata.")
            print('durations: ', self.duration)
            # Calculate hours, minutes, and seconds
            hours, remainder = divmod(self.duration, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format the string to display as H:M:S
            duration_str = f"{int(hours)}:{int(minutes):02}:{int(seconds):02}"  # format as H:M:S with leading zeros for M and S

            # Update the labels
            self.audio_count.config(text=f"Audio Count: {self.count}")
            self.total_aud_duration.config(text=f"Duration: {duration_str}")
        else:
            print(f"Failed to upload the audio file. Status code: {response.status_code}, Response: {response.text}")
        if audio_duration is None:
            self.popup_message('Error! No audio to save!!', destroy_duration= 2000)
        else:
            self.next_sentence()
            if os.path.exists('trimmed.wav'):
                os.remove('trimmed.wav')

    def previous_sentence(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_ui_with_sentence()
            self.play_audio_file()


    def next_sentence(self):
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.update_ui_with_sentence()
            self.audio_recorder.frames_48000 = []
            self.audio_recorder.frames_8000 = []
            if self.playback_frame is not None:
               self.playback_frame.destroy()
    
    def popup_message(self, message : str, destroy_duration = 750):
        top = Toplevel()
        top.title('To note.')
        top.attributes('-topmost', True)
        top.geometry(newGeometry='200x200+2+50')
        Message(top, text=message, padx=20, pady=20).pack()
        top.after(destroy_duration, top.destroy)

    def trim(self):

        if os.path.exists('trimmed.wav') and os.path.exists('trimmed_8k.wav'):    
            self.trimmed_audio =  trim_audio('trimmed.wav', float(self.start_trim.get().strip()), float(self.end_trim.get().strip()))
            self.trimmed_audio_8k = trim_audio('trimmed_8k.wav', float(self.start_trim.get().strip()), float(self.end_trim.get().strip()))
        else:
            self.trimmed_audio = trim_audio('temp1.wav', float(self.start_trim.get().strip()), float(self.end_trim.get().strip()))
            self.trimmed_audio_8k= trim_audio('temp_8k.wav', float(self.start_trim.get().strip()), float(self.end_trim.get().strip()))
        self.trimmed_audio.export('trimmed.wav', format = 'wav')
        self.trimmed_audio_8k.export('trimmed_8k.wav', format = 'wav')
        self.playback_seekbar('trimmed.wav', 'trimmed_8k.wav')
        # return self.trimmed_audio

    def untrim(self):

        if os.path.exists('trimmed.wav') and os.path.exists('trimmed_8k.wav'):
            self.trimmed_audio = None
            self.trimmed_audio_8k = None
            os.remove('trimmed.wav')
            os.remove('trimmed_8k.wav')
            self.playback_seekbar('temp.wav', 'temp_8k.wav')


    def playback_seekbar(self, audio_file_name  = None, audio_file_name_8k = None): 

        #seekbar intializations
        if hasattr(self, 'playback_frame') and self.playback_frame is not None:
            self.playback_frame.destroy()

        self.playback_frame = ttk.Frame(self.master)
        self.playback_frame.pack()
        if audio_file_name is not None:
            #print('audio file existss')
            self.audio_data = pyglet.media.load(audio_file_name, streaming = False)
            self.audio_data_8k = pyglet.media.load(audio_file_name_8k, streaming = False)
            if self.trimmed_audio is not None and self.trimmed_audio_8k is not None:
                self.seg = self.trimmed_audio
                self.seg_8k = self.trimmed_audio_8k
            else:
                self.seg = AudioSegment.from_file(file= audio_file_name, format= 'wav')
            with wave.open(audio_file_name, 'rb') as wf:
                num_frames = wf.getnframes()
                #print(num_frames)
                self.raw_data = wf.readframes(num_frames)
                #print(type(self.raw_data))
                self.np_data = np.frombuffer(self.raw_data, dtype=np.int16) 
        else:
            self.raw_data = b''.join(self.audio_recorder.frames_48000)
            self.np_data = np.frombuffer(self.raw_data, dtype= np.int16)
            #print('no file, loading from the current recording frames')
            #print(len(self.np_data))
            self.seg = self.audio_recorder._create_audio_segment(self.audio_recorder.frames_48000, rate= 48000)
            self.seg1 = self.seg + 8
            self.seg_8k = self.audio_recorder._create_audio_segment(self.audio_recorder.frames_8000, rate = 8000)
            #print(self.seg)
            self.seg_8k.export('temp_8k.wav', format = 'wav')
            self.seg1.export('temp.wav', format= 'wav') 
            self.seg.export('temp1.wav', format= 'wav') 
            self.audio_data = pyglet.media.load('temp1.wav', streaming= False)
        self.player = pyglet.media.Player()
        #print('before loading audio', self.player.volume) # self.player.loop = True
        self.player.queue(self.audio_data)
        #print('after loading audio: ',self.player.volume)
        self.player.on_eos = self.player.pause()
        #self.player.loop = True
        # self.player.loop = True
        self.paused = False
        self.resumed = False
        self.seek = False
        
        self.start = False
        self.stop = False
        self.audio_duration = self.seg.duration_seconds
        self.plot_waveform()
       
       
        x_axis_width = self.axes.get_position().width * self.fig2.get_figwidth() * self.fig2.dpi

        # Calculate the length of the scale widget to match the width of the x-axis
        scale_length = int(x_axis_width)
        #print('scale_length: ', scale_length)
        #seekbar
        self.seek_bar = ttk.Scale(
            self.playback_frame, from_=0, to=self.audio_duration, orient="horizontal", length=scale_length, command=self.update_time_label)
        self.seek_bar.pack(pady=(10,0), padx = (100,0))
        self.seek_bar.bind("<B1-Motion>", self.pause_audio)
        self.seek_bar.bind("<ButtonRelease-1>", self.seek_to_position)

        # Label to display current time and total duration
        self.time_label = ttk.Label(self.playback_frame, text="0:00 / {}".format(self.format_time(self.audio_duration)))
        self.time_label.pack(pady = (5,5), padx= (35, 0))

        # Create buttons
        self.play_button = ttk.Button(self.playback_frame, text="Play", command=self.play_audio)
        self.pause_button = ttk.Button(self.playback_frame, text="Pause", command=self.pause_audio)
        self.stop_button = ttk.Button(self.playback_frame, text="Stop", command=self.stop_audio)
        self.resume_button = ttk.Button(self.playback_frame, text = "Resume", command = self.resume_audio)
        self.start_trim = ttk.Entry(self.playback_frame, width= 6)
        self.start_trim.insert(0,'start trim')
        self.end_trim = ttk.Entry(self.playback_frame, width = 6)
        self.end_trim.insert(0, 'end trim')
        self.trim_btn = ttk.Button(self.playback_frame, text= 'trim audio', command= self.trim)
        # self.save_trim_btn = ttk.Button(self.playback_frame, text = 'Save trimmed audio', )
        self.revert_trim = ttk.Button(self.playback_frame, text= 'revert trim', command= self.untrim)
        self.start_trim.pack(side = tk.LEFT,padx=(400, 10))
        self.end_trim.pack(padx = 10, side= tk.LEFT)
        self.trim_btn.pack(side = tk.LEFT, padx = 10)
        self.revert_trim.pack(side = tk.LEFT, padx = 10)
        self.play_button.pack(side=tk.LEFT, padx= 10)
        self.pause_button.pack(side=tk.LEFT, padx= 10)
        self.resume_button.pack(side=tk.LEFT, padx = 10)
        self.stop_button.pack(side=tk.LEFT, padx= 10)
    

        self.playback_frame.after(100, self.update_seek_bar)
        
    def  on_entry(self, event):
        return 'break'
    
    def on_focus_in(self, event):
        widget = event.widget
        print(widget)
        widget.bind('<Left>', self.on_entry)
        widget.bind('<Right>', self.on_entry)


    def on_focus_out(self, event):
        widget = event.widget
        # print(widget)
        widget.unbind('<Left>')
        widget.unbind('<Right>')

    def on_focus_out_text_id(self):
        # widget = event.widget
        # print(widget)
        self.text_id.unbind('<Left>')
        self.text_id.unbind('<Right>')
        
    def on_focus_in_text_id(self):
        self.text_id.bind('<Left>', self.on_entry)
        self.text_id.bind('<Right>', self.on_entry)

    def on_focus_in_text_sentence(self):
        self.text_sentence.bind('<Left>', self.on_entry)
        self.text_sentence.bind('<Right>', self.on_entry)
        
    def update_time_label(self, value):
        self.current_time = int(float(value))
        self.time_label.config(text="{} / {}".format(self.format_time(self.current_time), self.format_time(self.audio_duration)))

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return "{:02}:{:02}".format(int(minutes), int(seconds))

    def play_audio(self):
        self.player.seek(0.1)
        self.player.play()
        self.play_start_time = time.time()
        self.start = True

    def pause_audio(self):

        if self.player.playing:
            #print('audio is playin')
            self.player.pause()
            self.paused = True
            # self.start = True
            self.resumed = False
            self.paused_position = self.seek_bar.get()
            self.seek_bar.set(self.paused_position)
            self.current_time = self.paused_position
            #print('audio paused at', self.current_time)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)
        else:
            #print('no audio is playin')
            self.popup_message('No audio playing to pause..', destroy_duration= 1000)

    def resume_audio(self):

        if self.paused:
            #print('Entering the resuming state')
            self.resumed = True
            self.paused = False
            self.current_time = self.paused_position
            #print('resumed at: ', self.current_time)
            #print('source: ', self.player.source)
            self.player.seek(float(self.current_time))
            self.player.play()
            
            ##print('audio resumed at', self.current_time)
            self.resume_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)

    def stop_audio(self):

        self.player.pause()
        #self.player.delete()
        self.stop = True
        self.paused = False
        self.seek = False
        self.resumed = False
        self.start = False
        self.seek_bar.set(0.0)  # Reset seek bar position
        self.resume_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)

    def seek_to_position(self, event):
        self.seek = True
        self.paused = False
        self.resumed = False
        position_seconds = float(event.widget.get())
        self.seek_bar.set(position_seconds)
        #print('Position in seconds:', position_seconds)
        self.player.seek(position_seconds)
        self.player.play()
        self.current_time = position_seconds
        self.start = True
        # self.seek = False

    def update_seek_bar(self):

        if self.start and not self.paused and not self.seek and not self.resumed:
            self.current_time = time.time() - self.play_start_time
            if self.current_time < self.audio_duration:
                self.seek_bar.set(self.current_time)
            else:
                self.stop_audio()
        elif self.paused and not self.resumed:
            self.seek_bar.set(self.current_time)
        elif self.resumed and not self.paused:
            if self.current_time < self.audio_duration:
                self.current_time += 0.1
                #print('new current time: ',self.current_time)
                self.seek_bar.set(self.current_time)
                self.current_time= self.seek_bar.get()
            else:
                self.stop_audio()
                self.resumed = False
        elif self.seek:
            if self.current_time < self.audio_duration:
                self.current_time += 0.1
                #print('new current time: ',self.current_time)
                self.seek_bar.set(self.current_time)
                self.current_time = self.seek_bar.get()
            else:
                self.stop_audio()
                self.seek = False
        elif self.stop:
            self.seek_bar.set(0.0)
            self.stop = False

        self.playback_frame.after(100, self.update_seek_bar)

    def plot_waveform(self):
        # pass
        #print(self.seg.dBFS)
        dbfs_frames = [frame.dBFS for frame in self.seg]
        #print(len(self.np_data))
        time_in_sec = np.linspace(0, self.audio_duration, len(self.np_data))

        font1 = {'family':'sans serif','color':'#0D2740','size':10, 'weight' : 'bold'}
        if hasattr(self, 'canvas2'):
            self.canvas2.get_tk_widget().destroy()
        self.fig2 = plt.figure(figsize=(14,2))
        self.axes = plt.axes()
        # plt.figure(figsize=(8, 2))
        self.axes.set_xlim(0, right= self.audio_duration)
        #plt.axhline(y = 17800, color = 'r', linestyle = '--')
        plt.plot(time_in_sec, self.np_data, color='#0D2740')
        plt.xlabel('Time (seconds)', fontdict= font1)
        plt.ylabel('Amplitude', fontdict= font1)
        #plt.title('Waveform') 
        plt.tight_layout()
        self.fig2.set_facecolor('#717b96')

        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.playback_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(pady=(5,0), padx = (0,0))

    def on_closing(self):
        self.master.destroy()
        sys.exit()
#################################################################################
@profile
def main():
    root = ttkb.Window(themename='flatly') # Main/Parent Window - Offers access to geometric configuration of widgets.
    root.state('zoomed')
    app = AudioRecorderApp(root)
    root.bind('<Key-asterisk>', lambda event: app.start_recording())
    root.bind('<space>', lambda event: app.stop_recording_or_playing(event))
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() # infinite loop, waits for an event to occur and process the event until window closed.
    #root.protocol("WM_DELETE_WINDOW", app.on_closing)
if __name__ == "__main__":
    #cProfile.run('main()', filename= 'profiling.prof')
    # profiler = pyinstrument.Profiler()
    # with profiler:
    main()
# profiler.print_stats()

# pyinstaller --onefile -w --add-data "static_files;static_files" recording-app-light-v0.py
# pyinstaller --onefile -w --add-data "static_files;static_files" recording-app.py








