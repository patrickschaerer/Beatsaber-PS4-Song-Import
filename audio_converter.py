import os
import subprocess
import argparse
import shutil

def get_atempo_filter(factor):
    """
    Erzeugt den atempo-Filterstring für ffmpeg.
    Da atempo nur Werte zwischen 0.5 und 2.0 erlaubt, müssen Werte außerhalb
    dieses Bereichs durch Verkettung gelöst werden.
    """
    filters = []
    while factor > 2.0:
        filters.append("atempo=2.0")
        factor /= 2.0
    while factor < 0.5:
        filters.append("atempo=0.5")
        factor /= 0.5
    filters.append(f"atempo={factor}")
    return ",".join(filters)

def convert_audio(input_file_path: str, source_bpm: float = None, target_bpm: float = None):
    """
    Converts the given audio file to a 44100 Hz WAV file in the same directory,
    optionally changing the tempo based on BPM.
    """
    # 1. Validate ffmpeg exists
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH.")

    # 2. Validate input file exists
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Input file not found: {input_file_path}")

    song_dir = os.path.dirname(input_file_path)
    file_name_without_ext = os.path.splitext(os.path.basename(input_file_path))[0]
    output_wav_path = os.path.join(song_dir, f"{file_name_without_ext}_44100Hz.wav")

    print(f"Input audio file: {input_file_path}")
    print(f"Outputting to: {output_wav_path}")

    command = [
        "ffmpeg",
        "-i", input_file_path,
        "-ar", "44100"
    ]

    # Tempo-Anpassung hinzufügen, falls BPM-Werte gegeben sind
    if source_bpm and target_bpm:
        tempo_factor = target_bpm / source_bpm
        if abs(tempo_factor - 1.0) > 0.0001:
            atempo_val = get_atempo_filter(tempo_factor)
            print(f"Tempo adjustment: {source_bpm} -> {target_bpm} (Factor: {tempo_factor:.4f})")
            command += ["-af", atempo_val]

    command.append(output_wav_path)
    # Überschreiben ohne Nachfrage erzwingen
    command.insert(1, "-y")

    try:
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("Audio conversion and tempo adjustment successful!")
            return output_wav_path
        else:
            if result.stderr:
                print("FFmpeg Stderr:\n", result.stderr)
            raise RuntimeError(f"FFmpeg conversion failed with exit code {result.returncode}.")
            
    except Exception as e:
        print(f"An error occurred during ffmpeg execution: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a given audio file to a 44100 Hz WAV file with optional tempo adjustment."
    )
    parser.add_argument("input_file", help="Full path to the input audio file.")
    parser.add_argument("-bpm", type=float, help="Original BPM of the song.")
    parser.add_argument("-tar", type=float, help="Target BPM of the song.")
    
    args = parser.parse_args()

    try:
        convert_audio(args.input_file, args.bpm, args.tar)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
