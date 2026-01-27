# Beatsaber-PS4-Song-Import-
Import Custom Songs from Beatsaver to a Jailbroken PS4 by replacing an existing song

Successful:
    - Convert the audiofile from a songzipfile from Beatsaver and import it to PS4-Beatsaber 2.0

To do:
    - Convert the beatmapfile to import it to PS4-Beatsaber 2.0


Audio Conversion and Import (short version):
1. Extract the Beatsaber Update Package with Package Toolbox.
2. Download a song from Beatsaver and extract that Zipfile.
1. Use audio_converter.py to convert the song.ogg to a 44.1kHz song.wav
2. In Unity create a scene with an audio and the song.wav as a resource. Make a build to get sharedassets0.assets and sharedassets0.resource
4. Open the PS4-Beatsaber songfile (e.g. dynamite) in UABEA
5. Import the sharedassets0.resource
6. Copy the original resource filename within UABEA (usually CAB-xxxxxxx.resource) and rename that file to "old"
7. rename the importet sharedassets0.resource within UABEA to the CAB-xxxxxx.resource filename and remove the "old"
8. Save and close the songfile in UABEA
9. use metadata_patcher.py to import the length and filesize of the new song to the asset info of the PS4-Beatsaber songfile.


Beatmap conversion and Import (short version):
1. Use covert_v3_to_v4.py to convert a Beatmap-File (e.g. ExpertStandard.dat) from Beatsaver to Beatsaber 4.0.0 json and for a first PS4 specific compression
2. Use recompress_beatmap.py to add a PS4 specific Header and a gzip compression. The target filename must match the Filename of the beatmap in Asset Info of the songfile (e.g. DynamiteExpert.beatmap.gz(.dat))
3. Open the songfile (e.g. dynamite) in UABEA.
4. Highlight the beatmapfile (e.g. DynamiteExpert.beatmap.gz) and click on Import RAW to import the createt DynamiteExpert.beatmap.gz.dat.



### Detailed Audio Conversion and Import (English)

This section provides a detailed walkthrough of the "Audio Conversion and Import" process for replacing a song in the PS4 version of Beat Saber.

**Required Tools:**
*   **PS4 PKG Toolbox:** For extracting the main Beat Saber update package (`.pkg`).
    *   [PS4 PKG Toolbox on GitHub](https://github.com/emo1312/PS4-PKG-Toolbox)
*   **Unity Hub:** To install and manage Unity Editor versions. You will need a Unity Editor version that is compatible with the version of Beat Saber you are modding.
    *   [Download Unity Hub](https://unity.com/download)
*   **UABEA (Unity Assets Bundle Extractor):** The primary tool for viewing and modifying the contents of Unity asset bundles. "UABE Avalanche" is a recommended modern version.
    *   [UABE Avalanche on GitHub](https://github.com/nesrak1/UABEA)

---

**Step-by-Step Guide:**

**1. Extract the Beat Saber Game Files**
   - You need the decrypted game files from your jailbroken PS4. Start with the main game update package (`.pkg`).
   - Use the **PS4 PKG Toolbox** to extract the contents of the update package. This will give you access to the game's file structure, including the song bundles located in `CUSAXXXXX-app\Image0\Media\StreamingAssets\BeatmapLevelsData`.

**2. Download and Prepare the Custom Song**
   - Download the custom song you want to import. A great source is [Beat Saver](https://beatsaver.com/).
   - Extract the downloaded `.zip` file into a dedicated working folder. Inside, you will typically find the audio file (e.g., `song.ogg`) and the beatmap files (e.g., `ExpertStandard.dat`).

**3. Convert the Audio to WAV**
   - The PS4 version of Beat Saber requires a specific audio format. The custom song's audio (usually an `.ogg` file) must be converted.
   - Use the `audio_converter.py` script (assuming it's part of this project) to convert the file. The script's purpose is to transform the audio into a **44.1kHz WAV file**.

**4. Create a "Dummy" Unity Asset for Metadata**
   - This is a crucial step to generate correctly formatted asset files (`sharedassets0.assets` and `sharedassets0.resource`) that UABEA can use.
   - Open **Unity Hub** and create a new, simple Unity project.
   - Import the `song.wav` file you created in the previous step into the Unity project's `Assets` folder.
   - Create a simple scene and add an `AudioSource` component to an object. Assign your `song.wav` to this `AudioSource`.
   - Go to `File > Build Settings` and build the project for a standalone platform (like Windows). When the build is complete, Unity will create a `*_Data` folder. Inside this folder, you will find `sharedassets0.assets` and `sharedassets0.resource`. These two files contain your new song's audio data and metadata in a format Unity understands.

**5. Import the New Audio Resource with UABEA**
   - Open **UABEA**.
   - Go to `File > Open` and select the official Beat Saber song file you want to replace (e.g., `dynamite`, `dna`) from the game files you extracted in Step 1.
   - Click Import and select the `sharedassets0.resource` file you generated with Unity in Step 4.
     - In the main UABEA window, find the original resource file (it will have a name like `CAB-xxxxxxxx.resource`). Note down this name.
     - Manually rename the original `CAB-xxxxxxxx.resource` file to `old` (or similar) in UABEA.
     - Rename your imported `sharedassets0.resource` to the original `CAB-xxxxxxxx.resource` name.

**6. Save the Modified Song Bundle**
   - After swapping the resource file, go to `File > Save` in UABEA.
  
**7. Patch the Audio Metadata**
   - At this point, the audio *stream* is replaced, but the game still has the *metadata* (like the song's length) of the original song. This mismatch will cause the song to end abruptly or crash the game.
   - The `metadata_patcher.py` script fixes this by copying the correct metadata from your "dummy" asset file to your newly modified song bundle.

   **7.1. Prerequisites for the script**
   - **Python 3.x:** The script is executed with Python. If you don't have it, you can download it from the [official Python website](https://www.python.org/downloads/).
   - **UnityPy:** This Python library is required to edit Unity asset files. You can install it by running the following command in your command line (PowerShell, CMD):
     ```bash
     pip install UnityPy
     ```

   **7.2. Directory Preparation**
   - The script requires a specific folder setup. Create a folder and place the following two files inside:
     1.  `sharedassets0.assets`: This is the file you generated with Unity in Step 4. It acts as the **source** of the correct metadata.
     2.  The modified song bundle: This is the file you saved from UABEA in Step 6 (e.g., `dynamite`). It is the **target** that will be patched.

     Your folder should look like this:
     ```
     patch-folder/
     │
     ├── sharedassets0.assets   <-- The source metadata file from your Unity build.
     │
     └── dynamite               <-- The target song bundle saved from UABEA.
     ```

   **7.3. Executing the Script**
   - Open a command line (like PowerShell).
   - Run the script using the following command structure, replacing the placeholders with your actual file paths and names.

     ```powershell
     python C:\Users\Dev-Box-User\BeatsaberConversion\metadata_patcher.py --song-dir "C:\Path\To\Your\patch-folder" --source-name "SOURCE_AUDIO_NAME" --target-name "TARGET_AUDIO_NAME"
     ```

   - **Explanation of Placeholders:**
     - `"C:\Path\To\Your\patch-folder"`: The full path to the folder you prepared in step 7.2.
     - `"SOURCE_AUDIO_NAME"`: The name of the AudioClip asset inside `sharedassets0.assets`. This is often just `"Song"` if you used a simple `.wav` file name in Unity.
     - `"TARGET_AUDIO_NAME"`: The name of the AudioClip asset inside the official song bundle you are modifying (e.g., `"Dynamite"`, `"CrabRave"`). You can find this name in UABEA.

After completing these steps, the song bundle should now contain your custom audio with the correct metadata, ready to be used on the PS4.