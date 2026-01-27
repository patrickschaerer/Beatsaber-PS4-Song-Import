# Beat Saber PS4 Custom Song - Zusammenfassung & Nächste Schritte

## ✅ Was wurde vorbereitet:

### Installierte Tools:
- **UABEA**: `C:\Users\Dev-Box-User\BeatsaberConversion\Tools\UABEA\UABEAvalonia.exe`
- **vgmstream**: `C:\Users\Dev-Box-User\BeatsaberConversion\Tools\vgmstream\vgmstream-cli.exe`
- **FFmpeg**: `C:\Users\Dev-Box-User\BeatsaberConversion\Tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe`

### Vorbereitete Dateien:
- **Audio (WAV)**: `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\BootySwing.wav`
  - Format: 48kHz, 16-bit Stereo
  - Dauer: 3:00.52 (180,52 Sekunden)
- **Cover**: `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\cover.jpg` (256x256)
- **Beatmaps**:
  - Hard: `Hard.dat` (JSON Version 2.0.0)
  - Expert: `Expert.dat` (JSON Version 2.0.0)

### Original PS4 Spiel:
- **Pfad**: `C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber`
- **Title ID**: CUSA12878 (NA/JP Version)
- **Zu ersetzender Song**: UGH (BTS Music Pack)
- **AssetBundle**: `...\StreamingAssets\BeatmapLevelsData\ugh`

---

## ⚠ Das ATRAC9-Audio-Problem

### Problem:
Die PS4-Version von Beat Saber verwendet **ATRAC9**-Codec für Audio, ein proprietäres Sony-Format.

### Versuchte Lösungen:
- ✅ Audio zu WAV konvertiert (erfolgreich)
- ❌ VGAudio unterstützt kein ATRAC9
- ❌ PS4-Beat-Saber-Converter Repository existiert nicht mehr

### Verfügbare Optionen:

#### Option 1: **Nur Beatmaps + Cover ersetzen** (Empfohlen zum Testen)
- **Vorteil**: Einfacher, kein Audio-Konvertierungs-Problem
- **Nachteil**: Das Original-Audio (UGH) spielt weiter, aber mit deinen Custom Beatmaps und Cover
- **Resultat**: Du kannst testen, ob die Beatmaps funktionieren

#### Option 2: **at9tool verwenden** (Schwierig)
- Sony's offizielles Tool (Teil des PS4 SDK)
- Schwer zu bekommen (benötigt DevNet-Zugang)
- Wenn du Zugang hast:
  ```bash
  at9tool -e -br 144 input.wav output.at9
  ```

#### Option 3: **Alternative Audio-Methode** (Experimentell)
- Manche Modder extrahieren ein ATRAC9-Audio von einem anderen Song
- Ersetzen es "binär" mit gleichlanger Audio-Datei
- Sehr komplex, hohe Fehlerrate

#### Option 4: **Warten auf bessere Tools**
- Die PS4 Homebrew-Szene entwickelt sich weiter
- Eventuell kommt ein neues ATRAC9-Tool

---

## 🎯 Empfohlener Workflow (ohne Audio)

### Schritt 1: UGH AssetBundle mit UABEA analysieren

1. Starte UABEA:
   ```
   C:\Users\Dev-Box-User\BeatsaberConversion\Tools\UABEA\UABEAvalonia.exe
   ```

2. Öffne das AssetBundle:
   - File → Open
   - Navigiere zu: `C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber\Image0\Media\StreamingAssets\BeatmapLevelsData\ugh`

3. Finde diese Assets (notiere ihre Path IDs):
   - **Texture2D** (Cover-Bild)
   - **MonoBehaviour** oder **BeatmapData** (Beatmap-Daten für verschiedene Schwierigkeiten)
   - **AudioClip** (Audio - NICHT ersetzen fürs Erste)

### Schritt 2: Cover ersetzen

1. In UABEA: Finde das **Texture2D** Asset
2. Rechtsklick → **Edit**
3. Im Editor: **Load** → Wähle `C:\Users\Dev-Box-User\BeatsaberConversion\BootySwing_extracted\cover.jpg`
4. **OK** → **Save**

### Schritt 3: Beatmap-Daten vorbereiten

**WICHTIG**: Die PS4-Version verwendet serialisierte Unity-Objekte, nicht JSON-Dateien.

Es gibt zwei Ansätze:

#### Ansatz A: JSON direkt in TextAsset-Feld einfügen (einfacher)
1. Finde ein **TextAsset** mit Beatmap-Daten
2. Rechtsklick → **Edit**
3. Finde das Feld `m_Script` oder `m_Data`
4. Öffne `Hard.dat` in einem Texteditor, kopiere den gesamten JSON-Inhalt
5. Füge den JSON ein
6. Wiederholen für Expert

#### Ansatz B: MonoBehaviour-Felder einzeln bearbeiten (präziser, komplexer)
1. Finde ein **MonoBehaviour** mit Beatmap-Daten
2. Rechtsklick → **Edit**
3. Schaue dir die Feldstruktur an (z.B. `_notes`, `_obstacles`, `_events`)
4. Übertrage die Daten aus `Hard.dat` manuell in die entsprechenden Felder

**HINWEIS**: Dies ist der schwierigste Teil. Beat Saber PS4 verwendet eine komplexe interne Struktur.

### Schritt 4: Speichern

1. File → **Save**
2. Wähle einen Speicherort: `C:\Users\Dev-Box-User\BeatsaberConversion\ModifiedGame\ugh`

### Schritt 5: Bundle ins Spiel einfügen

1. **Backup erstellen**:
   ```bash
   copy "C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber\Image0\Media\StreamingAssets\BeatmapLevelsData\ugh" "C:\Users\Dev-Box-User\BeatsaberConversion\ModifiedGame\ugh.backup"
   ```

2. **Ersetzen**:
   ```bash
   copy "C:\Users\Dev-Box-User\BeatsaberConversion\ModifiedGame\ugh" "C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber\Image0\Media\StreamingAssets\BeatmapLevelsData\ugh"
   ```

### Schritt 6: Fake PKG erstellen

Du benötigst **PS4 PKG Tool** oder **Fake PKG Generator**.

**Download-Optionen**:
- PS4 PKG Tool: https://www.psxhax.com/threads/ps4-pkg-tool-package-creator-extractor-by-pearlxcore.4283/
- Fake PKG Generator: Suche in PS4 Homebrew-Communities

**Verwendung** (PS4 PKG Tool):
1. Öffne PS4 PKG Tool
2. Wähle "Create PKG from Directory"
3. **Source**: `C:\Users\Dev-Box-User\BeatsaberConversion\BeatSaberOriginal\Beat Saber`
4. **Title ID**: `CUSA12878`
5. **Content ID**: Kopiere von der Original-Disc (wichtig!)
6. **Type**: Patch (GP4)
7. **Passcode**: `00000000000000000000000000000000`
8. Erstelle PKG

### Schritt 7: Installation auf PS4

1. Kopiere das PKG auf USB (FAT32-formatiert)
2. USB in PS4 einstecken
3. Starte GoldHEN/HEN
4. Gehe zu **Debug Settings** → **Game** → **Package Installer**
5. Wähle dein PKG
6. Installieren
7. Beat Saber starten und "UGH" Song spielen

---

## 🔧 Alternative: Einfacher Test ohne PKG-Neuerstell

Falls du direkten FTP-Zugriff auf deine PS4 hast:

1. **FTP aktivieren** auf PS4 (über GoldHEN)
2. **FTP-Client** (FileZilla) mit PS4 verbinden
3. Navigiere zu: `/user/app/CUSA12878/app0/Media/StreamingAssets/BeatmapLevelsData/`
4. Ersetze direkt die `ugh`-Datei
5. PS4 neu starten
6. Beat Saber starten

**Dies umgeht das PKG-Repackaging komplett!**

---

## 📋 Was du als Nächstes tun solltest

### Option A: Test ohne Audio (Schnellster Weg)
1. ✅ Öffne UABEA
2. ✅ Ersetze Cover
3. ✅ Versuche Beatmaps zu ersetzen (experimentell)
4. ✅ Speichern und per FTP auf PS4 kopieren
5. ✅ Testen!

### Option B: Vollständige Lösung mit Audio
1. ⏳ Suche nach `at9tool` oder Kontakt mit PS4 Modding-Community
2. ⏳ Konvertiere Audio zu ATRAC9
3. ⏳ Ersetze alle Assets (Cover, Audio, Beatmaps)
4. ⏳ PKG erstellen und installieren

---

## 🔗 Nützliche Ressourcen

- **UABEA GitHub**: https://github.com/nesrak1/UABEA
- **PS4 Homebrew Reddit**: r/ps4homebrew
- **Beat Saber Modding Discord**: https://discord.gg/beatsabermods
- **GBAtemp PS4 Forum**: https://gbatemp.net/forums/sony-playstation-4.228/

---

## 📞 Nächste Schritte mit mir

Sag mir, welchen Weg du gehen möchtest:

1. **"Zeig mir, wie ich UABEA verwende"** - Ich erstelle eine detaillierte Video-/Screenshot-Anleitung
2. **"Hilf mir, PS4 PKG Tool zu verwenden"** - Ich erkläre das PKG-Repackaging
3. **"Ich habe FTP-Zugriff"** - Ich zeige dir den direkten Ersetzungs-Weg
4. **"Ich habe at9tool"** - Ich zeige dir die Audio-Konvertierung
5. **"Andere Idee"** - Sag mir, was du brauchst!

---

**Status**: Bereit für manuelle UABEA-Bearbeitung. Audio-Problem identifiziert, aber umgehbar.
