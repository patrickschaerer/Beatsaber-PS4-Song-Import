# Beat Saber PS4 - Custom Song "Booty Swing" Installation

## Übersicht
Diese Anleitung zeigt dir, wie du den Song "UGH" (BTS Music Pack) durch "Booty Swing" von Parov Stelar ersetzt.

## Vorbereitete Dateien

### Original (wird ersetzt):
- **Song**: UGH (BTS Music Pack)
- **AssetBundle**: `C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber\Image0\Media\StreamingAssets\BeatmapLevelsData\ugh`

### Custom Song (Ersatz):
- **Audio (WAV)**: `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\BootySwing.wav`
  - Dauer: 3:00.52 (180,52 Sekunden)
  - Format: 48kHz, 16-bit Stereo
- **Cover**: `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\cover.jpg`
- **Beatmaps**:
  - Hard: `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\Hard.dat`
  - Expert: `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\Expert.dat`

### Tools:
- **UABEA**: `C:\Users\Dev-Box-User\BeatsaberConversion\Tools\UABEA\UABEAvalonia.exe`

---

## WICHTIGER HINWEIS zur PS4-Spezifischen Konvertierung

Bevor wir mit UABEA arbeiten, müssen wir das Audio für die PS4 vorbereiten:

### Problem:
Die PS4-Version von Beat Saber verwendet **ATRAC9** Audio-Codec, nicht OGG/Vorbis wie die PC-Version.

### Aktuelle Situation:
- Wir haben das Audio als WAV konvertiert (✓)
- Wir müssen es noch zu ATRAC9 konvertieren (siehe unten)

---

## Schritt 1: UGH AssetBundle analysieren

1. **UABEA starten**:
   ```
   C:\Users\Dev-Box-User\BeatsaberConversion\Tools\UABEA\UABEAvalonia.exe
   ```

2. **AssetBundle öffnen**:
   - Klicke auf "Open" oder drücke Strg+O
   - Navigiere zu: `C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber\Image0\Media\StreamingAssets\BeatmapLevelsData\ugh`
   - Öffne die Datei `ugh` (ohne Dateierweiterung)

3. **Assets durchsuchen**:
   Du solltest mehrere Assets sehen:
   - **AudioClip** - Die Musikdatei (ATRAC9-kodiert)
   - **Texture2D** - Das Cover-Bild
   - **MonoBehaviour** oder **TextAsset** - Beatmap-Daten für verschiedene Schwierigkeiten
   - **LevelCollectionSO** oder ähnlich - Level-Metadaten

4. **WICHTIG - Struktur dokumentieren**:
   - Notiere die **Path ID** für jedes Asset
   - Notiere den **Typ** jedes Assets
   - Exportiere zunächst alle Assets, um ihre Struktur zu verstehen:
     - Rechtsklick auf AudioClip → "Export Raw" → Speichere als `ugh_original_audio.dat`
     - Rechtsklick auf Texture2D → "Export" → Speichere als `ugh_original_cover.png`
     - Exportiere die Beatmap-Daten

---

## Schritt 2: Audio-Format Problem (KRITISCH)

### Das Problem:
Die PS4 verwendet ATRAC9-Codec. Unser WAV muss konvertiert werden.

### Optionen:

#### Option A: at9tool (Sony SDK - schwer zu bekommen)
Dies ist das offizielle Tool, aber schwer zugänglich.

#### Option B: Vorhandenes Audio wiederverwenden
1. Exportiere das Original-Audio aus dem UGH Bundle
2. Untersuche das Format (ATRAC9 in Unity AudioClip)
3. Ersetze nur die Beatmap-Daten und das Cover, behalte aber das Original-Audio bei
   - **NACHTEIL**: Falscher Song spielt

#### Option C: PS4 SDK oder Community-Tools
- Manche Modder verwenden `at9-cli` oder `VGAudio` Tools
- VGAudio kann ATRAC9 erstellen

### Empfohlene Lösung: VGAudio installieren

VGAudio ist ein Open-Source Tool, das ATRAC9 erstellen kann.

**PAUSE HIER** - Bevor du weitermachst:
- Sollen wir VGAudio herunterladen und das Audio konvertieren?
- Oder möchtest du zunächst nur die Beatmaps und das Cover ersetzen (als Test)?

---

## Schritt 3: Assets ersetzen (nach Audio-Konvertierung)

### 3.1 Cover-Bild ersetzen

1. In UABEA: Finde das **Texture2D** Asset
2. Rechtsklick → "Edit"
3. "Load" → Wähle `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\cover.jpg`
4. Stelle sicher, dass die Größe passt (meistens 256x256 oder 512x512)
5. "Save" klicken

### 3.2 Audio ersetzen

**NACH Audio-Konvertierung zu ATRAC9:**

1. In UABEA: Finde das **AudioClip** Asset
2. Rechtsklick → "Edit" oder "Import Raw"
3. Ersetze mit der konvertierten ATRAC9-Datei
4. **WICHTIG**: Passe die Metadaten an:
   - **m_Length**: `180.52` (Sekunden)
   - **m_Frequency**: `48000` (Hz)
   - **m_Channels**: `2` (Stereo)

### 3.3 Beatmap-Daten ersetzen

Dies ist der komplexeste Teil:

1. **Für Hard Schwierigkeit**:
   - Finde das entsprechende MonoBehaviour/TextAsset
   - Die PC .dat Datei ist JSON - PS4 erwartet eventuell binäre Daten
   - **Problem**: Unity serialisiert diese Daten anders
   - **Lösung**: Du musst eventuell die JSON-Daten manuell in die Unity-Felder eintragen

2. **Für Expert Schwierigkeit**:
   - Gleicher Prozess wie Hard

**HINWEIS**: Dies ist der schwierigste Teil, da Beat Saber auf PS4 ein proprietäres binäres Format verwendet. Die .dat Dateien von BeatSaver sind für PC gemacht.

---

## Schritt 4: Speichern und Repacken

1. **In UABEA**: "File" → "Save" oder Strg+S
2. Speichere das modifizierte Bundle

3. **Erstelle Backup**:
   ```bash
   copy "C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber\Image0\Media\StreamingAssets\BeatmapLevelsData\ugh" "C:\Users\Dev-Box-User\BeatsaberConversion\ModifiedGame\ugh.backup"
   ```

4. **Ersetze das Original**:
   - Kopiere das modifizierte Bundle zurück

---

## Schritt 5: Fake PKG erstellen

Du benötigst **Orbis Pub Tools** oder **PS4 PKG Tool**.

### Option A: Orbis Publishing Tools (Offiziell, benötigt Dev-Lizenz)
- Komplex, nicht für Homebrew geeignet

### Option B: PS4 PKG Tool (Community)
1. Lade PS4 PKG Tool herunter
2. Öffne das Tool
3. "Create PKG from Directory"
4. Wähle: `C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber`
5. **Title ID**: `CUSA12878`
6. **Content ID**: (Original beibehalten)
7. **Passcode**: `00000000000000000000000000000000`
8. Erstelle das PKG

---

## Schritt 6: Installation auf PS4

1. **Kopiere das PKG** auf USB (FAT32 formatiert)
2. **Auf PS4**:
   - Starte GoldHEN/HEN
   - Gehe zu "Debug Settings" → "Install PKG Files"
   - Wähle dein PKG
3. **Starte Beat Saber** und teste!

---

## Zusammenfassung der offenen Probleme

### ✓ Erledigt:
- Audio zu WAV konvertiert
- Cover-Bild vorhanden
- Beatmap .dat Dateien vorhanden (PC-Format)
- UABEA installiert

### ⚠ Zu tun:
1. **Audio zu ATRAC9 konvertieren** - KRITISCH
2. **Beatmap-Format konvertieren** - Die .dat Dateien müssen eventuell angepasst werden
3. **PS4 PKG Tool besorgen** - Für das Repackaging

---

## Nächster Schritt

**WARTE** - Bevor du mit UABEA arbeitest, lass uns:

1. VGAudio herunterladen und installieren
2. Das Audio zu ATRAC9 konvertieren
3. Dann erst das AssetBundle modifizieren

**Soll ich VGAudio jetzt herunterladen und die Audio-Konvertierung automatisieren?**
