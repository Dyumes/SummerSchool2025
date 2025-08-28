import pygame
import ReadMidiFile as rmf
import os
import pretty_midi
import Generation as gn
import Mountain_Generation as gn2
import Sun_Generation as sg2
import Point2D
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
bpm = 0
current_bpm_index = 0

startSong = False

fps = 60

# SETTINGS
(width, height) = (GetSystemMetrics(0) - 100, GetSystemMetrics(1) - 100)
background_colour = (15, 0, 35)
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
        mountains[n.pitch].animation_time = n.duration
        mountains[n.pitch].start_time = current_time
        mountains[n.pitch].animation_max_height = n.velocity * 10
        mountains[n.pitch].can_move = True


def detectPianoNotes(notes):
    for n in notes:
        print(n.pitch)
        print(n.duration)
        print(n.velocity * 2)
        gn.changeCubeAnimiationTime(n.duration,n.pitch)
        gn.changeCubeStartTime(current_time, n.pitch)
        # gn.changeMountainGrowthSpeed(200/n.duration, n.pitch)
        gn.changeCubeMaxHeight(n.velocity * 2,n.pitch)
        gn.playPiano(n.pitch)

if __name__ == "__main__":

    mountains = []
    static_mountains = []
    sun = sg2.SunV2(Point2D.Point2D(screen.get_width()/2, screen.get_height()/ 2 - GetSystemMetrics(1)/4))
    sun.generate()

    for i in range(12):
        temp = gn2.MountainV2()
        temp.width = screen.get_width() / 12
        temp.pos_x = temp.width * i
        temp.floor_position = height/2 + 50
        temp.generate()
        mountains.append(temp)

    for i in range(13):
        factor = 50
        temp = gn2.MountainV2()
        temp.width = screen.get_width() / 12 + factor
        temp.max_height = 500
        temp.pos_x = (temp.width - factor) * (i-1) + mountains[0].width/2
        temp.floor_position = height/2 + 50
        temp.generate()
        static_mountains.append(temp)

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

                    case pygame.K_ESCAPE:
                        running = False

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

        detectTrumpetNotes(active_flute_notes)
        detectPianoNotes(active_piano_notes)

        sun.manage_sun(screen, bpm)

        for e in mountains:
            e.manage_mountain(screen, current_time)

        for e in static_mountains:
            e.manage_mountain(screen, current_time)

        gn.globalGeneration(current_time, bpm)
        gn.firstLaunch = False
        gn.fps_counter(screen, clock)
        # detectTrumpetNotes(active_flute_notes)

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

