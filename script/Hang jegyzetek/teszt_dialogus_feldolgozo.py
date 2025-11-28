#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialógus Feldolgozó Teszt Script
=================================

Ez a script ellenőrzi a webm_dialogus_osszeallito.py függőségeit
és teszteli a funkciók működését.
"""

import sys
import os

print("="*60)
print("DIALÓGUS FELDOLGOZÓ TESZT")
print("="*60)

# 1. Python verzió ellenőrzése
print("\n1. Python verzió ellenőrzése...")
print(f"   Python verzió: {sys.version}")
if sys.version_info < (3, 7):
    print("   ❌ HIBA: Python 3.7 vagy újabb szükséges!")
    sys.exit(1)
else:
    print("   ✓ Python verzió megfelelő")

# 2. Pydub ellenőrzése
print("\n2. Pydub könyvtár ellenőrzése...")
try:
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
    print("   ✓ Pydub telepítve")
except ImportError as e:
    print(f"   ❌ Pydub nincs telepítve: {e}")
    print("   Telepítsd: pip install pydub")
    sys.exit(1)

# 3. Numpy ellenőrzése
print("\n3. Numpy könyvtár ellenőrzése...")
try:
    import numpy as np
    print(f"   ✓ Numpy telepítve (verzió: {np.__version__})")
except ImportError as e:
    print(f"   ❌ Numpy nincs telepítve: {e}")
    print("   Telepítsd: pip install numpy")
    sys.exit(1)

# 4. FFmpeg ellenőrzése
print("\n4. FFmpeg ellenőrzése...")
try:
    import subprocess
    result = subprocess.run(
        ['ffmpeg', '-version'],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"   ✓ FFmpeg telepítve")
        print(f"   {version_line}")
    else:
        print("   ❌ FFmpeg nem található")
        sys.exit(1)
except FileNotFoundError:
    print("   ❌ FFmpeg nincs telepítve vagy nincs a PATH-ban")
    print("   Telepítési útmutató: FFMPEG_TELEPITES.md")
    sys.exit(1)
except Exception as e:
    print(f"   ⚠️  FFmpeg ellenőrzési hiba: {e}")

# 5. Script fájl ellenőrzése
print("\n5. webm_dialogus_osszeallito.py ellenőrzése...")
script_path = os.path.join(os.path.dirname(__file__), 'webm_dialogus_osszeallito.py')
if os.path.exists(script_path):
    print(f"   ✓ Script megtalálva: {script_path}")
else:
    print(f"   ❌ Script nem található: {script_path}")
    sys.exit(1)

# 6. WEBM fájlok keresése (opcionális)
print("\n6. Teszt WEBM fájlok keresése...")
test_files = []
mp3_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'MP3')
if os.path.exists(mp3_dir):
    for file in os.listdir(mp3_dir):
        if file.endswith('.webm'):
            test_files.append(os.path.join(mp3_dir, file))
    
    if test_files:
        print(f"   ✓ Talált WEBM fájlok ({len(test_files)} db):")
        for f in test_files:
            print(f"     - {os.path.basename(f)}")
    else:
        print("   ℹ️  Nincs WEBM fájl a MP3/ mappában")
else:
    print("   ℹ️  MP3/ mappa nem található")

# 7. Funkció tesztelése (ha van WEBM fájl)
print("\n7. Alapfunkciók tesztelése...")
if len(test_files) >= 1:
    print(f"   Teszt fájl betöltése: {os.path.basename(test_files[0])}")
    try:
        # Csak betöltjük, nem dolgozzuk fel
        audio = AudioSegment.from_file(test_files[0])
        duration = len(audio) / 1000
        print(f"   ✓ Fájl sikeresen betöltve")
        print(f"   Hossz: {duration:.2f} másodperc")
        print(f"   Csatornák: {audio.channels}")
        print(f"   Sample rate: {audio.frame_rate} Hz")
    except Exception as e:
        print(f"   ❌ Fájl betöltési hiba: {e}")
else:
    print("   ℹ️  Nincs teszt fájl, funkció tesztelés kihagyva")

# Összegzés
print("\n" + "="*60)
print("TESZT EREDMÉNY")
print("="*60)
print("✅ Minden függőség telepítve!")
print("\nA script használatra kész. Példa parancs:")
print("\npython webm_dialogus_osszeallito.py \\")
print("    --kerdesek MP3/kerdesek.webm \\")
print("    --valaszok MP3/valaszok.webm \\")
print("    --kimenet Tételek/A_cselekvokepesseg/Dialógus/Audio \\")
print("    --tetel A_cselekvokepesseg")
print("\nRészletes dokumentáció: README_DIALOGUS_FELDOLGOZO.md")
print("="*60)

