from scipy.fft import rfft
from scipy.io import wavfile
import os
import numpy as np


AUDIO_FILE = os.path.join("media","wav","test.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav


FFT_WINDOW_SIZE = 2048
FFT_WINDOW_SECONDS = FFT_WINDOW_SIZE/fs # how many seconds of audio make up an FFT window


#FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
AUDIO_LENGTH = len(audio)/fs

NOTE_NAMES = ["do", "do#", "ré", "ré#", "mi", "fa", "fa#", "sol", "sol#", "la", "la#", "si"]

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


def freq_to_number(freq): return (69 + 12*np.log2(freq/440.0))%12
def round_note_num(num): return int(round(num,0))%12

# Hanning window function
window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, FFT_WINDOW_SIZE, False)))

print(len(audio))
print(FFT_WINDOW_SECONDS)
for tick in range(int(len(audio)/FFT_WINDOW_SIZE)):
    sample = extract_sample(audio, tick)
    fft = rfft(sample * window)
    for freq in fft:
        if 1000 >= freq.real >= 10:
            note_num = freq_to_number(freq.real)
            if (note_num % 1) < 0.005 or (note_num % 1) > 0.995:
                if abs(freq.imag) > 1000:
                    note_num = round_note_num(note_num)
                    print("tick:",(tick*FFT_WINDOW_SIZE) ,"second:",round((tick*FFT_WINDOW_SIZE/fs),4) ,NOTE_NAMES[note_num],"frequency:",freq.real,"intensity:", round(freq.imag,0))

#print(round_note_num(freq_to_number(440)))
#print(round_note_num(freq_to_number(16.35)))

#print(NOTE_NAMES[round_note_num(freq_to_number(16.35))])