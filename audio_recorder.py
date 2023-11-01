import pyaudio
import wave
import sys

# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
record_seconds = 10

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames = []

        self.is_recording = False
        self.selected_device = None

    def update_device_list(self):
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Input Device {i}: {device_info['name']}")

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

        filename = input("Enter the filename to save: ")

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
        self.frames = []
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()


if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.update_device_list()

    while True:
        print("\nOptions:")
        print("1. Start Recording")
        print("2. Stop Recording")
        print("3. Save Recording")
        print("4. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            recorder.start_recording()
        elif choice == '2':
            recorder.stop_recording()
        elif choice == '3':
            recorder.save_audio()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please select a valid option.")

