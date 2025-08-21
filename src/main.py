import pygame
import ReadMidiFile as rmf
import os
import pretty_midi
import Generation as gn
from win32api import GetSystemMetrics

#INIT variables
midi_data = pretty_midi.PrettyMIDI(os.path.join("media","midi","Ecossaise_Beethoven.midi"))
tempo_times, tempi = midi_data.get_tempo_changes()

piano_notes = []
flute_notes = []
active_piano_notes = []
active_flute_notes = []
current_piano_index = 0
current_flute_index = 0
current_bpm_index = 0

startSong = False

fps = 60

# SETTINGS
(width, height) = (GetSystemMetrics(0) - 100, GetSystemMetrics(1) - 100)
background_colour = (0,0,0)
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# INIT
rmf.getNotes(piano_notes, flute_notes, midi_data)
pygame.display.flip()
start_ticks = pygame.time.get_ticks()

pygame.mixer.init()
pygame.mixer.music.load(os.path.join("media", "mp3", "Ecossaise_Both.mp3"))

# Reorder Note by the starting time
piano_notes = sorted(piano_notes, key=lambda note: note.start)
flute_notes = sorted(flute_notes, key=lambda note: note.start)

def detectTrumpetNotes(notes):
    for n in notes:
        gn.changeMountainAnimiationTime(n.duration,n.pitch)
        gn.changeMountainStartTime(current_time, n.pitch)
        gn.changeMountainMaxHeight(n.velocity * 2,n.pitch)
        gn.playTrumpet(n.pitch)

if __name__ == "__main__":
    running = True
    while running:
        # Close the Windows if the button close is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        if not startSong:
                            startSong = True
                            pygame.mixer.music.play()
                            start_ticks = pygame.time.get_ticks()

        # Programme
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0

        if startSong:
            # detect if a piano notes should play
            while current_piano_index < len(piano_notes) and piano_notes[current_piano_index].start <= current_time:
                active_piano_notes.append(piano_notes[current_piano_index])
                current_piano_index += 1

            # detect if a flute notes should play
            while current_flute_index < len(flute_notes) and flute_notes[current_flute_index].start <= current_time:
                active_flute_notes.append(flute_notes[current_flute_index])
                current_flute_index += 1

            bpm = tempi[current_bpm_index]
            if len(tempo_times) != current_bpm_index + 1:
                if current_time >= tempo_times[current_bpm_index + 1]:
                    current_bpm_index += 1
                    bpm = tempi[current_bpm_index]

        if not startSong or current_time >= midi_data.get_end_time():
            bpm = 0

        # Drawing things

        screen.fill(background_colour)



        gn.globalGeneration(current_time, bpm)
        gn.firstLaunch = False
        gn.fps_counter(screen, clock)
        detectTrumpetNotes(active_flute_notes)

        for n in active_flute_notes:
            # if n.end <= current_time:
            active_flute_notes.remove(n)

        for n in active_piano_notes:
            # if n.end <= current_time:
            active_piano_notes.remove(n)

        # UPDATE the WINDOWS
        pygame.display.flip()

        # Manage refresh rate
        clock.tick(fps)

    # END
    pygame.display.quit()

