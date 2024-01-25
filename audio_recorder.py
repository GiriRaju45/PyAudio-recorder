import pyaudio
import wave
import sys
import pandas as pd
# from playsound import playsound

# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
# record_seconds = 10


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
        print(f'The recorded audio is saved in the filename: {self.id}')
        if not filename:
            print("Please enter a valid filename.")
            return

        output_filename = f"{filename}.wav"
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))
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
        playback_stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

        try:
            # Write the recorded frames to the playback stream
            for data in self.frames:
                playback_stream.write(data)
        except KeyboardInterrupt:
            print('Keyboard interruption during playback')
        finally:
            # Stop and close the playback stream
            playback_stream.stop_stream()
            playback_stream.close()
        

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
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            recorder.start_recording()
        elif choice == '2':
            recorder.stop_recording()
        elif choice == '3':
            recorder.save_audio()
        elif choice == '4':
            recorder.playback_audio()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please select a valid option.")

