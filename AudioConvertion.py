from pydub import AudioSegment

def mp3_to_wav(src, dst):
    AudioSegment.converter = 'ffmpeg.exe'
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")

mp3_to_wav("media/mp3/PinkPanther_Piano_Only.mp3", "media/wav/test.wav")