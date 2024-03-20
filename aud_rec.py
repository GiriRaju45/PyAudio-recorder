import pyaudio
import wave
import sys
import pandas as pd
from pydub import AudioSegment
from utils.detect_silence import trim_silence

# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
SAMPLE_WIDTH = pyaudio.get_sample_size(pyaudio.paInt16)

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.selected_device = None

    def update_device_list(self):
        """Update and display available input devices."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Input Device {i}: {device_info['name']}")

    def select_device(self, device_index):
        """Select the input device for recording."""
        self.selected_device = device_index

    def start_recording(self):
        """Start recording audio from the selected input device."""
        if not self.selected_device:
            print("No input device selected.")
            return

        try:
            self.stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                          input_device_index=self.selected_device, frames_per_buffer=CHUNK)
            self.is_recording = True
            print('Recording Started..')
            while self.is_recording:
                data = self.stream.read(CHUNK)
                self.frames.append(data)
        except KeyboardInterrupt:
            print('Keyboard interruption')
        finally:
            self.stop_recording()

    def stop_recording(self):
        """Stop recording audio."""
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            print("Recording stopped.")

    def save_audio(self, filename):
        """Save recorded audio to a WAV file."""
        if not self.frames:
            print("No audio to save.")
            return

        buffer = b''.join(self.frames)
        audio_segment = AudioSegment(buffer, sample_width=SAMPLE_WIDTH, channels=CHANNELS, frame_rate=RATE)
        trimmed_wav, duration = trim_silence(audio_segment)
        
        output_filename = f"{filename}.wav"
        trimmed_wav.export(output_filename, format='wav')
        print(f"Audio saved as {output_filename}")

        # Reset frames and recording status
        self.frames = []
        self.is_recording = False

    def select_next_sentence(self):
        """Move to the next sentence in the dataset."""
        pass  # Implement this method


if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.update_device_list()

    # Sample usage
    csv = input('Enter the name of the CSV: ')
    recorder.select_device(int(input("Enter the index of the input device you want to use: ")))

    while True:
        print("\nOptions:")
        print("1. Start Recording")
        print("2. Stop Recording")
        print("3. Save Recording")
        print("4. Next Sentence")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            recorder.start_recording()
        elif choice == '2':
            recorder.stop_recording()
        elif choice == '3':
            filename = input("Enter the filename to save: ")
            recorder.save_audio(filename)
        elif choice == '4':
            recorder.select_next_sentence()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please select a valid option.")
