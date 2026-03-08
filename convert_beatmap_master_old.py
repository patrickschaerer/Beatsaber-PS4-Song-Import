import UnityPy
import os
import json
import gzip
import struct
import argparse
from typing import Dict, List, Any, Tuple

# =============================================================================
# v2/v3 -> v4 KONVERTIERUNGS-LOGIK (ULTIMATE LINEAR & FIXED INDEXING)
# =============================================================================

def detect_version(data: Dict[str, Any]) -> str:
    version = data.get('version') or data.get('_version')
    if version: return str(version)
    if '_notes' in data or '_obstacles' in data: return '2.x.x'
    return '3.x.x'

def convert_v2_note_to_v3(v2_note: Dict) -> Dict:
    return {'b': v2_note.get('_time'), 'x': v2_note.get('_lineIndex', 0), 'y': v2_note.get('_lineLayer', 0), 'c': v2_note.get('_type', 0), 'd': v2_note.get('_cutDirection', 0), 'a': 0}

def convert_v2_obstacle_to_v3(v2_obstacle: Dict) -> Dict:
    obstacle_type = v2_obstacle.get('_type', 0)
    if obstacle_type == 0:
        y_position = 0
        height = 5
    else:
        y_position = 2
        height = 3
    return {
        'b': v2_obstacle.get('_time'),
        'x': v2_obstacle.get('_lineIndex', 0),
        'y': y_position,
        'd': v2_obstacle.get('_duration', 1),
        'w': v2_obstacle.get('_width', 1),
        'h': height
    }

def convert_v2_to_v3(v2_data: Dict[str, Any]) -> Dict[str, Any]:
    v3_data = {'version': '3.0.0', 'colorNotes': [], 'bombNotes': [], 'obstacles': [], 'sliders': [], 'burstSliders': [], 'waypoints': [], 'basicBeatmapEvents': []}
    if '_notes' in v2_data:
        for v2_note in v2_data['_notes']:
            v3_note = convert_v2_note_to_v3(v2_note)
            if v2_note.get('_type') == 3: v3_data['bombNotes'].append({'b': v3_note['b'], 'x': v3_note['x'], 'y': v3_note['y']})
            elif v2_note.get('_type') in [0, 1]: v3_data['colorNotes'].append(v3_note)
    if '_obstacles' in v2_data:
        for v2_obstacle in v2_data['_obstacles']: v3_data['obstacles'].append(convert_v2_obstacle_to_v3(v2_obstacle))
    return v3_data

def deduplicate_data(items: List[Dict], key_field: str = 'b') -> Tuple[List[Dict], List[Dict]]:
    data_list, data_to_index, events = [], {}, []
    for item in items:
        beat_value = item.get(key_field)
        data_dict = {k: v for k, v in item.items() if k != key_field and k != 'customData'}
        if 'a' in data_dict and data_dict['a'] == 0: del data_dict['a']
        data_tuple = tuple(sorted(data_dict.items()))
        if data_tuple in data_to_index: 
            data_index = data_to_index[data_tuple]
        else:
            data_index = len(data_list)
            data_list.append(data_dict)
            data_to_index[data_tuple] = data_index
        events.append({key_field: beat_value, 'i': data_index})
    return events, data_list

def convert_v3_to_v4(v3_data: Dict[str, Any]) -> Dict[str, Any]:
    v4_data = {"version": "4.0.0"}
    for v3_key, v4_key in [('colorNotes', 'colorNotes'), ('bombNotes', 'bombNotes'), ('obstacles', 'obstacles'), ('sliders', 'arcs'), ('burstSliders', 'chains'), ('waypoints', 'spawnRotations')]:
        if v3_key in v3_data and v3_data[v3_key]:
            events, data = deduplicate_data(v3_data[v3_key], 'b')
            v4_data[v4_key], v4_data[v4_key + 'Data'] = events, data
        else: 
            v4_data[v4_key], v4_data[v4_key + 'Data'] = [], []
    return v4_data

def convert_to_v4(input_data: Dict[str, Any]) -> Dict[str, Any]:
    version = detect_version(input_data)
    if version.startswith('4.'): return input_data
    elif version.startswith('2.'): return convert_v3_to_v4(convert_v2_to_v3(input_data))
    return convert_v3_to_v4(input_data)

def wrap_textasset(json_data_bytes, internal_name):
    gz_data = gzip.compress(json_data_bytes, compresslevel=9)
    name_bytes = internal_name.encode('utf-8')
    name_len = len(name_bytes)
    output = bytearray()
    output.extend(struct.pack('<I', name_len))
    output.extend(name_bytes)
    output.extend(b'\x00' * ((4 - (name_len % 4)) % 4))
    data_len = len(gz_data)
    output.extend(struct.pack('<I', data_len))
    output.extend(gz_data)
    output.extend(b'\x00' * ((4 - (data_len % 4)) % 4))
    return bytes(output)

def process_beatmap(input_dat_path, bundle_path, output_bundle_path):
    filename = os.path.basename(input_dat_path).lower()
    
    # Identify requested difficulty
    difficulty = None
    if "expertplus" in filename: difficulty = "expertplus"
    elif "expert" in filename: difficulty = "expert"
    elif "hard" in filename: difficulty = "hard"
    elif "normal" in filename: difficulty = "normal"
    elif "easy" in filename: difficulty = "easy"
    
    if not difficulty:
        print(f"      [!] Could not identify difficulty from filename: {filename}")
        return

    # Identify requested characteristic
    characteristics = ["onesaber", "noarrows", "360degree", "90degree", "lightshow", "lawless"]
    char_found = next((c for c in characteristics if c in filename), "standard")

    print(f"      [*] Target: Diff={difficulty}, Char={char_found}")

    env = UnityPy.load(bundle_path)
    modified = False
    
    for obj in env.objects:
        if obj.type.name == "TextAsset":
            raw = obj.get_raw_data()
            if len(raw) < 8: continue
            
            try:
                name_len = struct.unpack('<I', raw[:4])[0]
                internal_name = raw[4:4+name_len].decode('utf-8', 'ignore')
            except: continue
            
            if ".beatmap.gz" not in internal_name.lower(): continue
            
            name_lower = internal_name.lower()
            
            # Determine internal difficulty (EXACT matching)
            actual_diff = None
            if "expertplus" in name_lower: actual_diff = "expertplus"
            elif "expert" in name_lower: actual_diff = "expert"
            elif "hard" in name_lower: actual_diff = "hard"
            elif "normal" in name_lower: actual_diff = "normal"
            elif "easy" in name_lower: actual_diff = "easy"
            
            if actual_diff != difficulty: continue
            
            # Match characteristic
            char_match = False
            if char_found != "standard":
                if char_found in name_lower: char_match = True
            elif not any(c in name_lower for c in characteristics):
                char_match = True
            
            if char_match:
                print(f"      [+] Matching bundle object: {internal_name}")
                with open(input_dat_path, 'r', encoding='utf-8') as f:
                    input_json = json.load(f)
                
                v4_data = convert_to_v4(input_json)
                v4_json_bytes = json.dumps(v4_data, separators=(',', ':')).encode('utf-8')
                
                obj.set_raw_data(wrap_textasset(v4_json_bytes, internal_name))
                modified = True
                # Continue searching in case multiple characteristics match (though unlikely)

    if modified:
        with open(output_bundle_path, "wb") as f:
            # We use the same compression as before
            if hasattr(env, 'file') and env.file: f.write(env.file.save(packer="lz4"))
            else: f.write(env.save(packer="lz4"))
        print(f"      [OK] Updated {difficulty} in bundle.")
    else:
        print(f"      [?] No matching entry found in bundle for {difficulty} ({char_found}).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dat_file')
    parser.add_argument('bundle')
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    process_beatmap(args.dat_file, args.bundle, args.output if args.output else args.bundle + "_modified")
