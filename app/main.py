from audio_recorder_app import AudioRecorderApp
import ttkbootstrap as ttkb

def main():
    root = ttkb.Window(theme='superhero')
    app = AudioRecorderApp(root)
    root.mainloop()
if __name__ == '__main__':
    main()
