## Manual trim 

from pydub import AudioSegment

def trim_audio(input_file, start_trim, end_trim):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)
    
    # Calculate the start and end trim positions in milliseconds
    start_trim_ms = int(start_trim * 1000)
    end_trim_ms = int(end_trim * 1000)
    
    # Get the length of the audio
    audio_length = len(audio)
    
    # Trim the audio by removing the specified region
    trimmed_audio = audio[:start_trim_ms] + audio[end_trim_ms:]
    
    # Export the trimmed audio to a new file
    return trimmed_audio