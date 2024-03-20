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
import requests
import threading
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
    
class AudioRecorder:
    def __init__(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.frames_48000 = []
        self.frames_8000 = []
        self.format = pyaudio.paInt16  # Defined as a class attribute for reuse
        self.channels = 1
        self.rate_48000 = 48000
        self.rate_8000 = 8000
        self.frames_per_buffer = 1024
        self.is_recording = False
        self.stream = None

    def start_recording(self, device_index=None):
        self.stream_48000 = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate_48000,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index,
        )
        self.stream_8000 = self.pyaudio_instance.open(format=self.format,
            channels=self.channels,
            rate=self.rate_8000,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index,)
        
        self.is_recording = True
        self.recording_thread_48000 = threading.Thread(target=self._record_loop, args=(self.stream_48000, self.frames_48000))
        self.recording_thread_8000 = threading.Thread(target=self._record_loop, args=(self.stream_8000, self.frames_8000))
        self.recording_thread_48000.start()
        self.recording_thread_8000.start()
        


    def _record_loop(self, stream, frames):
        while self.is_recording:
            try:
                data = stream.read(self.frames_per_buffer, exception_on_overflow=False)
                frames.append(data)
            except:
                KeyboardInterrupt
                print('Keyboard Interupt')
                return
            
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
            print("No audio to save.")
            return
        self.audio_dir_48khz = os.path.join(audio_dir, '48khz')
        self.audio_dir_8khz = os.path.join(audio_dir, '8khz')
        os.makedirs(self.audio_dir_8khz, exist_ok= True)
        os.makedirs(self.audio_dir_48khz, exist_ok=True)    

        audio_segment_48000 = self._create_audio_segment(self.frames_48000, 48000)
        audio_segment_8000 = self._create_audio_segment(self.frames_8000, 8000)

        trimmed_wav_48k, duration_48k = trim_silence(audio_segment_48000)
        output_filename_48k = os.path.join(self.audio_dir_48khz, f"{filename}")
        trimmed_wav_48k.export(output_filename_48k, format='wav')
        trimmed_wav_8k, duration_8k = trim_silence(audio_segment_8000)
        output_filename_8k = os.path.join(self.audio_dir_8khz, f"{filename}")
        trimmed_wav_8k.export(output_filename_8k, format = 'wav')
        self.frames_48000 = []
        self.frames_8000 = []

    def _create_audio_segment(self, frames, rate):
        buffer = b''.join(frames)
        return AudioSegment(buffer, sample_width=self.pyaudio_instance.get_sample_size(self.format),
                            channels=self.channels, frame_rate=rate)

    def record(self, data):
        self.frames.append(data)
    
#################################################################################
class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Audio Recorder App')
        self.count = 0
        self.duration = 0
        self.audio_recorder = AudioRecorder()
        self.current_index = 0 # Keep track of the current sentence
        self.data = None # Load your CSV data here
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
        self.styles_dropdown.set('Select Style')

        # Languages Dropdown
        self.language_var = tk.StringVar()
        self.languages_dropdown = ttk.Combobox(self.master, textvariable=self.language_var, values=my_languages)
        self.languages_dropdown.pack(pady=20)
        self.languages_dropdown.set('Select Language')
        
        # Speaker Dropdown
        self.speaker_var = tk.StringVar()
        self.speakers_dropdown = ttk.Combobox(self.master, textvariable=self.speaker_var, values=my_speakers)
        self.speakers_dropdown.pack(pady=20)
        self.speakers_dropdown.set('Select Speaker')

        # Microphone Dropdown

        self.microphone_var = tk.StringVar()
        self.microphone_dropdown = ttk.Combobox(self.master, textvariable=self.microphone_var, state='readonly')
        self.microphone_dropdown.pack(pady= 20)
        self.microphone_dropdown.set('Select Microphone')
       
        self.update_microphone_dropdown()


        # Add a submit button
        self.submit_btn = tk.Button(self.master, text="Submit", command=self.on_submit)
        self.submit_btn.pack(pady=20)
        
       # print(self.microphone_var.get())

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
            self.master.after(1000, lambda: messagebox._show("Success", "Directory Created"))
            
        
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
        
        # Update dropdown options
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
        # style.configure('danger.TButton', font=('Helvetica', 60), padding=30) # Modify font size and padding as needed
        

        # Frame for buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=0)
        
        # self.btn_play = ttk.Button(buttons_frame, text="▶️", command=self.play_audio, style='danger.TButton', bootstyle='success')
        # # self.btn_play = ttk.Button(buttons_frame, text="PLAY", command=self.play_audio, style='success.TButton, bold', bootstyle='success')
        # self.btn_play.pack(side=tk.LEFT, padx=32, pady=5)

        # self.btn_stop = ttk.Button(buttons_frame, text="⏹️", command=self.stop_recording_or_playing, style='my.TButton', bootstyle='secondary')
        # self.btn_stop.pack(side=tk.LEFT, padx=32, pady=5)
        
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

        # self.btn_play.pack(side=tk.LEFT, padx=32, pady=5)

        # self.audio_var = tk.StringVar()
        # self.audiotype_dropdown = ttk.Combobox(self.master, values=audio_types, width= 35)
        # self.audiotype_dropdown.pack(pady=20, padx=15, side= LEFT)
        # self.audiotype_dropdown.place(x = 30, y = 350)
        # self.audiotype_dropdown.set('Select audio format to listen the recorded audio')


        # self.plyback_btn = ttk.Button(buttons_frame, text= 'play selected format audio', command= self.playback_recorded_audio, style= 'my.TButton', bootstyle='secondary')
        self.btn_play.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_stop.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_record.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_save.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_previous.pack(side=tk.LEFT, padx=32, pady=5)
        self.btn_next.pack(side=tk.LEFT, padx=32, pady=5)



########################################################################################################################################
        # self.btn_record = ttk.Button(buttons_frame, text="🔴", command=self.start_recording, style='my.TButton', bootstyle='danger', font=emoji_font)
        # self.btn_record.pack(side=tk.LEFT, padx=32, pady=5)

        # self.btn_save = ttk.Button(buttons_frame, text="💾", command=self.save_audio, style='my.TButton', bootstyle='warning')
        # self.btn_save.pack(side=tk.LEFT, padx=32, pady=5)

        # self.btn_previous = ttk.Button(buttons_frame, text="⏮️", command=self.previous_sentence, style='my.TButton', bootstyle='info')
        # self.btn_previous.pack(side=tk.LEFT, padx=32, pady=5)

        # self.btn_next = ttk.Button(buttons_frame, text="⏭️", command=self.next_sentence, style='my.TButton', bootstyle='info')
        # self.btn_next.pack(side=tk.LEFT, padx=32, pady=5)
    
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

    def select_and_save_csv(self):
        filepath = fd.askopenfilename(filetypes=[("Upload TRANSCRIPT", "*.csv")])
        if not filepath:
            return
        target_folder = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.basename(filepath)
        self.target_path = os.path.join(target_folder, filename)
        shutil.copy(filepath, self.target_path)

        print(f"File saved to {self.target_path}")
        
    def load_csv(self):
        filepath = fd.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filepath:
            self.data = pd.read_csv(filepath)
            self.current_index = 0
            self.update_ui_with_sentence()

    def play_audio(self):
        id = self.text_id.get().strip()
        filename = os.path.join(self.audio_dir,f"{id}.wav")
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Audio file {filename} does not exists.")
            return
        threading.Thread(target=self.play_audio_file, args=(filename,)).start()
        
    def play_audio_file(self, filename):
        wf = wave.open(filename, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        chunk_size=1024
        data=wf.readframes(chunk_size)
        while data:
            stream.write(data)
            data=wf.readframes(chunk_size)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def playback_recorded_audio(self):
        #frames = []
        #print(self.audiotype_dropdown.get())
        if self.audiotype_dropdown.get().strip() == '48khz':
            frames = self.audio_recorder.frames_48000
            rate = 48000
        elif self.audiotype_dropdown.get().strip() == '8khz':
            frames = self.audio_recorder.frames_8000
            rate = 8000
        elif self.audiotype_dropdown.get().strip() == 'Select audio format to listen the recorded audio' or self.audiotype_dropdown.get() not in ['48khz', '8khz']:
            messagebox.showerror('Error!', 'Please select a valid audio format')
        print(rate)
        print(frames)
        if True:
            print(rate)
         # Open an output stream
            self.audio = pyaudio.PyAudio()
            playback_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=rate, output=True, input_device_index= int(self.microphone_dropdown.get().split(' ')[1].replace(':', '')))
            try:
                # Write the recorded frames to the playback stream
                for data in frames:
                    #print(data)
                    playback_stream.write(data)
            except KeyboardInterrupt:
                print('Keyboard interruption during playback')
            finally:
                # Stop and close the playback stream
                playback_stream.stop_stream()
                playback_stream.close()

    def start_recording(self):
        index = int(self.microphone_dropdown.get().split(' ')[1].replace(':', ''))
        messagebox.showinfo("Recording Started", "Recording has started.")
        self.master.after(2000, lambda: messagebox._show("Recording Started", "Recording has started."))

        self.audio_recorder.start_recording(device_index=index)

    def stop_recording_or_playing(self):
        self.audio_recorder.stop_recording()

    def save_audio(self):
        id = self.text_id.get()
        sentence = self.text_sentence.get("1.0", "end-1c")
        filename = f"{id}.wav" 
        audio_duration = self.audio_recorder.save_recording(filename, self.audio_dir)
        file_path = os.path.join(self.audio_dir, filename)
        data = {
            "easy_id": self.current_date,
            "Sentence": sentence,
            "speaker": self.current_speaker,
            "language": self.current_language,
            "style": self.current_language,
            "category": self.current_category,
            "data_id": id
        }
        with open(file_path, 'rb') as audio_file:
            files = {
                'audio_file': (filename, audio_file, 'audio/wav')
            }
            response = requests.post('http://tts-dc-prod.centralindia.cloudapp.azure.com:8094/audio_upload', files=files,data=data)
            
        if response.ok:
            self.count += 1
            self.duration += round(audio_duration/60000, 2)
            print("Successfully uplaoded the audio file and metadata.")
            self.audio_count.config(text=f"Audio Count: {self.count}")
            self.audio_duration.config(text=f"Duration: {self.duration} minutes") 
        else:
            print(f"Failed to upload hte audio file. Status code: {response.status_code}, Response: {response.text}")

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

