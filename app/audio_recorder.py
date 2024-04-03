import os
import pyaudio
import threading
from pydub import AudioSegment
from utils.detect_silence import trim_silence

base_dir = 'data'
audio_types = ['48khz', '8khz']

class AudioRecorder:
    def __init__(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.frames_48000 = []
        self.frames_18000 = []
        self.format = pyaudio.paInt16 
        self.channels = 1
        self.rate_48000 = 48000
        self.rate_18000 = 18000
        self.frames_per_buffer = 1024 # record in chunks of 1024
        self.is_recording = False
        self.stream = None
        
    def start_recording(self, device_index=None):
        self.stream_48000 = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate_48000,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index            
        )
        self.stream_18000 = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate_18000,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=device_index            
        )
        self.is_recording=True
        self.recording_thread_48000=threading.Thread(target=self._record_loop, args=(self.stream_48000,self.frames_48000))
        self.recording_thread_18000=threading.Thread(target=self._record_loop, args=(self.stream_18000,self.frames_18000))
        self.recording_thread_48000.start()
        self.recording_thread_18000.start()
        
    def _rocord_loop(self,stream,frames):
        while self.is_recording:
            try:
                data = stream.read(self.frames_per_buffer, exception_on_overflow=False)
                frames.append(data)
            except:
                KeyboardInterrupt
                print('Keyboard Interrupt')
                return
    
    def stop_recording(self):
        if self.is_recording:
            self.is_recording=False
            self.recording_thread_48000.join() 
            self.recording_thread_18000.join()
            self.stream_48000.stop_stream()
            self.stream_18000.stop_stream()
            self.stream_48000.close()
            self.stream_18000.close()
            
    def save_recording(self, filename, audio_dir):
        if not self.frames_48000 or self.frames_18000:
            print("No audio to save.")
            return
        self.audio_dir_48khz = os.path.join(audio_dir, '48khz')
        self.audio_dir_18khz = os.path.join(audio_dir, '18khz')
        os.makedirs(self.audio_dir_48khz, exists_ok=True)
        os.makedirs(self.audio_dir_18khz, exist_ok=True)
        
        audio_segment_48000 = self._create_audio_segment(self.frames_48000, 48000)
        audio_segment_18000 = self._create_audio_segment(self.frames_18000, 18000)
        
        trimmed_wav_48k, duration_48k = trim_silence(audio_segment_48000)
        output_filename_48k = os.path.join(self.audio_dir_48khz, f"{filename}")
        trimmed_wav_48k.export(output_filename_48k, format='wav')
        trimmed_wav_18k, duration_18k = trim_silence(audio_segment_18000)
        output_filename_18k = os.path.join(self.audio_dir_18khz, f"{filename}")
        trimmed_wav_18k.export(output_filename_18k, format='wav')
        self.frames_48000 = []
        self.frames_18000 = []     
        
    def _create_audio_segment(self, frames, rate):
        buffer = b''.join(frames)
        return AudioSegment(buffer, sample_width=self.pyaudio_instance.get_sample_size(self.format),
                            channels=self.channels, frame_rate=rate)
        
    def record(self, data):
        self.frames.append(data)        



