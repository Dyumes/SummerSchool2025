from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from scipy import interpolate
import os
import numpy as np

AUDIO_FILE = os.path.join("media","wav","PinkPanther_Piano_Only.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav


FFT_WINDOW_SIZE = 4096          # 2048 -> 50ms, 21 Hrz //4096 -> 100ms, 10Hz
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

def humanreadvalues():
    for timeNote in values:
        i = 0
        print("____________________________________")
        print("SECONDS: ",timeNote.tick/fs*FFT_WINDOW_SIZE)
        print("tick:", timeNote.tick*FFT_WINDOW_SIZE)
        while i < len(timeNote.frequencies):
            if timeNote.frequencies[i].amplitude > 1500000:
                while timeNote.frequencies[i].amplitude < timeNote.frequencies[i+1].amplitude:
                    i += 1
                if timeNote.frequencies[i].amplitude > timeNote.frequencies[i-1].amplitude:
                    print(f"local maximum: {timeNote.frequencies[i]} between {timeNote.frequencies[i-1]} and {timeNote.frequencies[i+1]}")

                    p = (timeNote.frequencies[i+1].amplitude - timeNote.frequencies[i-1].amplitude) /2 /(2*timeNote.frequencies[i].amplitude - timeNote.frequencies[i-1].amplitude - timeNote.frequencies[i+1].amplitude)
                    inter_max = timeNote.frequencies[i].frequency + p*(timeNote.frequencies[i].frequency - timeNote.frequencies[i-1].frequency)
                    print("interpolated maximum:", inter_max)
                    print("estimated note:", NOTE_NAMES[round_note_num(freq_to_number(inter_max))])

            i += 1

#humanreadvalues()

def filter(values):
    newvalues = []
    for timeNote in values:
        frequencies = []

        i = 0
        while i < len(timeNote.frequencies):
            if timeNote.frequencies[i].amplitude > 500000:
                while timeNote.frequencies[i].amplitude < timeNote.frequencies[i+1].amplitude:
                    i += 1
                if timeNote.frequencies[i].amplitude > timeNote.frequencies[i-1].amplitude:

                    p = (timeNote.frequencies[i+1].amplitude - timeNote.frequencies[i-1].amplitude) /2 /(2*timeNote.frequencies[i].amplitude - timeNote.frequencies[i-1].amplitude - timeNote.frequencies[i+1].amplitude)
                    inter_max = timeNote.frequencies[i].frequency + p*(timeNote.frequencies[i].frequency - timeNote.frequencies[i-1].frequency)
                    inter_max_magnitude = timeNote.frequencies[i].amplitude- (timeNote.frequencies[i-1].amplitude - timeNote.frequencies[i].amplitude)*p/4

                    newNote = Note(inter_max,inter_max_magnitude)
                    frequencies.append(newNote)


            i += 1

        newvalues.append(timeNotes(timeNote.tick,frequencies))

    return newvalues

values = filter(values)

def printvalues(values):
    for timeNote in values:
        print("_______________")
        print("tick: ",timeNote.tick*FFT_WINDOW_SIZE, "seconds: ",timeNote.tick/fs*FFT_WINDOW_SIZE)
        for note in timeNote.frequencies:
            print("FREQ: ",note.frequency ,"AMP: " ,note.amplitude,"NOTE: ",NOTE_NAMES[round_note_num(freq_to_number(note.frequency))] )

#printvalues(values)


def pianovtrumpet(values):
    trumpetvalues = []
    pianovalues = []

    for timeNote in values:
        frequencies = timeNote.frequencies
        trumpetfrequencises = []
        pianofrequencies = []
        notes = []
        for note in frequencies:
            if note.frequency <= 1000 and note.amplitude > 1500000:
                notes.append([note.frequency, note.amplitude, NOTE_NAMES[round_note_num(freq_to_number(note.frequency))]])
            if note.frequency > 1000:
                searchednote = NOTE_NAMES[round_note_num(freq_to_number(note.frequency))]
                for i in range(len(notes)):
                    if searchednote == notes[i][2]:
                        if notes[i][1] < note.amplitude:
                            pianofrequencies.append(searchednote)
                        else:
                            trumpetfrequencises.append(searchednote)

        trumpetvalues.append([timeNote.tick,trumpetfrequencises])
        pianovalues.append([timeNote.tick,pianofrequencies])


    return trumpetvalues, pianovalues

trumpetnotes,pianonotes = pianovtrumpet(values)

for timeNote in trumpetnotes:
    print("_______________")
    print("tick: ",timeNote[0]*FFT_WINDOW_SIZE, "seconds: ",timeNote[0]/fs*FFT_WINDOW_SIZE)
    for note in timeNote[1]:
        print(note)


for timeNote in pianonotes:
    print("_______________")
    print("tick: ",timeNote[0]*FFT_WINDOW_SIZE, "seconds: ",timeNote[0]/fs*FFT_WINDOW_SIZE)
    for note in timeNote[1]:
        print(note)





"""
for value in values:
    print (value.tick/fs*FFT_WINDOW_SIZE)
    for j in value.frequencies:
        if j.amplitude > 1000000:
            print(j)
"""
