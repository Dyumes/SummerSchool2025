import subprocess
import os

def mp3_to_wav(src, dst):
    """
        Converts an MP3 file to WAV format using ffmpeg.

        Args:
            src (str): Path to the source MP3 file.
            dst (str): Path where the output WAV file will be saved.
        """
    try:
        subprocess.call(["ffmpeg", "-i", src, dst], stdout=subprocess.DEVNULL,
                                                         stderr=subprocess.STDOUT)
    except Exception as e:
        print(f"The error \"{e}\" occurred during the conversion process.")
        print("Please ensure that you have ffmpeg installed and the path is correctly set.")

#mp3_to_wav(os.path.join("media", "mp3", "Gamme.mp3"), os.path.join("media", "wav", "Gamme.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "Gamme_Piano.mp3"), os.path.join("media", "wav", "Gamme_Piano.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "Gamme_Trumpet.mp3"), os.path.join("media", "wav", "Gamme_Trumpet.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "SSB.mp3"), os.path.join("media", "wav", "SSB.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "SSB_Piano.mp3"), os.path.join("media", "wav", "SSB_Piano.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "SSB_Trumpet.mp3"), os.path.join("media", "wav", "SSB_Trumpet.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "SuperMario.mp3"), os.path.join("media", "wav", "SuperMario.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "SuperMarion_Piano.mp3"), os.path.join("media", "wav", "SuperMarion_Piano.wav"))
#mp3_to_wav(os.path.join("media", "mp3", "SuperMarion_Trumpet.mp3"), os.path.join("media", "wav", "SuperMarion_Trumpet.wav"))
