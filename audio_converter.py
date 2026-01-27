import os
import glob
import subprocess # For executing PowerShell script
import argparse

def convert_audio_to_wav_44100hz(song_dir: str, ffmpeg_path: str):
    """
    Converts an audio file (e.g., .egg) in the given directory to a 44100 Hz WAV file.
    """
    if not os.path.exists(song_dir):
        raise FileNotFoundError(f"Song directory not found: {song_dir}")
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg executable not found at: {ffmpeg_path}")

    print(f"Searching for audio file in: {song_dir}")

    audio_file_path = None
    # Prioritize common audio formats, e.g., song.egg
    for ext in ["*.egg", "*.ogg", "*.mp3", "*.wav"]:
        matches = glob.glob(os.path.join(song_dir, ext))
        if matches:
            # Pick the first one found
            audio_file_path = matches[0]
            break
    
    if not audio_file_path:
        raise FileNotFoundError(f"No audio file (egg, ogg, mp3, wav) found in: {song_dir}")

    output_wav_path = os.path.join(song_dir, os.path.splitext(os.path.basename(audio_file_path))[0] + "_44100Hz.wav")

    print(f"Found audio file: {audio_file_path}")
    print(f"Converting to: {output_wav_path}")

    # Create a temporary PowerShell script to execute ffmpeg
    # Use the '&' operator to ensure the command is executed even with spaces in paths
    ps_script_content = f"""
& "{ffmpeg_path}" -i "{audio_file_path}" -ar 44100 "{output_wav_path}"
"""
    temp_ps_script_path = os.path.join(song_dir, "temp_ffmpeg_convert.ps1")
    
    try:
        with open(temp_ps_script_path, "w", encoding="utf-8") as f:
            f.write(ps_script_content)
        
        print(f"Executing ffmpeg via temporary PowerShell script: {temp_ps_script_path}")
        # Use subprocess to run powershell.exe -File
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-File", temp_ps_script_path],
            capture_output=True,
            text=True,
            check=False # Do not raise exception for non-zero exit codes immediately
        )
        
        # Print stdout and stderr from the PowerShell process
        print("FFmpeg Stdout:\n", result.stdout)
        if result.stderr:
            print("FFmpeg Stderr:\n", result.stderr)
        
        if result.returncode == 0:
            print("Audio conversion successful!")
        else:
            raise RuntimeError(f"FFmpeg conversion failed with exit code {result.returncode}.")
            
    except Exception as e:
        print(f"An error occurred during ffmpeg execution: {e}")
        raise
    finally:
        # Clean up the temporary PowerShell script
        if os.path.exists(temp_ps_script_path):
            os.remove(temp_ps_script_path)
            print(f"Cleaned up temporary script: {temp_ps_script_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts an audio file in a specified directory to a 44100 Hz WAV file."
    )
    parser.add_argument("--song-dir", required=True, help="Directory containing the audio file.")
    parser.add_argument("--ffmpeg-path", required=True, help="Full path to the ffmpeg.exe executable.")
    
    args = parser.parse_args()

    convert_audio_to_wav_44100hz(args.song_dir, args.ffmpeg_path)
