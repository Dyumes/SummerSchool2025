from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from scipy import interpolate
import os
import numpy as np

AUDIO_FILE = os.path.join("media","wav","PinkPanther_Piano_Only.wav")

fs, data = wavfile.read(AUDIO_FILE)  #Return the sample rate (in samples/sec) and data from an LPCM WAV file
audio = data.T[0]       # 1st channel of wav


FFT_WINDOW_SIZE = 4096
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

#values = []

class Note :
    def __init__(self,freq,ampl):
        self.frequency = freq
        self.amplitude = ampl
    def __str__(self):
        return f"|feq: {self.frequency}, amp: {self.amplitude}|"

class TimeNotes :
    def __init__(self,tick,freqs):
        self.frequencies = freqs
        self.tick = tick
    def __str__(self):
        return f"[tick: {self.tick}]"


def compute_time_notes(audio, window, FFT_WINDOW_SIZE, fs):
    values = []
    for tick in range(int(len(audio)/FFT_WINDOW_SIZE)):
        sample = extract_sample(audio, tick)
        fft = rfft(sample * window)
        freqs = rfftfreq(FFT_WINDOW_SIZE, 1/fs)
        idx = 1
        frequencies = []
        while idx < len(freqs):
            noteA = Note(freqs[idx], np.abs(fft[idx]))
            frequencies.append(noteA)
            idx += 1
        values.append(TimeNotes(tick, frequencies))
    return values


def find_estimated_note(values, fs, FFT_WINDOW_SIZE, NOTE_NAMES):
    previous_note = None
    note_start_tick = None
    notes_with_duration = []

    for timeNote in values:
        i = 0
        while i < len(timeNote.frequencies):
            if timeNote.frequencies[i].amplitude > 2000000:
                while i + 1 < len(timeNote.frequencies) and timeNote.frequencies[i].amplitude < timeNote.frequencies[i + 1].amplitude:
                    i += 1

                estimated_note = None
                if i > 0 and i + 1 < len(timeNote.frequencies) and timeNote.frequencies[i].amplitude > timeNote.frequencies[i - 1].amplitude:
                    inter_max = timeNote.frequencies[i].frequency + (
                        (timeNote.frequencies[i + 1].amplitude - timeNote.frequencies[i - 1].amplitude) / 2 /
                        (2 * timeNote.frequencies[i].amplitude - timeNote.frequencies[i - 1].amplitude - timeNote.frequencies[i + 1].amplitude)
                    ) * (timeNote.frequencies[i].frequency - timeNote.frequencies[i - 1].frequency)
                    estimated_note = NOTE_NAMES[round_note_num(freq_to_number(inter_max))]

                if estimated_note is not None:
                    if estimated_note != previous_note:
                        if previous_note is not None and note_start_tick is not None:
                            duration = timeNote.tick - note_start_tick
                            notes_with_duration.append((previous_note, duration, note_start_tick))
                        previous_note = estimated_note
                        note_start_tick = timeNote.tick
            i += 1

    if previous_note is not None and note_start_tick is not None:
        duration = (values[-1].tick + 1) - note_start_tick
        notes_with_duration.append((previous_note, duration, note_start_tick))

    notes_with_duration = [(note, duration, start_tick) for note, duration, start_tick in notes_with_duration if duration > 0]
    return notes_with_duration


def merge_short_notes(notes_with_duration):
    merged = []
    for note, duration, start_tick in notes_with_duration:
        if duration == 1 and merged and merged[-1][0] == note:
            # Fusionne avec la note précédente, conserve le start_tick initial
            prev_note, prev_duration, prev_start_tick = merged[-1]
            merged[-1] = (note, prev_duration + 1, prev_start_tick)
        else:
            merged.append((note, duration, start_tick))
    return merged

# def add_silences(notes_with_duration):
#     notes_and_silences = []
#
#     for i in range(len(notes_with_duration) -1):
#         if notes_with_duration[i+1][2] > (notes_with_duration[i][2] + notes_with_duration[i][1]):
#             silence_duration = notes_with_duration[i+1][2] - (notes_with_duration[i][2] + notes_with_duration[i][1])
#             notes_and_silences.append((notes_with_duration[i][0], notes_with_duration[i][1], notes_with_duration[i][2]))
#             notes_and_silences.append(("silence", silence_duration, notes_with_duration[i][2] + notes_with_duration[i][1]))
#         else:
#             notes_and_silences.append((notes_with_duration[i][0], notes_with_duration[i][1], notes_with_duration[i][2]))
#
#     # Add the last note
#     notes_and_silences.append((notes_with_duration[-1][0], notes_with_duration[-1][1], notes_with_duration[-1][2]))
#
#     # Add silence at the end
#     notes_and_silences.append(("silence", 10, notes_with_duration[-1][2] + notes_with_duration[-1][1]))
#
#     return notes_and_silences

values = compute_time_notes(audio, window, FFT_WINDOW_SIZE, fs)
notesAndDuration = find_estimated_note(values, fs, FFT_WINDOW_SIZE, NOTE_NAMES)
notesAndDuration = merge_short_notes(notesAndDuration)
#notesAndDuration = add_silences(notesAndDuration)
for note, duration, start_tick in notesAndDuration:
    print(f"Note: {note}, Duration (ticks) : {duration} ({duration * FFT_WINDOW_SECONDS:.5f} seconds), First tick : {start_tick}")

### TEST WRITE MIDI FILE
import test

test.test_write_midi_file(notesAndDuration, FFT_WINDOW_SECONDS)

"""
for value in values:
    print (value.tick/fs*FFT_WINDOW_SIZE)
    for j in value.frequencies:
        if j.amplitude > 1000000:
            print(j)
"""
