from pydub import AudioSegment
import subprocess

def mp3_to_wav(src, dst):
    try:
        #AudioSegment.converter = 'ffmpeg.exe'
        #print("Voluntary error: This is a voluntary error to test the error handling in mp3_to_wav().")
        #raise "This is a voluntary error to test the error handling in mp3_to_wav()."
        #sound = AudioSegment.from_mp3(src)
        #sound.export(dst, format="wav")
        subprocess.call(["ffmpeg", "-i", src, dst], stdout=subprocess.DEVNULL,
                                                         stderr=subprocess.STDOUT)
    except:
        print("An error occurred during the conversion process.")
        print("Please ensure that you have ffmpeg installed and the path is correctly set.")

mp3_to_wav("media/mp3/PinkPanther_Piano_Only.mp3", "media/wav/test.wav")