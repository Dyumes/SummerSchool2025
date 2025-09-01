# SummerSchool2025

## Overview  
This project implements a **virtual orchestra synchronizable to any music**, transforming an audio input into a **music-synchronized animated video**.  
The visualization is **procedurally generated** using only geometric primitives (triangles) and reacts to the music being played.

---

## Features  
- **Input:**  
  - Accepts a `.mp3` file as input.  
  - Supports **maximum 2 instruments** (currently: **piano** & **trumpet**).  
  - Implemented using **Python** and standard libraries.

- **Output:**   
  - Live **music-synchronized animation**.  
  - Visualization designed with **Pygame**.  

- **Animation Characteristics:**  
  - Only **triangles** used as graphical primitives.  
  - Fully **procedural content** (no external images, textures, or video files).  
  - **Animated**: shapes move over time and react to specific notes.  
  - **Synchronized with music**: effects occur in sync with the score.  

---

## Technical Details

### System Architecture
- **Audio Processing**: 
  - FFT (Fast Fourier Transform) analysis for frequency detection
  - Instrument differentiation between piano and trumpet
  - MIDI conversion capabilities for precise note timing

- **Visual Generation**:
  - Procedural mountain generation that reacts to trumpet notes
  - Procedural ground generation that reacts to piano notes
  - Dynamic sun that reacts to the music's tempo
  - Physics-based particle behavior with gravitational forces

- **Synchronization**:
  - Real-time music-to-visual mapping
  - Tempo-aware animation adjustments
  - Note velocity affecting visual intensity

### Core Components
- **`FFT.py`**: Analyzes audio files using Fast Fourier Transform to extract frequency data
- **`Particles.py`**: Physics engine for particle generation and movement
- **`Mountain_Generation.py`** & **`Sun_Generation.py`**: Procedural visual elements that react to music
- **`main.py`**: Central orchestration of all components and pygame visualization

---

## Installation

### Prerequisites
- Python 3.8+
- Pygame
- NumPy
- SciPy
- pretty_midi
- PyAudio
- Matplotlib
- FFmpeg (for audio conversion)

### FFmpeg Installation

This project requires the **FFmpeg** tool for audio conversion.  
Make sure FFmpeg is installed on your system and its executable is accessible in the `PATH` environment variable.

#### Installation on Windows

1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) or [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/).
2. Extract the downloaded archive.
3. Add the folder containing `ffmpeg.exe` to the `PATH` environment variable:
   - Open **Advanced System Settings**.
   - Click on **Environment Variables**.
   - Edit the `PATH` variable and add the path to the FFmpeg `bin` folder.
4. Restart your terminal or IDE.

To verify the installation, run the following command in a terminal:

```bash
  ffmpeg -version
```

#### Installation on MacOS
1. Open the terminal.
2. Install Homebrew if it is not already installed by following the instructions at [https://brew.sh/](https://brew.sh/).
3. Install FFmpeg by running the following command:
```bash
  brew install ffmpeg
```
4. To verify the installation, run the following command in the terminal:
```bash
  ffmpeg -version
```

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/SummerSchool2025.git
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Prepare your audio files:
   - Place your `.mp3` files in the `media/mp3/` directory
   - Ensure they contain primarily piano and trumpet instruments for optimal results

---

## Usage

### Basic Operation
1. Run the main application:
   ```
   python src/main.py
   ```

2. The system will:
   - Process the audio file specified in the code
   - Generate visualizations synchronized to the music
   - Display the result in a Pygame window
   - Save the output as an MP4 video file

### Customization
- Edit `main.py` to change input files and visual parameters
- Adjust threshold values in `FFT.py` for different audio sensitivity
- Modify particle behavior in `Particles.py` for different visual effects

---

## MIDI Comparison Tools

The project includes MIDI comparison functionality through `MidiComparison.py`:

- Analyzes similarities between MIDI files using Longest Common Subsequence (LCS) algorithm
- Provides visual representation of note progressions and common patterns
- Useful for comparing generated MIDI outputs with original compositions

---

## Examples

The repository includes sample media files for testing:
- `Ecossaise_Beethoven.midi` and `PinkPanther.midi` for MIDI reference
- Pre-processed audio files in `.mp3` and `.wav` formats
- Examples of the visual output in the video files

---

## License

This project is licensed under the **MIT License** - see below for details:

```
MIT License

Copyright (c) 2025 SummerSchool2025 Project Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

*Note: This is an educational project developed as part of a school assignment. The code is primarily for educational purposes.*

---

## Acknowledgments

- **Supervisor:**
  - Dr. Louis Lettry 

- **Contributors:**
  - Veuillet Gaëtan
  - Favre Fabien
  - Weber Benno
  - Schanen Louis


*This project was developed as part of the Summer School 1 at HEI - Sion, Summer 2025.*
