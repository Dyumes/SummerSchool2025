from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
import os
import numpy as np
import scipy
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import WriteMidiFile
import MidiComparison

AUDIO_FILE = os.path.join("media","wav","PinkPanther_Both.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav

FFT_WINDOW_SIZE = 2048         # 2048 -> 50ms, 21 Hrz //4096 -> 100ms, 10Hz
FFT_WINDOW_SECONDS = FFT_WINDOW_SIZE/fs # how many seconds of audio make up an FFT window
#FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
AUDIO_LENGTH_TICKS = len(audio)
AUDIO_LENGTH_SECONDS = len(audio)/fs    #audio length in seconds
freq_ana_precision = 0.1

ZERO_PADDING_FACTOR = 2 #doubles precision(time or frequency)

NOTE_NAMES = ["do", "do#", "ré", "ré#", "mi", "fa", "fa#", "sol", "sol#", "la", "la#", "si"]

STEP_NUMBER = int(len(audio)/FFT_WINDOW_SIZE)

BASE_TRESH = 100000
ANY_TRESH = 3000

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

sigma_factor = 8
hanningWindow = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, FFT_WINDOW_SIZE, False)))
gaussianWindow = scipy.signal.windows.gaussian(FFT_WINDOW_SIZE,FFT_WINDOW_SIZE/sigma_factor,False)

class Note :
    def __init__(self,freq,ampl):
        self.frequency = freq
        self.amplitude = ampl
        self.number = round_note_num(freq_to_number(self.frequency))        #number corresponding to note name

    def __str__(self):
        return f"|FEQ: {self.frequency} AMP: {self.amplitude} NOTE: {self.name()}|"

    def name(self): return NOTE_NAMES[self.number]

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
        elif window == "none":
            fft = rfft(sample,n=ZERO_PADDING_FACTOR*FFT_WINDOW_SIZE)

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

        i = 2 # if i = 1 and peak then i-1 = 0 = freq 0 Hz which will cause lots of problems
        while i < len(timeNote.notes):
            if timeNote.notes[i].amplitude > ANY_TRESH :
                while timeNote.notes[i].amplitude < timeNote.notes[i+1].amplitude:
                    i += 1
                if timeNote.notes[i].amplitude > timeNote.notes[i-1].amplitude:
                    if interp == "gaussian":
                        inter_max, inter_max_magnitude = interp_gaussian(timeNote.notes[i-1],timeNote.notes[i],timeNote.notes[i+1])
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


def getaudiblefreqs(notelist):
    audiblefreqs = []
    for note in notelist:
        if note.frequency < 2000 and note.frequency > 10 and note.amplitude > BASE_TRESH:
            if note.frequency < 1000 or note.amplitude > 1.5 * BASE_TRESH:
                audiblefreqs.append(note)
    return audiblefreqs

def get_feq_amp(values,step):
    frq = []
    amp = []
    for note in values[step].notes:
        frq.append(note.frequency)
        amp.append(note.amplitude)
    return frq, amp

def certainty(note):
    notes = [16.35, 17.32, 18.35, 19.44, 20.6, 21.82, 23.12, 24.5, 25.95, 27.5, 29.13, 30.86, 32.7, 34.64, 36.7, 38.89, 41.2, 43.65, 46.24, 48.99, 51.91, 54.99, 58.26, 61.73, 65.4, 69.29, 73.41, 77.77, 82.4, 87.3, 92.49, 97.99, 103.82, 109.99, 116.53, 123.46, 130.8, 138.58, 146.82, 155.55, 164.8, 174.6, 184.98, 195.98, 207.63, 219.98, 233.06, 246.92, 261.6, 277.16, 293.64, 311.1, 329.6, 349.19, 369.96, 391.96, 415.26, 439.96, 466.12, 493.84, 523.2, 554.31, 587.27, 622.19, 659.19, 698.39, 739.92, 783.91, 830.52, 880.0, 932.24, 987.68, 1046.48, 1108.62, 1174.55, 1244.37, 1318.38, 1396.78, 1479.83, 1567.82, 1661.23, 1760.0, 1864.48, 1975.37, 2092.95, 2217.25, 2349.09, 2488.73, 2636.75, 2793.55, 2959.65, 3135.65, 3322.45, 3520.0, 3728.96, 3950.74, 4185.9, 4434.5, 4698.18, 4977.46, 5273.5, 5587.1, 5919.29, 6271.3, 6644.9, 7040.0, 7457.91, 7901.48, 8371.8, 8869.0, 9396.37, 9954.92, 10547.01, 11174.21, 11838.59, 12542.6, 13289.79, 14080.0, 14915.83, 15803.0, 16743.59, 17739.01, 18792.75, 19909.84]

    i = 0
    while i < len(notes) :
        if notes[i] > note.frequency:
            high_freq = notes[i]
            low_freq = notes[i-1]
            i = len(notes)   #stop while
        i += 1
    diff = min(abs(note.frequency-low_freq),abs(note.frequency-high_freq))

    return diff/(high_freq-low_freq)

#piano_freqs = []

def get_median_harmonics(piano_freqs):
    #print(piano_freqs)
    full_piano_anal = []
    for i in range(9):
        full_piano_anal.append([])

    for bunch in piano_freqs:
        bunch = bunch[0]

        #print("Bunch:")

        #print(bunch)
        base_amp = bunch[0][1].amplitude

        single_note = True
        for i in range (1,len(bunch)):
            if bunch[i][0] == 1:
                single_note = False

        if single_note:     # if there is only one base note to get good freqs
            for note in bunch:
                if note[0]< 9:
                    #print(note[0],note[1].amplitude/base_amp)
                    full_piano_anal[note[0]].append(note[1].amplitude/base_amp)
    #print(full_piano_anal)
    for i in range(1,len(full_piano_anal)):
        full_piano_anal[i] = np.median(full_piano_anal[i])
    print(full_piano_anal)


def freq_anal(values):

    return_values_piano = []
    return_values_trumpet = []
    return_values_all = []
    return_values_raw = []

    for timeNote in values:
        base_notes = getaudiblefreqs(timeNote.notes)
        base_notes_ref = getaudiblefreqs(timeNote.notes)
        result = []

        for base_noteA in base_notes_ref:
            for base_noteB in base_notes_ref:           ## remove harmonics from basenotes
                fraction =  base_noteA.frequency/base_noteB.frequency
                fraction_excess = (fraction+0.5) %1 -0.5
                fraction_int = int(fraction-fraction_excess)
                #if timeNote.step == 170:
                #    print(base_noteA.frequency,base_noteB.frequency,fraction_excess)

                if abs(fraction_excess) < freq_ana_precision and fraction_int>1:
                    if base_noteA in base_notes:
                        base_notes.remove(base_noteA)

        for base_note in base_notes:
            bunch = []
            #print(certainty(base_note),base_note.frequency)
            for note in timeNote.notes:

                fraction =  note.frequency/base_note.frequency
                fraction_excess = (fraction+0.5) %1 -0.5
                fraction_int = int(fraction-fraction_excess)

                #if timeNote.step == 170:
                #    print(fraction_int,base_note.frequency,note,fraction_excess)

                if abs(fraction_excess) < freq_ana_precision:
                    bunch.append([fraction_int,note])

            result.append(bunch)

        r_piano = []
        r_trumpet = []
        r_all = []
        r_raw = []

        piano_comparison_mean = [0, np.float64(1.0), np.float64(0.6327285648288827), np.float64(0.2647386789612746), np.float64(0.17201458476639642), np.float64(0.13515905554207736), np.float64(0.10292263867561052), np.float64(0.11210653450368742), np.float64(0.08744076515106432)]
        trumpet_comparison_mean = [0, np.float64(1.0), np.float64(0.992499293761613), np.float64(0.6459633061734135), np.float64(0.31838611332848116), np.float64(0.21360601223562686), np.float64(0.11931605750938493), np.float64(0.08316339062309164), np.float64(0.0701687057473084)]

        piano_comparison_median = [[], np.float64(1.0), np.float64(0.4814294293182334), np.float64(0.10392308167988006), np.float64(0.10060534116654808), np.float64(0.08918406948375554), np.float64(0.044676543080990186), np.float64(0.07514166966407616), np.float64(0.034217232045258665)]
        trumpet_comparison_median = [[], np.float64(1.0), np.float64(1.0562095347338256), np.float64(0.7313740805027068), np.float64(0.2588301447131931), np.float64(0.15505121616392709), np.float64(0.07352018582192671), np.float64(0.0465575078627254), np.float64(0.030314936431951517)]

        piano_comparison_ecossaise = [[], np.float64(1.0), np.float64(0.9060887757894084), np.float64(0.3078628526315612), np.float64(0.42474040144621245), np.float64(0.24427959645602856), np.float64(0.19084171644421477), np.float64(0.19751781954808278), np.float64(0.1288031149753406)]
        trumpet_comparison_ecossaise = [[], np.float64(1.0), np.float64(0.7812244987387269), np.float64(0.5776206600479266), np.float64(0.33850899652676075), np.float64(0.25509798335514233), np.float64(0.23989290168227487), np.float64(0.15063101735291518), np.float64(0.08265174010236381)]

        piano_comparison = piano_comparison_median
        trumpet_comparison = trumpet_comparison_median

        for bunch in result:
            piano_indice:float = 0
            trumpet_indice:float = 0

            base_freq = bunch[0][1].amplitude
            for freq in bunch:
                if 0<freq[0]<= 3:

                    """
                    piano_indice += abs(piano_comparison[freq[0]]-(freq[1].amplitude/base_freq))
                    trumpet_indice += abs(trumpet_comparison[freq[0]]-(freq[1].amplitude/base_freq))
                    """
                    """
                    piano_indice += np.log(abs(1+piano_comparison[freq[0]]*base_freq-freq[1].amplitude))/freq[0]
                    trumpet_indice += np.log(abs(1+trumpet_comparison[freq[0]]*base_freq-freq[1].amplitude))/freq[0]
                    """
                    piano_indice += abs(np.log(piano_comparison[freq[0]]*base_freq / freq[1].amplitude))
                    trumpet_indice += abs(np.log(trumpet_comparison[freq[0]]*base_freq / freq[1].amplitude))

                    #print("piano_indice:",piano_indice)

                    #print("pian",piano_comparison[freq[0]]-(freq[1].amplitude/base_freq))
                    #print("trum",trumpet_comparison[freq[0]]-(freq[1].amplitude/base_freq))
            print("piano",piano_indice)
            print("trumpet", trumpet_indice)
            #print("trumpet",trumpet_indice)

            if len(bunch) >1:
                if piano_indice <= trumpet_indice:
                    r_piano.append(bunch[0][1])
                else:
                    r_trumpet.append(bunch[0][1])
                r_all.append(bunch[0][1])
                r_raw.append(bunch)



            #if len(bunch) >2:
            #        piano_freqs.append(bunch)



        return_values_piano.append(timeNotes(timeNote.step,r_piano))
        return_values_trumpet.append(timeNotes(timeNote.step,r_trumpet))
        return_values_all.append(timeNotes(timeNote.step,r_all))
        if r_raw != []:
            return_values_raw.append(r_raw)

    return return_values_piano, return_values_trumpet, return_values_all, return_values_raw

def hide_noise(values,strength):
    outvalues = []
    for i in range(1,len(values)-strength):
        enclosing_notes = []
        for note in values[i-1].notes:
            enclosing_notes.append(note.name())
        for note in values[i+strength].notes:
            enclosing_notes.append(note.name())

        outnotes = []

        for note in values[i].notes:
            name = note.name()
            if name in enclosing_notes:
                outnotes.append(note)
        outvalues.append(timeNotes(values[i].step,outnotes))

    if strength != 1:
        outvalues = hide_noise(outvalues,strength-1)

    return outvalues

def fill_gaps(values,strength):
    outvalues = []
    for i in range(1,len(values)-strength):
        before_notes = []
        after_names = []
        for note in values[i-1].notes:
            before_notes.append(note)
        for note in values[i+strength].notes:
            after_names.append(note.name())

        outnotes = []

        for before_note in before_notes:
            if before_note.name() in after_names:
                outnotes.append(before_note)
        for note in values[i].notes:
            if not note in outnotes:
                outnotes.append(note)

        outvalues.append(timeNotes(values[i].step,outnotes))

    if strength != 1:
        outvalues = fill_gaps(outvalues,strength-1)

    return outvalues

"""
unfiltered_values_gauss = dofft("gaussian")
unfiltered_values_hanning = dofft("hanning")
unfilterd_values_none = dofft("none")

gaussvalues = filter(unfiltered_values_gauss,"gaussian")
paravalues = filter(unfiltered_values_hanning,"parabolic")

allvalues = freq_anal(gaussvalues)

allvalues = hide_noise(hide_noise(allvalues,2),2)

printvalues(allvalues)
"""



def freezoom(event):
    ax.autoscale(enable=True, axis='x', tight=False)
    ax.set_xlim(left=0, right=20000)


def submit(text):
    step = eval(text)

    ax.cla()

    notes = [16.35, 17.32, 18.35, 19.44, 20.6, 21.82, 23.12, 24.5, 25.95, 27.5, 29.13, 30.86, 32.7, 34.64, 36.7, 38.89, 41.2, 43.65, 46.24, 48.99, 51.91, 54.99, 58.26, 61.73, 65.4, 69.29, 73.41, 77.77, 82.4, 87.3, 92.49, 97.99, 103.82, 109.99, 116.53, 123.46, 130.8, 138.58, 146.82, 155.55, 164.8, 174.6, 184.98, 195.98, 207.63, 219.98, 233.06, 246.92, 261.6, 277.16, 293.64, 311.1, 329.6, 349.19, 369.96, 391.96, 415.26, 439.96, 466.12, 493.84, 523.2, 554.31, 587.27, 622.19, 659.19, 698.39, 739.92, 783.91, 830.52, 880.0, 932.24, 987.68, 1046.48, 1108.62, 1174.55, 1244.37, 1318.38, 1396.78, 1479.83, 1567.82, 1661.23, 1760.0, 1864.48, 1975.37, 2092.95, 2217.25, 2349.09, 2488.73, 2636.75, 2793.55, 2959.65, 3135.65, 3322.45, 3520.0, 3728.96, 3950.74, 4185.9, 4434.5, 4698.18, 4977.46, 5273.5, 5587.1, 5919.29, 6271.3, 6644.9, 7040.0, 7457.91, 7901.48, 8371.8, 8869.0, 9396.37, 9954.92, 10547.01, 11174.21, 11838.59, 12542.6, 13289.79, 14080.0, 14915.83, 15803.0, 16743.59, 17739.01, 18792.75, 19909.84]
    ax.set_xticks(notes)
    """
    frq_unf_gauss, amp_unf_gauss = get_feq_amp(unfiltered_values_gauss,step)
    frq_fil_gauss, amp_fil_gauss = get_feq_amp(gaussvalues,step)

    frq_unf_hanning, amp_unf_hanning = get_feq_amp(unfiltered_values_hanning,step)
    frq_fil_para, amp_fil_para = get_feq_amp(paravalues,step)

    frq_unfil_none,amp_unfil_none = get_feq_amp(unfilterd_values_none,step)

    # Create a figure containing a single Axes.
    ax.plot(frq_unf_gauss,amp_unf_gauss,label="gauss window",color="red")# Plot some data on the Axes.
    ax.scatter(frq_unf_gauss,amp_unf_gauss, s=2)
    ax.scatter(frq_fil_gauss,amp_fil_gauss,label = "gauss interpolation", color ="orange")

    ax.plot(frq_unf_hanning,amp_unf_hanning,label="hanning window",color="blue")
    ax.scatter(frq_fil_para,amp_fil_para,label = "parabolic interpolation", color="green")

    ax.plot(frq_unfil_none,amp_unfil_none,label="no window",color="grey")
    """
    frq, amp = get_feq_amp(fftvalues,step)
    ax.plot(frq,amp)
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


def test_write_midi_file(piano_values,trumpet_values):
    # Test the creation of a MIDI file and adding a piano instrument
    file = WriteMidiFile.create_midi_file()
    WriteMidiFile.add_piano(file)
    WriteMidiFile.add_trumpet(file)
    file.instruments[0].name = "Piano"
    file.instruments[1].name = "Flute"
    print(file.instruments)


    # Add notes to the MIDI file
    for timeNote in piano_values:
        for note in timeNote.notes:

            WriteMidiFile.add_note(file.instruments[0], note.name(), timeNote.second, FFT_WINDOW_SECONDS)

    for timeNote in trumpet_values:
        for note in timeNote.notes:

            WriteMidiFile.add_note(file.instruments[1], note.name(), timeNote.second, FFT_WINDOW_SECONDS)

    # Save the MIDI file
    WriteMidiFile.write_midi_file(file, "media/midi/test_output.mid")
    print("MIDI file created successfully.")

    # Clean the MIDI file by merging overlapping notes
    WriteMidiFile.merge_notes("media/midi/test_output.mid", "media/midi/test_output_clean.mid")


#test_write_midi_file(allvalues)

fftvalues = dofft("gaussian")
totalvalues = filter(fftvalues,"gaussian")
piano_values,trumpet_values,allvalues,rawvalues = freq_anal(totalvalues)
get_median_harmonics(rawvalues)

piano_values = hide_noise(piano_values,2)
trumpet_values = hide_noise(trumpet_values,2)
totalvalues = hide_noise(totalvalues,2)

test_write_midi_file(piano_values,trumpet_values)


print("PIANO HEREEEEEEEEE")
printvalues(piano_values)
print("TRUMPET HEREEEEEEEEE")

printvalues(trumpet_values)

plot()



midi_a = os.path.join("media", "midi", "test_output_clean.mid")
midi_b = os.path.join("media", "midi", "PinkPanther.midi")
similarity, lcs_len, len1, len2 = MidiComparison.compare_midis(midi_a, midi_b)
print(f"Similarity: {similarity:.2f}%")

MidiComparison.detailed_comparison_visualizer(midi_a, midi_b, "Detailed comparison between generated and original MIDI")