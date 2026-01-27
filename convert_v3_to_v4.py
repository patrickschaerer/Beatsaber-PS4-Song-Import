#!/usr/bin/env python3
"""
Beat Saber Beatmap Converter: v3.x → v4.0.0

Konvertiert Beat Saber Beatmaps vom v3.x Format (BeatSaver) 
zum v4.0.0 kompakten Format (Unity Asset Bundle).

Hauptunterschiede:
- v3.x: Jedes Objekt enthält alle Felder (expanded)
- v4.0: Zwei Arrays - eines für Timing, eines für Daten (compact)
"""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Any, Tuple


def deduplicate_data(items: List[Dict], key_field: str = 'b') -> Tuple[List[Dict], List[Dict]]:
    """
    Teilt eine Liste von Objekten in zwei Arrays auf:
    1. Events Array (nur key_field + optionaler Index)
    2. Data Array (alle anderen Felder)
    
    Eliminiert Duplikate in den Daten durch Wiederverwendung von Indizes.
    """
    # Sammle alle einzigartigen Daten-Kombinationen
    data_list = []
    data_to_index = {}
    events = []
    
    for item in items:
        # Extrahiere den Timing-Wert
        beat_value = item.get(key_field)
        
        # Erstelle Daten-Dict (alles außer dem key_field)
        data_dict = {k: v for k, v in item.items() if k != key_field}
        
        # Konvertiere zu hashbarem Format für Deduplication
        data_tuple = tuple(sorted(data_dict.items()))
        
        # Prüfe ob diese Daten-Kombination bereits existiert
        if data_tuple in data_to_index:
            # Verwende existierenden Index
            data_index = data_to_index[data_tuple]
        else:
            # Erstelle neuen Daten-Eintrag
            data_index = len(data_list)
            data_list.append(data_dict)
            data_to_index[data_tuple] = data_index
        
        # Erstelle Event-Eintrag
        if data_index == len(events):
            # Wenn Index == Position, kann 'i' weggelassen werden
            event = {key_field: beat_value}
        else:
            # Ansonsten expliziten Index angeben
            event = {key_field: beat_value, 'i': data_index}
        
        events.append(event)
    
    return events, data_list


def convert_v3_to_v4(v3_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert eine Beat Saber v3.x Beatmap zu v4.0.0 Format.
    """
    v4_data = {
        "version": "4.0.0"
    }
    
    # Konvertiere colorNotes
    if 'colorNotes' in v3_data and v3_data['colorNotes']:
        # Entferne 'a' (angle) Feld aus v3.x, da es in v4 nicht existiert
        cleaned_notes = []
        for note in v3_data['colorNotes']:
            cleaned = {k: v for k, v in note.items() if k != 'a'}
            cleaned_notes.append(cleaned)
        
        events, data = deduplicate_data(cleaned_notes, 'b')
        v4_data['colorNotes'] = events
        v4_data['colorNotesData'] = data
    else:
        v4_data['colorNotes'] = []
        v4_data['colorNotesData'] = []
    
    # Konvertiere bombNotes
    if 'bombNotes' in v3_data and v3_data['bombNotes']:
        events, data = deduplicate_data(v3_data['bombNotes'], 'b')
        v4_data['bombNotes'] = events
        v4_data['bombNotesData'] = data
    else:
        v4_data['bombNotes'] = []
        v4_data['bombNotesData'] = []
    
    # Konvertiere obstacles
    if 'obstacles' in v3_data and v3_data['obstacles']:
        events, data = deduplicate_data(v3_data['obstacles'], 'b')
        v4_data['obstacles'] = events
        v4_data['obstaclesData'] = data
    else:
        v4_data['obstacles'] = []
        v4_data['obstaclesData'] = []
    
    # Konvertiere sliders → arcs (v3 "sliders" werden zu v4 "arcs")
    if 'sliders' in v3_data and v3_data['sliders']:
        events, data = deduplicate_data(v3_data['sliders'], 'b')
        v4_data['arcs'] = events
        v4_data['arcsData'] = data
    else:
        v4_data['arcs'] = []
        v4_data['arcsData'] = []
    
    # Konvertiere burstSliders → chains
    if 'burstSliders' in v3_data and v3_data['burstSliders']:
        events, data = deduplicate_data(v3_data['burstSliders'], 'b')
        v4_data['chains'] = events
        v4_data['chainsData'] = data
    # Füge leere Arrays hinzu, wenn nicht vorhanden
    if 'chains' not in v4_data:
        v4_data['chains'] = []
        v4_data['chainsData'] = []
    
    # Konvertiere waypoints → spawnRotations (optional)
    if 'waypoints' in v3_data and v3_data['waypoints']:
        events, data = deduplicate_data(v3_data['waypoints'], 'b')
        v4_data['spawnRotations'] = events
        v4_data['spawnRotationsData'] = data
    # Füge leere Arrays hinzu, wenn nicht vorhanden
    if 'spawnRotations' not in v4_data:
        v4_data['spawnRotations'] = []
        v4_data['spawnRotationsData'] = []
    
    return v4_data


def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_v3_to_v4.py <input.dat> <output.json>")
        print("\nKonvertiert Beat Saber v3.x Beatmaps zu v4.0.0 Format")
        print("Input:  .dat Datei von BeatSaver (v3.x)")
        print("Output: .json Datei im v4.0.0 Format (bereit für Komprimierung)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Lade v3 Daten
    print(f"Lade {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        v3_data = json.load(f)
    
    version = v3_data.get('version', 'unknown')
    print(f"Input Version: {version}")
    
    if not version.startswith('3.'):
        print(f"WARNUNG: Erwartete v3.x Format, gefunden: {version}")
        response = input("Trotzdem fortfahren? (j/n): ")
        if response.lower() != 'j':
            sys.exit(0)
    
    # Konvertiere zu v4
    print("Konvertiere zu v4.0.0...")
    v4_data = convert_v3_to_v4(v3_data)
    
    # Statistiken
    print("\n=== Konvertierungs-Statistiken ===")
    print(f"colorNotes:     {len(v4_data.get('colorNotes', []))} events, "
          f"{len(v4_data.get('colorNotesData', []))} unique data")
    print(f"bombNotes:      {len(v4_data.get('bombNotes', []))} events, "
          f"{len(v4_data.get('bombNotesData', []))} unique data")
    print(f"obstacles:      {len(v4_data.get('obstacles', []))} events, "
          f"{len(v4_data.get('obstaclesData', []))} unique data")
    print(f"arcs:           {len(v4_data.get('arcs', []))} events, "
          f"{len(v4_data.get('arcsData', []))} unique data")
    print(f"chains:         {len(v4_data.get('chains', []))} events, "
          f"{len(v4_data.get('chainsData', []))} unique data")
    print(f"spawnRotations: {len(v4_data.get('spawnRotations', []))} events, "
          f"{len(v4_data.get('spawnRotationsData', []))} unique data")
    
    # Speichere v4 Daten
    print(f"\nSpeichere {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        # Verwende compact JSON (keine Leerzeichen)
        json.dump(v4_data, f, separators=(',', ':'), ensure_ascii=False)
    
    # Zeige Größenvergleich
    import os
    input_size = os.path.getsize(input_file)
    output_size = os.path.getsize(output_file)
    reduction = (1 - output_size / input_size) * 100
    
    print(f"\n=== Größenvergleich ===")
    print(f"v3.x Input:  {input_size:,} Bytes")
    print(f"v4.0 Output: {output_size:,} Bytes")
    print(f"Reduktion:   {reduction:.1f}%")
    
    print(f"\n✓ Konvertierung erfolgreich!")
    print(f"Nächster Schritt: Verwende recompress.py um die .gz Datei zu erstellen")


if __name__ == "__main__":
    main()
