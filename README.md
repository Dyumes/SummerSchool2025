# SummerSchool2025

## Installation de FFmpeg

Ce projet nécessite l’outil **FFmpeg** pour la conversion audio.  
Assurez-vous que FFmpeg est installé sur votre système et que son exécutable est accessible dans la variable d’environnement `PATH`.

### Installation sous Windows

1. Téléchargez FFmpeg depuis [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) ou [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/).
2. Décompressez l’archive téléchargée.
3. Ajoutez le dossier contenant `ffmpeg.exe` à la variable d’environnement `PATH` :
   - Ouvrez les **Paramètres système avancés**.
   - Cliquez sur **Variables d’environnement**.
   - Modifiez la variable `PATH` et ajoutez le chemin vers le dossier `bin` de FFmpeg.
4. Redémarrez votre terminal ou IDE.

Pour vérifier l’installation, lancez la commande suivante dans un terminal :

```bash
   ffmpeg -version
``` 
### Installation sous MacOS
1. Ouvrez le terminal.
2. Installez Homebrew si ce n’est pas déjà fait en suivant les instructions sur [https://brew.sh/](https://brew.sh/).
3. Installez FFmpeg en exécutant la commande suivante :
```bash
   brew install ffmpeg
```
4. Pour vérifier l’installation, lancez la commande suivante dans le terminal :
```bash
   ffmpeg -version
```
