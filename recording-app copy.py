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
import threading
from pydub import AudioSegment
from PIL import Image, ImageTk
from utils.detect_silence import trim_silence  

base_dir = 'data'
my_styles = ["FEAR","PROPER NOUN","Happy","HAPPY","Sad","SAD","Disgust","DISGUST","BOOK","BB","WIKI","Surprise","SURPRISE","DIGI","ALEXA","NEWS","Anger","ANGER","INDIC","SANGRAH","CONV","UMANG"]
my_languages = ['DEMO','ASM', 'BEN', 'BRX', 'DOI', 'GUJ', 'HIN', 'KAN', 'KAS', 'KOK', 'MAI', 'MAL', 'MAR', 'MNI', 'NEP', 'ORI', 'PAN', 'SAN', 'SAT', 'SND', 'TAM', 'TEL', 'URD']
my_speakers = ['Male','Female']
    
class AudioRecorder:
    def __init__(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.frames = []
        self.format = pyaudio.paInt16  # Defined as a class attribute for reuse
        self.channels = 1
        self.rate = 48000
        self.frames_per_buffer = 1024
        self.is_recording = False
        self.stream = None

    def start_recording(self, device_index=None):
        self.stream = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index,
        )
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_loop)
        self.recording_thread.start()
        
    def _record_loop(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                self.frames.append(data)
            except:
                KeyboardInterrupt
                print('Keyboard Interupt')
                return
            
    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False   
            self.recording_thread.join()       
            self.stream.stop_stream()
            self.stream.close()

    def save_recording(self, filename):
        if not self.frames:
            print("No audio to save.")
            return    
        buffer = b''.join(self.frames)
        audio_segment = AudioSegment(
            buffer, 
            sample_width=self.pyaudio_instance.get_sample_size(self.format),
            channels=self.channels,
            frame_rate=self.rate           
        ) 
        self.audio_dir = r"C:\Users\richa\Downloads\TTS_DC\tkinter\data\DEMO\12-03-2024\ANGER\Male"
        trimmed_wav, duration = trim_silence(audio_segment)
        output_filename = f"{self.audio_dir}/{filename}.wav"
        trimmed_wav.export(output_filename, format='wav')
        self.frames = []

    def record(self, data):
        self.frames.append(data)

    def play_audio(self, filename):
        # This function needs to be implemented based on your requirements.
        pass
    
#################################################################################
class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Audio Recorder App')
        self.audio_recorder = AudioRecorder()
        self.current_index = 0 # Keep track of the current sentence
        self.data = pd.read_csv(r'C:\Users\richa\Downloads\TTS_DC\tkinter\demo_correct.csv') # Load your CSV data here
        self.setup_menu()
        self.create_widgets()
        self.update_ui_with_sentence()  # Add this line to load the first sentence on startup
    
    def setup_menu(self):
        # Create menu
        # Add a menu bar for CSV handling
        self.menubar = tk.Menu(self.master)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)        
        self.filemenu.add_command(label="Select and Save CSV", command=self.select_and_save_csv)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Load CSV", command=self.load_csv)
        self.menubar.add_cascade(menu=self.filemenu, label="File")
        
        # Adding new menu
        self.optionsmenu = tk.Menu(self.menubar, tearoff=0)
        self.optionsmenu.add_command(label="Select Date and Options", command=self.show_date_and_options_ui)
        self.menubar.add_cascade(menu=self.optionsmenu, label="Options")
        # Attach the menu bar to the master window
        self.master.config(menu=self.menubar)   
 
    def setup_date_selection(self):
        self.my_date = ttkb.DateEntry(self.master, bootstyle="superhero")
        self.my_date.pack(pady=20)
                
    def setup_dropdowns(self):
        # Styles Dropdown
        self.style_var = tk.StringVar()
        self.styles_dropdown = ttk.Combobox(self.master, textvariable=self.style_var, values=my_styles)
        self.styles_dropdown.pack(pady=20)

        # Languages Dropdown
        self.language_var = tk.StringVar()
        self.languages_dropdown = ttk.Combobox(self.master, textvariable=self.language_var, values=my_languages)
        self.languages_dropdown.pack(pady=20)
        
        # Speaker Dropdown
        self.speaker_var = tk.StringVar()
        self.speakers_dropdown = ttk.Combobox(self.master, textvariable=self.speaker_var, values=my_speakers)
        self.speakers_dropdown.pack(pady=20)
        
        # Add a submit button
        self.submit_btn = tk.Button(self.master, text="Submit", command=self.on_submit)
        self.submit_btn.pack(pady=20)
        
        
    def show_date_and_options_ui(self):
        self.setup_date_selection()
        self.setup_dropdowns() 
            
    
    def make_directory(self):
        language = self.language_var.get()
        style =self.style_var.get()
        speaker = self.speaker_var.get()
        current_date = self.my_date.entry.get()
        self.audio_dir = os.path.join(base_dir,language,current_date,style,speaker)
        os.makedirs(self.audio_dir, exist_ok=True)
        
    def on_submit(self):
        self.make_directory()
    
    def create_widgets(self):
        self.master.minsize(width=1536, height=480)  # Set the minimum size of the window

        # Use a frame to center-align the widgets in the application
        main_frame = ttk.Frame(self.master)
        main_frame.pack(expand=True)
        
        # Configure the ID Entry to be at the top and bold
        self.text_id = ttk.Entry(main_frame, font=('Times New Roman', 18, 'bold'), width=24, bootstyle="success")
        self.text_id.bind('<Return>', self.load_entry_from_id)
        self.text_id.pack(pady=(16, 0))  # Padding only at the top

        # Configure the Sentence Text with bold font and padding
        bold_font = ('Arial Unicode MS', 22)  # Using 'Arial Unicode MS' for better Unicode character support
        self.text_sentence = tk.Text(main_frame, height=4, width=50, wrap="word", font=bold_font, spacing3=22)
        # spacing3 adds extra space below each line in the Text widget
        self.text_sentence.tag_configure("center", justify='center')
        self.text_sentence.pack(pady=20, padx=10)  # Padding on sides for the Text widget
        
        # Create a style object
        style = ttk.Style()

        # Define a new style that inherits from the default Button style and modify it
        style.configure('danger.TButton', font=('Helvetica', 60), padding=30) # Modify font size and padding as needed

        # Frame for buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=0)

        # Create buttons with the new style and specific bootstyle color themes
        # self.btn_play = ttk.Button(buttons_frame, text="▶️", command=self.play_audio, style='danger.TButton', bootstyle='success')
        self.btn_play = ttk.Button(buttons_frame, text="PLAY", command=self.play_audio, style='success.TButton, bold', bootstyle='success')
        self.btn_play.pack(side=tk.LEFT, padx=32, pady=5)

        self.btn_stop = ttk.Button(buttons_frame, text="⏹️", command=self.stop_recording_or_playing, style='my.TButton', bootstyle='secondary')
        self.btn_stop.pack(side=tk.LEFT, padx=32, pady=5)
        
        # original_img = Image.open(r'C:\Users\richa\Downloads\TTS_DC\tkinter\800px-Auto_Racing_Red_Circle.svg.png')
        # resized_img = original_img.resize((50, 50), Image.Resampling.LANCZOS)
        # record_img = ImageTk.PhotoImage(resized_img)
        # # Create a button with the image
        # self.btn_record = ttk.Button(buttons_frame, image=record_img, command=self.start_recording,)
        # self.btn_record.image = record_img  # Keep a reference to prevent garbage collection
        # self.btn_record.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_record = ttk.Button(buttons_frame, text="🔴", command=self.start_recording, style='my.TButton', bootstyle='danger')
        self.btn_record.pack(side=tk.LEFT, padx=32, pady=5)

        self.btn_save = ttk.Button(buttons_frame, text="💾", command=self.save_audio, style='my.TButton', bootstyle='warning')
        self.btn_save.pack(side=tk.LEFT, padx=32, pady=5)

        self.btn_previous = ttk.Button(buttons_frame, text="⏮️", command=self.previous_sentence, style='my.TButton', bootstyle='info')
        self.btn_previous.pack(side=tk.LEFT, padx=32, pady=5)

        self.btn_next = ttk.Button(buttons_frame, text="⏭️", command=self.next_sentence, style='my.TButton', bootstyle='info')
        self.btn_next.pack(side=tk.LEFT, padx=32, pady=5)
    
        # self.btn_skip = ttk.Button(buttons_frame, text="⏭️⏭️", command=self.skip_sentence)  # Use appropriate skip icon
        # self.btn_skip.pack(side=tk.LEFT, **padding)
        
    def load_entry_from_id(self, event=None):
        entered_id = self.text_id.get().strip()          
        matching_index = self.data.index[self.data['ID']==entered_id].tolist()
        
        if matching_index:
            self.current_index = matching_index[0]
            self.update_ui_with_sentence()
        else:
            print("ID not found.")
    
    def update_ui_with_row(self, row):
        self.text_sentence.delete("1.0", tk.END)
        self.text_sentence.insert("1.0", str(row['Sentence']))
        self.current_style = row['style']
        self.current_category = row['category']
        self.current_speaker = row['speaker']
        self.current_language = row['language']

    def update_ui_with_sentence(self):
        if 0 <= self.current_index < len(self.data):
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
            # Handle index out of range if needed
            print("Index out of range.")

    def select_and_save_csv(self):
        filepath = fd.askopenfilename(filetypes=[("Upload TRANSCRIPT", "*.csv")])
        if not filepath:
            return
        target_folder = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.basename(filepath)
        target_path = os.path.join(target_folder, filename)
        shutil.copy(filepath, target_path)
        print(f"File saved to {target_path}")
        
    def load_csv(self):
        filepath = fd.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filepath:
            self.data = pd.read_csv(filepath)
            self.current_index = 0
            self.update_ui_with_sentence()

    def play_audio(self):
        # Implement this method to play the selected audio
        pass

    def start_recording(self):
        # Start recording audio
        self.audio_recorder.start_recording()

    def stop_recording_or_playing(self):
        # Stop recording or playing audio
        self.audio_recorder.stop_recording()

    def save_audio(self):
        # Save the recorded audio
        id = self.text_id.get()
        sentence = self.text_sentence.get("1.0", "end-1c")
        filename = f"{id}.wav"  # Construct filename based on ID and edited sentence
        self.audio_recorder.save_recording(filename)

    def previous_sentence(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_ui_with_sentence()

    def next_sentence(self):
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.update_ui_with_sentence()
#################################################################################
def main():
    root = ttkb.Window(themename='superhero') # Main/Parent Window - Offers access to geometric configuration of widgets.
    app = AudioRecorderApp(root)
    root.mainloop() # infinite loop, waits for an event to occur and process the event until window closed.

if __name__ == "__main__":
    main()
