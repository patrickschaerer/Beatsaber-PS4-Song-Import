#!/usr/bin/env python3
"""
Beat Saber Beatmap Recompressor - VERBESSERT mit 4-Byte-Alignment

Komprimiert v4.0.0 Beatmap JSON-Dateien mit proprietärem Header.

KRITISCHE ERKENNTNIS:
Der GZIP-Stream MUSS auf einer 4-Byte-Grenze beginnen!

Header-Struktur:
1. 4 Bytes: Dateiname-Länge (uint32 LE)
2. N Bytes: Dateiname (ASCII)
3. 1 Byte: Null-Terminator (0x00)
4. P Bytes: Padding (Null-Bytes, um 4-Byte-Alignment zu erreichen)
5. 6 Bytes: Metadaten (0x0000, metadata_value, 0x0000)
6. Rest: GZIP-Stream (beginnt IMMER auf Offset % 4 == 0!)
"""

import gzip
import sys
import struct
import json
import os


def calculate_metadata_value(compressed_gzip_data: bytes) -> int:
    """
    Berechnet den Metadaten-Wert für den Header.
    
    WICHTIG: Nach Analyse von 11 Original-Dateien:
    Der Metadaten-Wert ist die Größe der komprimierten GZIP-Daten minus 1.
    
    Formel: metadata_value = len(compressed_gzip_data) - 1
    
    Die Original-Dateien zeigen: metadata = gzip_size - (0 bis 3)
    Wir verwenden -1 als besten Kompromiss für alle Fälle.
    """
    return len(compressed_gzip_data) - 1


def calculate_padding(filename_length: int) -> int:
    """
    Berechnet die Anzahl der Padding-Bytes, die benötigt werden,
    damit der GZIP-Stream auf einer 4-Byte-Grenze beginnt.
    
    Header ohne Padding:
    - 4 Bytes: Dateiname-Länge
    - N Bytes: Dateiname
    - 1 Byte: Null-Terminator
    - 6 Bytes: Metadaten
    = 4 + N + 1 + 6 = N + 11
    
    GZIP soll bei (N + 11 + padding) beginnen
    Bedingung: (N + 11 + padding) % 4 == 0
    
    padding = (4 - ((N + 11) % 4)) % 4
    """
    base_size = 4 + filename_length + 1 + 6  # length + name + null + metadata
    padding = (4 - (base_size % 4)) % 4
    return padding


def recompress_file(input_filepath: str, output_filepath: str, 
                   original_filename_in_header: str = None,
                   metadata_value: int = None):
    """
    Komprimiert eine v4.0.0 Beatmap JSON-Datei zu .gz Format mit Header.
    
    Args:
        input_filepath: Pfad zur dekomprimierten JSON-Datei
        output_filepath: Pfad für die komprimierte Ausgabe-Datei
        original_filename_in_header: Dateiname für den Header (Standard: Output-Dateiname)
        metadata_value: Expliziter Metadaten-Wert (Standard: automatisch berechnet)
    """
    try:
        # Lade JSON-Daten
        print(f"Lade {input_filepath}...")
        with open(input_filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Validiere Version
        version = json_data.get('version', 'unknown')
        if not version.startswith('4.'):
            print(f"WARNUNG: Erwartete v4.x Format, gefunden: {version}")
            response = input("Trotzdem fortfahren? (j/n): ")
            if response.lower() != 'j':
                return False
        
        # Konvertiere zu compact JSON
        json_str = json.dumps(json_data, separators=(',', ':'), ensure_ascii=False)
        decompressed_data = json_str.encode('utf-8')
        
        print(f"JSON-Größe: {len(decompressed_data):,} Bytes")
        
        # GZIP-Kompression (Level 9 für maximale Kompression)
        print("Komprimiere mit GZIP (Level 9)...")
        compressed_data = gzip.compress(decompressed_data, compresslevel=9)
        
        print(f"Komprimierte Größe: {len(compressed_data):,} Bytes")
        print(f"Kompressionsrate: {(1 - len(compressed_data) / len(decompressed_data)) * 100:.1f}%")
        
        # Bestimme Dateinamen für Header
        if original_filename_in_header is None:
            original_filename_in_header = os.path.basename(output_filepath)
        
        # Berechne Metadaten-Wert aus komprimierten Daten
        if metadata_value is None:
            metadata_value = calculate_metadata_value(compressed_data)
            print(f"Berechneter Metadaten-Wert: {metadata_value} (GZIP-Größe)")
        else:
            print(f"Verwendeter Metadaten-Wert: {metadata_value} (manuell)")
        
        print(f"\n=== Header-Konstruktion ===")
        
        # 1. Dateiname-Länge (4 Bytes, little-endian)
        filename_bytes = original_filename_in_header.encode('ascii')
        filename_length = len(filename_bytes)
        header_part1 = struct.pack('<I', filename_length)
        print(f"1. Dateiname-Länge: {filename_length} Bytes")
        
        # 2. Dateiname
        header_part2 = filename_bytes
        print(f"2. Dateiname: '{original_filename_in_header}'")
        
        # 3. Null-Terminator
        header_part3 = b'\x00'
        print(f"3. Null-Terminator: 1 Byte")
        
        # 4. Padding-Berechnung
        padding_size = calculate_padding(filename_length)
        header_part4 = b'\x00' * padding_size
        print(f"4. Padding: {padding_size} Bytes (für 4-Byte-Alignment)")
        
        # 5. Metadaten-Bytes (6 Bytes gesamt)
        #    - Erste 2 Bytes: 0x0000
        #    - Mittlere 2 Bytes: Metadaten-Wert (little-endian uint16)
        #    - Letzte 2 Bytes: 0x0000
        header_part5 = struct.pack('<HHH', 0x0000, metadata_value, 0x0000)
        print(f"5. Metadaten: 6 Bytes (00 00 {metadata_value:04x} 00 00)")
        
        # Kombiniere Header-Teile
        full_header = header_part1 + header_part2 + header_part3 + header_part4 + header_part5
        
        # Validiere 4-Byte-Alignment
        header_size = len(full_header)
        print(f"\nGesamte Header-Größe: {header_size} Bytes")
        
        if header_size % 4 == 0:
            print(f"✓ Header ist auf 4-Byte-Grenze aligned ({header_size} % 4 = 0)")
        else:
            print(f"✗ FEHLER: Header NICHT auf 4-Byte-Grenze! ({header_size} % 4 = {header_size % 4})")
            print(f"  Dies sollte nicht passieren! Bitte Padding-Berechnung prüfen.")
            return False
        
        # Header-Struktur anzeigen
        print(f"\nHeader-Struktur:")
        print(f"  Bytes 0-3:     Dateiname-Länge = {filename_length}")
        print(f"  Bytes 4-{4+filename_length-1}:     Dateiname = '{original_filename_in_header}'")
        print(f"  Byte {4+filename_length}:      Null-Terminator = 0x00")
        
        if padding_size > 0:
            padding_start = 4 + filename_length + 1
            padding_end = padding_start + padding_size - 1
            print(f"  Bytes {padding_start}-{padding_end}:    Padding = {header_part4.hex()}")
        
        meta_start = 4 + filename_length + 1 + padding_size
        print(f"  Bytes {meta_start}-{meta_start+5}:    Metadaten = {header_part5.hex()}")
        print(f"  Byte {header_size}+:     GZIP-Stream")
        
        # Kombiniere Header und komprimierte Daten
        final_data = full_header + compressed_data
        
        # Schreibe Ausgabe-Datei
        print(f"\nSchreibe {output_filepath}...")
        with open(output_filepath, 'wb') as f:
            f.write(final_data)
        
        # Zeige finale Statistiken
        print(f"\n=== Ergebnis ===")
        print(f"Header:      {len(full_header)} Bytes")
        print(f"GZIP-Daten:  {len(compressed_data):,} Bytes")
        print(f"Gesamt:      {len(final_data):,} Bytes")
        print(f"\n✓ Rekomprimierung erfolgreich!")
        
        return True
        
    except Exception as e:
        print(f"✗ Fehler bei der Rekomprimierung: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python recompress_beatmap.py <input.json> <output.gz> [header_filename] [metadata_value]")
        print("\nArgumente:")
        print("  input.json       - Dekomprimierte v4.0.0 Beatmap JSON")
        print("  output.gz        - Ausgabe-Datei (komprimiert mit Header)")
        print("  header_filename  - Optional: Dateiname für den Header (Standard: output Dateiname)")
        print("  metadata_value   - Optional: Expliziter Metadaten-Wert (Standard: automatisch)")
        print("\nBeispiele:")
        print("  python recompress_beatmap.py beatmap_v4.json Expert.beatmap.gz")
        print("  python recompress_beatmap.py beatmap_v4.json output.gz Expert.beatmap.gz")
        print("  python recompress_beatmap.py beatmap_v4.json output.gz Expert.beatmap.gz 5423")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    header_filename = sys.argv[3] if len(sys.argv) >= 4 else None
    metadata_value = int(sys.argv[4]) if len(sys.argv) >= 5 else None
    
    success = recompress_file(input_file, output_file, header_filename, metadata_value)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
