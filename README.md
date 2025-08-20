# SummerSchool2025

## Overview  
This project implements a **virtual orchestra synchronizable to any music**, transforming a `.mp3` audio input into a **music-synchronized animated video** (`.mp4`).  
The visualization is **procedurally generated** using only geometric primitives (triangles) and reacts to the music being played.

---

## Features  
- 🎼 **Input:**  
  - Accepts a `.mp3` file as input.  
  - Supports **maximum 2 instruments** (currently: **piano** & **trumpet**).  
  - Implemented using **Python** and standard libraries.

- 🎥 **Output:**  
  - Generates a `.mp4` video file.  
  - Contains **music-synchronized animation**.  
  - Visualization designed with **Pygame**.  

- ✨ **Animation Characteristics:**  
  - Only **triangles** used as graphical primitives.  
  - Fully **procedural content** (no external images, textures, or video files).  
  - **Animated**: shapes move over time and react to specific notes.  
  - **Synchronized with music**: effects occur in sync with the score.  

---

## FFmpeg Installation

This project requires the **FFmpeg** tool for audio conversion.  
Make sure FFmpeg is installed on your system and its executable is accessible in the `PATH` environment variable.

### Installation on Windows

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

### Installation on MacOS
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
