import sounddevice as sd
from scipy.io.wavfile import write


def record_local_audio(seconds=5, filename="test_audio.wav"):
    fs = 16000
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)

if __name__ == "__main__":
    record_local_audio(seconds=5, filename="test.wav")
