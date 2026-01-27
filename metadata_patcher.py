import UnityPy
import argparse
import os

def find_asset(env, asset_type, asset_name):
    """Finds a specific asset in a UnityPy environment by type and name."""
    for obj in env.objects:
        if obj.type.name == asset_type:
            tree = obj.read_typetree()
            if tree.get('m_Name') == asset_name:
                return obj
    return None

def patch_audio_metadata(song_dir: str, source_name: str, target_name: str):
    """
    Patches AudioClip metadata (m_Length, m_Size) from a source to a target asset bundle.
    """
    try:
        # 1. Validate paths and find target bundle
        if not os.path.isdir(song_dir):
            raise FileNotFoundError(f"Song directory not found: {song_dir}")

        source_assets_path = os.path.join(song_dir, "sharedassets0.assets")
        if not os.path.exists(source_assets_path):
            raise FileNotFoundError(f"Source assets file 'sharedassets0.assets' not found in: {song_dir}")

        # Find the target bundle file (the one without an extension)
        target_bundle_filename = None
        for item in os.listdir(song_dir):
            item_path = os.path.join(song_dir, item)
            if os.path.isfile(item_path) and '.' not in item:
                if target_bundle_filename is not None:
                     raise ValueError(f"Multiple files without extension found in song directory: {song_dir}. Please ensure only one exists.")
                target_bundle_filename = item
        
        if not target_bundle_filename:
            raise FileNotFoundError(f"No file without an extension (target bundle) found in song directory: {song_dir}.")

        target_bundle_path = os.path.join(song_dir, target_bundle_filename)
        print(f"Determined target bundle file: '{target_bundle_path}'")

        # 2. Load source environment and extract metadata
        print(f"\nLoading source assets: {source_assets_path}")
        source_env = UnityPy.load(source_assets_path)

        source_obj = find_asset(source_env, "AudioClip", source_name)
        if not source_obj:
            raise ValueError(f"Source AudioClip '{source_name}' not found.")
        
        source_tree = source_obj.read_typetree()
        print(f"Found source audio '{source_name}'. Reading metadata...")

        new_length = source_tree.get('m_Length')
        if new_length is None:
            raise KeyError(f"'m_Length' not found in source asset '{source_name}'.")

        resource_node = source_tree.get('m_Resource')
        if not resource_node:
            raise KeyError(f"'m_Resource' node not found in source asset '{source_name}'.")
        
        new_size = resource_node.get('m_Size')
        if new_size is None:
            raise KeyError(f"'m_Size' not found in source asset's m_Resource node.")

        print(f"  - Extracted m_Length: {new_length}")
        print(f"  - Extracted m_Size: {new_size}")

        # 3. Load Target, Patch Metadata, and Save
        print(f"\nLoading target bundle for patching: {target_bundle_path}")
        target_env = UnityPy.load(target_bundle_path)
        
        target_audio_obj = find_asset(target_env, "AudioClip", target_name)
        if not target_audio_obj:
            raise ValueError(f"Target AudioClip '{target_name}' not found.")

        print(f"Found target audio '{target_name}'. Overwriting its metadata...")
        target_audio_tree = target_audio_obj.read_typetree()
        
        # Patch metadata (m_Length and m_Size)
        target_audio_tree['m_Length'] = new_length
        target_audio_tree['m_Size'] = new_size
        
        if 'm_Resource' in target_audio_tree and target_audio_tree['m_Resource']:
            target_audio_tree['m_Resource']['m_Size'] = new_size

        target_audio_obj.save_typetree(target_audio_tree)
        
        print("Successfully patched audio metadata.")

        # 4. Save Final Bundle
        output_path = target_bundle_path
        print(f"\nSaving all changes back to {output_path}...")
        with open(output_path, "wb") as f:
            f.write(target_env.file.save())

        print(f"\nProcess complete! '{os.path.basename(output_path)}' has been overwritten.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Patches AudioClip metadata (m_Length, m_Size) from a source to a target bundle.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--song-dir", 
        required=True, 
        help="Directory containing:\n" 
             "1. The source 'sharedassets0.assets'.\n" 
             "2. The target bundle (file without extension)."
    )
    parser.add_argument(
        "--source-name", 
        required=True, 
        help="Name of the source AudioClip asset in 'sharedassets0.assets'."
    )
    parser.add_argument(
        "--target-name", 
        required=True, 
        help="Name of the target AudioClip asset in the target bundle."
    )

    args = parser.parse_args()

    patch_audio_metadata(
        args.song_dir,
        args.source_name, 
        args.target_name
    )
