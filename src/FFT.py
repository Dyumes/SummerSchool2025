from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
import os
import numpy as np
import scipy
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import WriteMidiFile

AUDIO_FILE = os.path.join("media","wav","PinkPanther_Piano_Only.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav

FFT_WINDOW_SIZE = 2048          # 2048 -> 50ms, 21 Hrz //4096 -> 100ms, 10Hz
FFT_WINDOW_SECONDS = FFT_WINDOW_SIZE/fs # how many seconds of audio make up an FFT window
#FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
AUDIO_LENGTH_TICKS = len(audio)
AUDIO_LENGTH_SECONDS = len(audio)/fs    #audio length in seconds

ZERO_PADDING_FACTOR = 2 #doubles precision(time or frequency)

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
gaussianWindow = scipy.signal.windows.gaussian(FFT_WINDOW_SIZE,FFT_WINDOW_SIZE/8,False)

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

def dofft(window):
    values = []
    for step in range(STEP_NUMBER):
        sample = extract_sample(audio, step)
        if window == "hanning":
            fft = rfft(sample*hanningWindow,n=ZERO_PADDING_FACTOR*FFT_WINDOW_SIZE)
        elif window == "gaussian":
            fft = rfft(sample*gaussianWindow,n=ZERO_PADDING_FACTOR*FFT_WINDOW_SIZE)

        freqs = rfftfreq(ZERO_PADDING_FACTOR*FFT_WINDOW_SIZE,1/fs)

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


def interp_parabolic(x_1, x, x1):
    p = -(x_1.amplitude - x1.amplitude) /2 /(2*x.amplitude - x_1.amplitude - x1.amplitude)
    max = x.frequency +p*(x.frequency - x_1.frequency)
    max_magnitude = x.amplitude- (x_1.amplitude - x1.amplitude)*p/4

    return max, max_magnitude

def interp_gaussian(x_1, x, x1):
    #delta = (np.log(x1.amplitude/x_1.amplitude))/2/(np.log(np.square(x.amplitude))/x_1.amplitude*x1.amplitude)

    p = -(np.log(x_1.amplitude) - np.log(x1.amplitude)) /2 /(2*np.log(x.amplitude) - np.log(x_1.amplitude) - np.log(x1.amplitude))
    max = x.frequency +p*(x.frequency - x_1.frequency)
    max_magnitude = x.amplitude- (x_1.amplitude - x1.amplitude)*p/4

    return max, max_magnitude


def filter(values,interp):
    newvalues = []
    for timeNote in values:
        notes = []

        i = 0
        while i < len(timeNote.notes):
            if timeNote.notes[i].amplitude > 100000:
                while timeNote.notes[i].amplitude < timeNote.notes[i+1].amplitude:
                    i += 1
                if timeNote.notes[i].amplitude > timeNote.notes[i-1].amplitude:
                    if interp == "gaussian":
                        inter_max, inter_max_magnitude = interp_parabolic(timeNote.notes[i-1],timeNote.notes[i],timeNote.notes[i+1])
                    else:
                        inter_max, inter_max_magnitude = interp_parabolic(timeNote.notes[i-1],timeNote.notes[i],timeNote.notes[i+1])

                    newNote = Note(inter_max,inter_max_magnitude)
                    notes.append(newNote)

            i += 1

        newvalues.append(timeNotes(timeNote.step,notes))
    return newvalues



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
                if harmonicslist[0].frequency < 1000 and harmonicslist[0].amplitude > 400000:

                    if harmonicslist[0].amplitude *1.8 < harmonicslist[1].amplitude:
                        trumpetnotes.append(harmonicslist[0])
                    else:
                        pianonotes.append(harmonicslist[0])
                    allnotes.append(harmonicslist[0])

        trumpetvalues.append(timeNotes(timeNote.step,trumpetnotes))
        pianovalues.append(timeNotes(timeNote.step,pianonotes))
        allvalues.append(timeNotes(timeNote.step,allnotes))

    return trumpetvalues,pianovalues,allvalues



unfiltered_values_gauss = dofft("gaussian")
unfiltered_values_hanning = dofft("hanning")

gaussvalues = filter(unfiltered_values_gauss,"gaussian")
paravalues = filter(unfiltered_values_hanning,"parabolic")

trumpetvalues, pianovalues, allvalues = pianovtrumpet(gaussvalues)

printvalues(allvalues)
printvalues(pianovalues)

def get_feq_amp(values,step):
    frq = []
    amp = []
    for note in values[step].notes:
        frq.append(note.frequency)
        amp.append(note.amplitude)
    return frq, amp



def freezoom(event):
    ax.autoscale(enable=True, axis='x', tight=False)
    ax.set_xlim(left=0, right=20000)


def submit(text):
    step = eval(text)

    ax.cla()

    notes = [16.35, 17.32, 18.35, 19.44, 20.6, 21.82, 23.12, 24.5, 25.95, 27.5, 29.13, 30.86, 32.7, 34.64, 36.7, 38.89, 41.2, 43.65, 46.24, 48.99, 51.91, 54.99, 58.26, 61.73, 65.4, 69.29, 73.41, 77.77, 82.4, 87.3, 92.49, 97.99, 103.82, 109.99, 116.53, 123.46, 130.8, 138.58, 146.82, 155.55, 164.8, 174.6, 184.98, 195.98, 207.63, 219.98, 233.06, 246.92, 261.6, 277.16, 293.64, 311.1, 329.6, 349.19, 369.96, 391.96, 415.26, 439.96, 466.12, 493.84, 523.2, 554.31, 587.27, 622.19, 659.19, 698.39, 739.92, 783.91, 830.52, 880.0, 932.24, 987.68, 1046.48, 1108.62, 1174.55, 1244.37, 1318.38, 1396.78, 1479.83, 1567.82, 1661.23, 1760.0, 1864.48, 1975.37, 2092.95, 2217.25, 2349.09, 2488.73, 2636.75, 2793.55, 2959.65, 3135.65, 3322.45, 3520.0, 3728.96, 3950.74, 4185.9, 4434.5, 4698.18, 4977.46, 5273.5, 5587.1, 5919.29, 6271.3, 6644.9, 7040.0, 7457.91, 7901.48, 8371.8, 8869.0, 9396.37, 9954.92, 10547.01, 11174.21, 11838.59, 12542.6, 13289.79, 14080.0, 14915.83, 15803.0, 16743.59, 17739.01, 18792.75, 19909.84]
    ax.set_xticks(notes)

    frq_unf_gauss, amp_unf_gauss = get_feq_amp(unfiltered_values_gauss,step)
    frq_fil_gauss, amp_fil_gauss = get_feq_amp(gaussvalues,step)

    frq_unf_hanning, amp_unf_hanning = get_feq_amp(unfiltered_values_hanning,step)
    frq_fil_para, amp_fil_para = get_feq_amp(paravalues,step)

    # Create a figure containing a single Axes.
    ax.plot(frq_unf_gauss,amp_unf_gauss,label="gauss window",color="red")# Plot some data on the Axes.
    ax.scatter(frq_unf_gauss,amp_unf_gauss, s=2)
    ax.scatter(frq_fil_gauss,amp_fil_gauss,label = "gauss interpolation", color ="orange")

    ax.plot(frq_unf_hanning,amp_unf_hanning,label="hanning window",color="blue")
    ax.scatter(frq_fil_para,amp_fil_para,label = "parabolic interpolation", color="green")

    ax.legend()
    ax.grid()

    ax.set_xlim(left=0, right=1000)

    plt.draw()

def plot():

    axzoom = plt.axes([0.81, 0.01, 0.1, 0.04])
    bzoom = Button(axzoom, 'full view')
    bzoom.on_clicked(freezoom)

    initial = "160"
    text_box = TextBox(plt.axes([0.4, 0.01, 0.1, 0.04]), 'Step', initial=initial)
    submit(initial)
    text_box.on_submit(submit)

    plt.show()

fig, ax = plt.subplots()
plot()



