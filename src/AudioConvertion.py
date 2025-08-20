import subprocess

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

mp3_to_wav("media/mp3/Ecossaise_Trumpet.mp3", "media/wav/Ecossaise_Trumpet.wav")