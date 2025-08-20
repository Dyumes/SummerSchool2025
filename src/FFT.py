from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
import os
import numpy as np

AUDIO_FILE = os.path.join("media","wav","PinkPanther_Piano_Only.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav

FFT_WINDOW_SIZE = 4096          # 2048 -> 50ms, 21 Hrz //4096 -> 100ms, 10Hz
FFT_WINDOW_SECONDS = FFT_WINDOW_SIZE/fs # how many seconds of audio make up an FFT window
#FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
AUDIO_LENGTH_TICKS = len(audio)
AUDIO_LENGTH_SECONDS = len(audio)/fs    #audio length in seconds

NOTE_NAMES = ["do", "do#", "ré", "ré#", "mi", "fa", "fa#", "sol", "sol#", "la", "la#", "si"]

STEP_NUMBER = int(len(audio)/FFT_WINDOW_SIZE)

def extract_sample(audio, step):    #exctrats window size sample from audio with zero-padding
    end = step*FFT_WINDOW_SIZE
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
hanningWindow = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, FFT_WINDOW_SIZE, False)))

class Note :
    def __init__(self,freq,ampl):
        self.frequency = freq
        self.amplitude = ampl
        self.number = round_note_num(freq_to_number(self.frequency))        #number corresponding to note name
        self.name = NOTE_NAMES[self.number]

    def __str__(self):
        return f"|FEQ: {self.frequency} AMP: {self.amplitude} NOTE: {self.name}|"

class timeNotes :
    def __init__(self,step,notes):
        self.notes = notes
        self.step = step
        self.tick = self.step*FFT_WINDOW_SIZE
        self.second = self.tick/fs
    def __str__(self):
        string =f"[step: {self.step}  second = {self.second}]"
        for note in self.notes:
            string += str(note)
        return string

def dofft():
    values = []
    for step in range(STEP_NUMBER):
        sample = extract_sample(audio, step)
        fft = rfft(sample * hanningWindow)

        freqs = rfftfreq(FFT_WINDOW_SIZE,1/fs)

        idx = 1
        notes = []

        while idx<len(freqs):

            noteA = Note(freqs[idx],np.abs(fft[idx]))       #frequence and amplitude put into note
            notes.append(noteA)

            idx += 1

        values.append(timeNotes(step,notes))
    return values

print(AUDIO_LENGTH_TICKS)
print(FFT_WINDOW_SECONDS)
values = dofft()

def interp_quadratic(x_1, x, x1):
    p = (x_1.amplitude - x1.amplitude) /2 /(2*x.amplitude - x_1.amplitude - x1.amplitude)
    max = x.frequency +p*(x.frequency - x_1.frequency)
    max_magnitude = x.amplitude- (x_1.amplitude - x1.amplitude)*p/4

    return max, max_magnitude

def filter(values):
    newvalues = []
    for timeNote in values:
        notes = []

        i = 0
        while i < len(timeNote.notes):
            if timeNote.notes[i].amplitude > 80000:
                while timeNote.notes[i].amplitude < timeNote.notes[i+1].amplitude:
                    i += 1
                if timeNote.notes[i].amplitude > timeNote.notes[i-1].amplitude:

                    inter_max, inter_max_magnitude = interp_quadratic(timeNote.notes[i-1],timeNote.notes[i],timeNote.notes[i+1])
                    newNote = Note(inter_max,inter_max_magnitude)
                    notes.append(newNote)
            i += 1

        newvalues.append(timeNotes(timeNote.step,notes))
    return newvalues

values = filter(values)

def printvalues(values):
    for timeNote in values:
        print(timeNote)

#printvalues(values)


def getharmonics(notelist,name):
    harmonicslist = []
    for note in notelist:
        if note.name == name:
            harmonicslist.append(note)
    return harmonicslist

def pianovtrumpet(values):
    trumpetvalues = []
    pianovalues = []
    allvalues = []

    for timeNote in values:
        trumpetnotes = []
        pianonotes = []
        allnotes = []

        for name in NOTE_NAMES:
            harmonicslist = getharmonics(timeNote.notes,name)
            if len(harmonicslist)>1:
                if harmonicslist[0].frequency < 1000 and harmonicslist[0].amplitude > 800000:

                    if harmonicslist[0].amplitude *1.8 < harmonicslist[1].amplitude:
                        trumpetnotes.append(harmonicslist[0])
                    else:
                        pianonotes.append(harmonicslist[0])
                    allnotes.append(harmonicslist[0])

        trumpetvalues.append(timeNotes(timeNote.step,trumpetnotes))
        pianovalues.append(timeNotes(timeNote.step,pianonotes))
        allvalues.append(timeNotes(timeNote.step,allnotes))

    return trumpetvalues,pianovalues,allvalues


trumpetvalues, pianovalues,allvalues = pianovtrumpet(values)

printvalues(allvalues)
printvalues(pianovalues)