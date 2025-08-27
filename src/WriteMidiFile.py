import os
import pretty_midi


def note_name_to_pitch(note_name, octave=4):
    """
    Convert a note name to MIDI pitch value.

    Args:
        note_name: Note name.
        octave (int): Octave number.

    Returns:
        int: MIDI pitch value.
    """
    if isinstance(note_name, str):
        note_names = ["do", "do#", "ré", "ré#", "mi", "fa", "fa#", "sol", "sol#", "la", "la#", "si"]
        base_pitch = note_names.index(note_name)
        return base_pitch + 12 * (octave + 1)  # MIDI: C4 = 60

    return note_name

def ticks_to_seconds(ticks):
    """
    Convert ticks to seconds using the FFT window duration.

    Args:
        ticks (int): Number of ticks.

    Returns:
        float: Time in seconds.
    """
    return ticks

def add_note(instrument, note_name, start_tick, duration, octave=4):
    """
    Add a note to a PrettyMIDI instrument.

    Args:
        instrument (pretty_midi.Instrument): The instrument to add the note to.
        note_name (str): Note name.
        start_tick (int): Start tick of the note.
        duration (int): Duration in ticks.
        octave (int): Octave number.
    """
    pitch = note_name_to_pitch(note_name, octave)
    start_time = ticks_to_seconds(start_tick)
    end_time = ticks_to_seconds(start_tick+duration)
    instrument.notes.append(pretty_midi.Note(100, pitch, start_time, end_time))

def create_piano():
    """
    Create a PrettyMIDI piano instrument.

    Returns:
        pretty_midi.Instrument: Piano instrument.
    """
    return pretty_midi.Instrument(program=0)

def create_trumpet():
    """
    Create a PrettyMIDI trumpet instrument.

    Returns:
        pretty_midi.Instrument: Trumpet instrument.
    """
    return pretty_midi.Instrument(program=56)

def add_piano(file):
    """
    Add a piano instrument to a PrettyMIDI file.

    Args:
        file: The MIDI file.
    """
    file.instruments.append(create_piano())

def add_trumpet(file):
    """
    Add a trumpet instrument to a PrettyMIDI file.

    Args:
        file: The MIDI file.
    """
    file.instruments.append(create_trumpet())

def create_midi_file():
    """
    Create a new PrettyMIDI file.

    Returns:
        pretty_midi.PrettyMIDI: New MIDI file.
    """
    return pretty_midi.PrettyMIDI()

def write_midi_file(midi, filename):
    """
    Write a PrettyMIDI file to disk.

    Args:
        midi: The MIDI file.
        filename (str): Output file name.
    """
    midi.write(filename)

def get_all_notes(filename):
    data = pretty_midi.PrettyMIDI(filename)
    notes = []
    for instrument in data.instruments:
        for note in instrument.notes:
            notes.append({
                "pitch": note.pitch,
                "start": note.start,
                "end": note.end,
                "velocity": note.velocity,
                "instrument": instrument.program,
                "octave": (note.pitch // 12) - 1
            })
    return notes

def separate_instruments(notes):
    piano_notes = []
    trumpet_notes = []
    for note in notes:
        if note["instrument"] == 0:
            piano_notes.append(note)
        elif note["instrument"] == 56:
            trumpet_notes.append(note)
    return piano_notes, trumpet_notes

def sort_notes_by_start(notes):
    return sorted(notes, key=lambda note: note["start"])

def sort_notes_by_pitch(notes):
    return sorted(notes, key=lambda note: note["pitch"])

def concat_notes(notes):

    if not notes:
        return []

    # Sort notes by pitch, then by start time
    notes.sort(key=lambda n: (n["pitch"], n["start"]))

    merged_notes = []
    current = notes[0]

    for next_note in notes[1:]:
        if next_note["pitch"] == current["pitch"] and next_note["start"] <= current["end"]:
            # Merge overlapping/consecutive notes
            current["end"] = max(current["end"], next_note["end"])
            current["velocity"] = max(current["velocity"], next_note["velocity"])
        else:
            merged_notes.append(current)
            current = next_note

    merged_notes.append(current)
    return merged_notes

def merge_notes(filename, new_filename):
    piano_notes, trumpet_notes = separate_instruments(get_all_notes(filename))
    piano_notes_concat = concat_notes(piano_notes)
    trumpet_notes_concat = concat_notes(trumpet_notes)

    file = create_midi_file()
    add_piano(file)
    add_trumpet(file)

    # Add notes to the MIDI file
    if piano_notes_concat:
        print("Traitement des notes de piano")
        for note in piano_notes_concat:
            #print("Piano note:", note)
            add_note(file.instruments[0], note["pitch"], note["start"], (note["end"] - note["start"]))


    if trumpet_notes_concat:
        print("Traitement des notes de trompette")
        for note in trumpet_notes_concat:
            add_note(file.instruments[1], note["pitch"], note["start"], (note["end"] - note["start"]))

    # Save the MIDI file
    write_midi_file(file, new_filename)
    print("MIDI file created successfully.")

if __name__ == "__main__":
    # piano_notes, trumpet_notes = separate_instruments(get_all_notes(os.path.join("media", "midi", "test_output.mid")))
    #
    # piano_notes_concat = concat_notes(piano_notes)
    # trumpet_notes_concat = concat_notes(trumpet_notes)

    merge_notes(os.path.join("media", "midi", "test_output.mid"), os.path.join("media", "midi", "test_output_clean.mid"))



