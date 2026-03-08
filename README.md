# Beatsaber-PS4-Song-Import
Import Custom Songs from Beatsaver to a Jailbroken PS4 by replacing an existing song

The original Song and the Song from Beatsaver need to habe similar BPM. Small adjustments are possible with the audio_converter.

**Watch the Video of the process here:** https://youtu.be/YZVxmnnO6g4

**Required Tools:**
*   **PS4 PKG Toolbox:** For extracting the main Beat Saber update package (`.pkg`).
    *   [PS4 PKG Toolbox on GitHub](https://github.com/emo1312/PS4-PKG-Toolbox)
*   **Unity Hub:** To install and manage Unity Editor versions. You will need a Unity Editor version that is compatible with the version of Beat Saber you are modding.
    *   [Download Unity Hub](https://unity.com/download)
*   **UABEA (Unity Assets Bundle Extractor):** The primary tool for viewing and modifying the contents of Unity asset bundles. "UABE Avalanche" is a recommended modern version.
    *   [UABE Avalanche on GitHub](https://github.com/nesrak1/UABEA)
*   **FFmpeg:** For converting the egg-Audio and adjusting small BPM changes.
    *    https://ffmpeg.org/download.html (https://ffmpeg.org/download.html)
*   **PS4-Fake-PKG-Tools-3.87:** To provide the Update PKG-File.
    *   (https://github.com/CyB1K/PS4-Fake-PKG-Tools-3.87)


   - The script requires a specific folder setup. Create a folder and place the following two files inside:
     1.  `sharedassets0.assets`: This is the file you generated with Unity in Step 5. It acts as the **source** of the correct metadata.
     2.  The modified song bundle: This is the file you saved from UABEA in Step 6 (e.g., `dynamite`). It is the **target** that will be patched.
     3.  UABEA needs to be installed in Tools/UABEA

     Your folder should look like this:
     ```
     Tools/
     │
     └── UABEA/
     patch-folder/
     │
     ├── sharedassets0.assets   <-- The source metadata file from your Unity build.
     │
     └── dynamite               <-- The target song bundle saved from UABEA.


### Conversion and Import (short version):
1. Extract the Beatsaber Update Package with Package Toolbox.
2. Download a song from Beatsaver and extract that Zipfile.
3. Copy the BEATSABER-SONG to your patch-folder.
4. Use audio_converter.py to convert the song.ogg to a 44.1kHz song.wav (use parameter -bpm [Beatsaver-Song-BPM] -tar [Beatsaber-Song-BPM])
5. In Unity create a scene with an audio and the song.wav as a resource. Make a build to get sharedassets0.assets and sharedassets0.resource
6. Open Powershell and use convert_beat_saber_songs.ps1
7. Copy the BEATSABER-SONG_FINAL.bundle to the BeatmapLevelsData and rename it.
8. After processing all new songs make a new PKG file with PS4-Fake-PKG-Tools


