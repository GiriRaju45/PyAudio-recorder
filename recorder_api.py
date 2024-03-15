from flask import Flask, render_template, request, redirect, url_for
from audio_recorder import AudioRecorder

app = Flask(__name__)
recorder = AudioRecorder()

@app.route('/')
def index():
    return render_template('interface2.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    recorder.start_recording()
    return redirect(url_for('index'))

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    recorder.stop_recording()
    return redirect(url_for('index'))

@app.route('/save_audio', methods=['POST'])
def save_audio():
    recorder.save_audio()
    return redirect(url_for('index'))

@app.route('/playback_audio', methods=['POST'])
def playback_audio():
    recorder.playback_audio()
    return redirect(url_for('index'))

@app.route('/goto_previous', methods=['POST'])
def goto_previous():
    recorder.goto_previous()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
