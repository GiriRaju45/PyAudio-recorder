from pydub import AudioSegment

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=1):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dBFS
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    #sound = AudioSegment.from_file(filepath, format="wav")

    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

# <<<<<<< HEAD
# sound = AudioSegment.from_file("TA_F_35000.wav", format="wav")
# =======
# # sound = AudioSegment.from_file("TA_F_35000.wav", format="wav")
# >>>>>>> 18752d9eae9ba055b5ef63978a39734a16f88499

def trim_silence(sound):
                 
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)
    trimmed_sound = sound[start_trim:duration-end_trim]

    return trimmed_sound, duration

# trimmed_wav, duration =  trim_silence(sound)
# silence = duration - len(trimmed_wav)


# print("duration ",duration)
# print("silence ",silence)


# trimmed_wav.export(out_f = 'TA_F_35001_silence_reduced_new.wav', format = 'wav')