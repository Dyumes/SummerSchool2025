import pretty_midi

def note_name_to_pitch(note_name, octave=4):
    note_names = ["do", "do#", "ré", "ré#", "mi", "fa", "fa#", "sol", "sol#", "la", "la#", "si"]
    base_pitch = note_names.index(note_name)
    return base_pitch + 12 * (octave + 1)  # MIDI: C4 = 60

def ticks_to_seconds(ticks, fft_window_seconds):
    return ticks * fft_window_seconds

def add_note(instrument, note_name, start_tick, duration, octave=4):
    pitch = note_name_to_pitch(note_name, octave)
    start_time = ticks_to_seconds(start_tick, 0.1)  # Assuming 0.1 seconds per tick
    end_time = ticks_to_seconds(start_tick+duration, 0.1)
    instrument.notes.append(pretty_midi.Note(100, pitch, start_time, end_time))

def create_piano():
    return pretty_midi.Instrument(program=0)

def create_trumpet():
    return pretty_midi.Instrument(program=56)

def add_piano(file):
    file.instruments.append(create_piano())

def add_trumpet(file):
    file.instruments.append(create_trumpet())

def create_midi_file():
    return pretty_midi.PrettyMIDI()

def write_midi_file(midi, filename):
    midi.write(filename)