from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from scipy import interpolate
import os
import numpy as np

AUDIO_FILE = os.path.join("media","wav","PinkPanther_Piano_Only.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav


FFT_WINDOW_SIZE = 4096 * 2
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

values = []

class Note :
    def __init__(self,freq,ampl):
        self.frequency = freq
        self.amplitude = ampl
    def __str__(self):
        return f"|feq: {self.frequency}, amp: {self.amplitude}|"

class timeNotes :
    def __init__(self,tick,freqs):
        self.frequencies = freqs
        self.tick = tick
    def __str__(self):
        return f"[tick: {self.tick}]"


for tick in range(int(len(audio)/FFT_WINDOW_SIZE)):
    sample = extract_sample(audio, tick)
    fft = rfft(sample * window)

    freqs = rfftfreq(FFT_WINDOW_SIZE,1/fs)

    idx = 1
    frequencies = []

    while idx<len(freqs):

        noteA = Note(freqs[idx],np.abs(fft[idx]))
        frequencies.append(noteA)

        idx += 1

    values.append(timeNotes(tick,frequencies))


for timeNote in values:
    i = 0
    while i < len(timeNote.frequencies):
        if timeNote.frequencies[i].amplitude > 1000000:
            while timeNote.frequencies[i].amplitude < timeNote.frequencies[i+1].amplitude:
                i += 1
            if timeNote.frequencies[i].amplitude > timeNote.frequencies[i-1].amplitude:
                print(f"local maxima: {timeNote.frequencies[i]} between {timeNote.frequencies[i-1]} and {timeNote.frequencies[i+1]}")

                x = [timeNote.frequencies[i-2].frequency, timeNote.frequencies[i-1].frequency, timeNote.frequencies[i].frequency, timeNote.frequencies[i+1].frequency,timeNote.frequencies[i+2].frequency]
                y = [timeNote.frequencies[i-2].amplitude, timeNote.frequencies[i-1].amplitude,timeNote.frequencies[i].amplitude,timeNote.frequencies[i+1].amplitude, timeNote.frequencies[i+2].amplitude,]
                f = interpolate.interp1d(x,y,"quadratic")
                inter_max = np.max(f.y)

                for j in range(len(f.y)):
                    if f.y[j] == inter_max:
                        print(f"interpolated maxima: frequency: {f.x[j]}, amplitude: {f.y[j]}")

        i += 1




"""
for value in values:
    print (value.tick/fs*FFT_WINDOW_SIZE)
    for j in value.frequencies:
        if j.amplitude > 1000000:
            print(j)
"""
