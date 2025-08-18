from scipy.fftpack import fft
from scipy.io import wavfile
import os


print("tonsebastian")

AUDIO_FILE = os.path.join("media","wav","test.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav

