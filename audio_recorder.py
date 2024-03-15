import pyaudio
import wave
import sys
import pandas as pd
from pydub import AudioSegment
from detect_silence import trim_silence
import numpy as np


# from playsound import playsound

# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

CHUNK = 1024
# record_seconds = 10
SAMPLE_WIDTH = pyaudio.get_sample_size(pyaudio.paInt16)

print(SAMPLE_WIDTH)

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames = []

        self.is_recording = False
        self.selected_device = None

    def load_data(self, file_path):
        self.file = file_path
        self.df = pd.read_csv(self.file)
        self.start_id = 0
        self.sentence = self.df.text.iloc[self.start_id]
        self.id = self.df.ID.iloc[self.start_id]

    def update_device_list(self):
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                #print(f"Input Device {i}: {device_info['name']}")
                print('')

    def select_device(self, device_index):
        self.selected_device = device_index

    def start_recording(self):
        if not self.is_recording:
            print('List of available input Microphones: \n')
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    print(f"Input Device {i}: {device_info['name']}")
            self.select_device(int(input("Enter the index of the input device you want to use: ")))
            if self.selected_device is not None:
                self.stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=self.selected_device, frames_per_buffer=CHUNK)
                self.is_recording = True
                print('The audio is being recorded from the input device: ', self.audio.get_device_info_by_index(self.selected_device)['name'])
                print(f'SENTENCE: {self.sentence}')
                print(f'ID: {self.id}')
                print('Recording Started..')
                try:
                    while self.is_recording:
                        data = self.stream.read(CHUNK)
                        self.frames.append(data)
                except:
                    KeyboardInterrupt 
                    print('Keyboard interruption')
                    return 
                
    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            print("Recording stopped.")

    def save_audio(self):
        if not self.frames:
            print("No audio to save.")
            return
        filename = self.id
        print(len(self.frames))
        buffer = b''.join(self.frames)
        audio_segment = AudioSegment(
        buffer,
        sample_width=SAMPLE_WIDTH,
        channels=CHANNELS,
        frame_rate=RATE)
        #audio_segment.export('non-silenced.wav', format = 'wav')
        trimmed_wav, duration = trim_silence(audio_segment)
        #trimmed_wav.export('silenced.wav', format = 'wav')
        print(f'The recorded audio is saved in the filename: {self.id}')
        if not filename:
            print("Please enter a valid filename.")
            return
        # self.seg_data = AudioSegment(self.frames, frame_rate = 44100)
        # self.sil_aud = 
        output_filename = f"{filename}.wav"
        # with wave.open(output_filename, 'wb') as wf:
        #     wf.setnchannels(CHANNELS)
        #     wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        #     wf.setframerate(RATE)
        #     wf.writeframes(b''.join(self.frames))
        trimmed_wav.export(output_filename, format= 'wav')
        print(f"Audio saved as {output_filename}")
        print(f'Sample rate of the audio: ')
        self.frames = []
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        print('\n The next sentence and ID:')
        self.start_id += 1
        print(self.start_id)
        self.sentence = self.df.text.iloc[self.start_id]
        self.id = self.df.ID.iloc[self.start_id]
        print('Sentence: ', self.sentence)
        print('ID: ', self.id)

    def playback_audio(self):

        if not self.frames:
            print('No audio to play..')
         # Open an output stream
        playback_stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, input_device_index= self.selected_device)
        try:
            # Write the recorded frames to the playback stream

            for data in self.frames:
                print(data)
                playback_stream.write(data)
        except KeyboardInterrupt:
            print('Keyboard interruption during playback')
        finally:
            # Stop and close the playback stream
            playback_stream.stop_stream()
            playback_stream.close()
        
<<<<<<< HEAD
    def goto_previous(self):
        if self.start_id == 0:
            print('No previous ID! This is the first value')
        else:
            self.prev_index = self.start_id - 1
            print(self.prev_index)
            self.prev = self.df.ID.iloc[int(self.prev_index)]
            print(self.prev)
            print(self.df.text.iloc[self.prev_index])
            


=======
    # def detect_leading_silence(sound, silence_threshold=-60.0, chunk_size=1):
    # '''
    # sound is a pydub.AudioSegment
    # silence_threshold in dBFS
    # chunk_size in ms

    # iterate over chunks until you find the first one with sound
    # '''
    # #sound = AudioSegment.from_file(filepath, format="wav")

    # trim_ms = 0 # ms

    # assert chunk_size > 0 # to avoid infinite loop
    # while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
    #     trim_ms += chunk_size

    # return trim_ms
>>>>>>> parent of 13d5516 (added detect_silence.py under a new folder utils which can be used to detect and trim silence from the recorded audio and updated audio_recorder.py)

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.update_device_list()
    csv = input('Enter the name of the CSV: ')
    recorder.load_data(csv)

    while True:
        print("\nOptions:")
        print("1. Start Recording")
        print("2. Stop Recording")
        print("3. Save Recording")
        print("4. playback the recorded audio")
        print("5. go to previous")
        print("6. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            recorder.start_recording()
        elif choice == '2':
            recorder.stop_recording()
        elif choice == '3':
            recorder.save_audio()
        elif choice == '4':
            recorder.playback_audio()
        elif choice == '6':
            break
        elif choice == '5':
            recorder.goto_previous()
        else:
            print("Invalid choice. Please select a valid option.")

