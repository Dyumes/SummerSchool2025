from scipy.fft import fft
from scipy.io import wavfile
import os
import numpy as np


AUDIO_FILE = os.path.join("media","wav","test.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav

#fourrier = fft(audio)
#print(fourrier)

FPS = 30
FFT_WINDOW_SECONDS = 0.046 # how many seconds of audio make up an FFT window

#FRAME_STEP = (fs / FPS) # audio samples per video frame
FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
AUDIO_LENGTH = len(audio)/fs

def extract_sample(audio, tick):
    end = tick*FFT_WINDOW_SIZE
    begin = int(end - FFT_WINDOW_SIZE)

    if end == 0:
        # We have no audio yet, return all zeros (very beginning)
        return np.zeros((np.abs(begin)),dtype=float)
    elif begin<0:
        # We have some audio, padd with zeros
        return np.concatenate([np.zeros((np.abs(begin)),dtype=float),audio[0:end]])
    else:
        # Usually this happens, return the next sample
        return audio[begin:end]


print(len(audio))
for tick in range(int(len(audio)/FFT_WINDOW_SIZE)):
    sample = extract_sample(audio, tick)
    fft = np.fft.rfft(sample)
    for freq in fft:
        if 439 < freq.real < 441:
            if freq.imag > 0:
                print("la",freq.imag)
    #print(fft)
    #print("a")
