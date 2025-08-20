import pretty_midi

def note_name_to_pitch(note_name, octave=4):
    """
    Convert a note name to MIDI pitch value.

    Args:
        note_name (str): Note name.
        octave (int): Octave number.

    Returns:
        int: MIDI pitch value.
    """
    note_names = ["do", "do#", "ré", "ré#", "mi", "fa", "fa#", "sol", "sol#", "la", "la#", "si"]
    base_pitch = note_names.index(note_name)
    return base_pitch + 12 * (octave + 1)  # MIDI: C4 = 60

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


### Example usage in an other file

"""
import WriteMidiFile

def test_write_midi_file(notes):
    # Test the creation of a MIDI file and adding a piano instrument
    file = WriteMidiFile.create_midi_file()
    WriteMidiFile.add_piano(file)
    WriteMidiFile.add_trumpet(file)

    # Add notes to the MIDI file
    for note, duration, first_tick in notes:
        WriteMidiFile.add_note(file.instruments[0], note.name, first_tick, duration)

    # Save the MIDI file
    WriteMidiFile.write_midi_file(file, "media/midi/test_output.mid")
    print("MIDI file created successfully.")
"""
