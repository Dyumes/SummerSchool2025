import pretty_midi
import os
import pygame


def getNotes(pianoArr, fluteArr, data):
    for instrument in data.instruments:
        print(instrument)
        for note in instrument.notes:
            note.pitch %= 12
            if instrument.name == "Piano":
                pianoArr.append(note)
            elif instrument.name == "Flute":
                fluteArr.append(note)

# TEST

def drawNotes(notes, color, pos_y):
    for n in notes:
        pygame.draw.circle(screen, color, (100 + 100 * n.pitch, pos_y), 10)

# for e in piano_notes:
#     print(e)

if __name__ == "__main__":
    # INIT variables
    midi_data = pretty_midi.PrettyMIDI(os.path.join("media", "midi", "test_output_clean.mid"))
    # print(midi_data.estimate_tempo()) #Print estimate bpm (For the sun)

    tempo = 60 / midi_data.estimate_tempo()
    # print(tempo)

    piano_notes = []
    flute_notes = []
    active_piano_notes = []
    active_flute_notes = []
    current_piano_index = 0
    current_flute_index = 0

    # SETTINGS
    (width, height) = (1920, 1080)
    background_colour = (255, 255, 255)
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()


    # INIT
    getNotes(piano_notes, flute_notes, midi_data)
    pygame.display.flip()
    start_ticks = pygame.time.get_ticks()

    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join("media", "mp3", "Ecossaise_Both.mp3"))
    pygame.mixer.music.play()

    # Reorder Note by the starting time
    piano_notes = sorted(piano_notes, key=lambda note: note.start)
    flute_notes = sorted(flute_notes, key=lambda note: note.start)

    running = True
    while running:

        # Close the Windows if the button close is pressed
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            running = False
        # Programme
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0

        # detect if a piano notes should play
        while current_piano_index < len(piano_notes) and piano_notes[current_piano_index].start <= current_time:
            active_piano_notes.append(piano_notes[current_piano_index])
            current_piano_index += 1

        for n in active_piano_notes:
            if n.end <= current_time:
                active_piano_notes.remove(n)
        # detect if a flute notes should play
        while current_flute_index < len(flute_notes) and flute_notes[current_flute_index].start <= current_time:
            active_flute_notes.append(flute_notes[current_flute_index])
            current_flute_index += 1

        for n in active_flute_notes:
            if n.end <= current_time:
                active_flute_notes.remove(n)

        # Drawing things

        screen.fill(background_colour)
        drawNotes(active_piano_notes, (0,255,255), 500)
        drawNotes(active_flute_notes, (255,0,255), 700)


        # UPDATE the WINDOWS
        pygame.display.flip()

        # Manage refresh rate
        clock.tick(60)

    # END
    pygame.display.quit()