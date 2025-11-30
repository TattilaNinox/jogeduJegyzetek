#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebM to MP3 Converter
Konvertálja a WebM fájlokat MP3 formátumra, maximum 5 MB mérettel
"""

import os
import subprocess
import sys
import glob
from pathlib import Path

# Maximum fájlméret: 5 MB
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def check_ffmpeg():
    """Ellenőrzi, hogy az ffmpeg telepítve van-e"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Próbáljuk meg megtalálni közvetlenül
        ffmpeg_path = find_ffmpeg_in_path()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            # Módosítjuk a PATH-ot ideiglenesen
            os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get('PATH', '')
            try:
                subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              check=True)
                return True
            except:
                return False
        return False

def find_ffmpeg_in_path():
    """Megpróbálja megtalálni az ffmpeg-et a tipikus telepítési helyeken"""
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_*\ffmpeg-*\bin\ffmpeg.exe"),
    ]
    
    for path_pattern in common_paths:
        # Ha van wildcard, próbáljuk meg globbal
        if '*' in path_pattern:
            matches = glob.glob(path_pattern)
            if matches:
                return matches[0]
        elif os.path.exists(path_pattern):
            return path_pattern
    
    return None

def try_install_ffmpeg():
    """Megpróbálja telepíteni az ffmpeg-et"""
    print("\n[!] Automatikus telepitesi kiserlet...")
    sys.stdout.flush()
    
    # Először ellenőrizzük, hogy már telepítve van-e (winget list)
    try:
        print("   [INFO] Ellenorzes: FFmpeg mar telepítve van-e...")
        sys.stdout.flush()
        result = subprocess.run(
            ['winget', 'list', '--id=Gyan.FFmpeg'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and 'Gyan.FFmpeg' in result.stdout:
            print("   [INFO] FFmpeg mar telepítve van winget szerint!")
            sys.stdout.flush()
            # Próbáljuk meg megtalálni a PATH-ban vagy tipikus helyeken
            ffmpeg_path = find_ffmpeg_in_path()
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                print(f"   [INFO] FFmpeg megtalalva: {ffmpeg_path}")
                print("   [FIGYELMEZTETES] Az FFmpeg telepítve van, de nincs a PATH-ban.")
                print("   [FIGYELMEZTETES] Indits ujra a terminalt vagy add hozza a PATH-hoz.")
                sys.stdout.flush()
            return False  # Nem sikerült telepíteni, mert már telepítve van
    except Exception:
        pass
    
    # Próbáljuk meg winget-tel telepíteni (ha még nincs telepítve)
    try:
        print("   [1/2] Probalokozas winget-tel...")
        sys.stdout.flush()
        result = subprocess.run(
            ['winget', 'install', '--id=Gyan.FFmpeg', '-e', 
             '--accept-source-agreements', '--accept-package-agreements'],
            capture_output=True,  # Capture output hogy ne legyen interaktív
            text=True,
            timeout=300,
            input='\n'  # Automatikus válasz
        )
        # Winget exit code 2316632107 azt jelenti hogy már telepítve van
        if result.returncode == 0 or 'already installed' in result.stdout.lower() or result.returncode == 2316632107:
            print("   [OK] FFmpeg mar telepítve van vagy sikeresen telepítve!")
            sys.stdout.flush()
            return True
        else:
            print(f"   [HIBA] Winget telepites sikertelen (exit code: {result.returncode})")
            sys.stdout.flush()
    except FileNotFoundError:
        print("   [HIBA] Winget nem talalhato a rendszeren")
        sys.stdout.flush()
    except subprocess.TimeoutExpired:
        print("   [HIBA] Winget telepites tullepte az idokorlatot")
        sys.stdout.flush()
    except Exception as e:
        print(f"   [HIBA] Winget hiba: {str(e)[:100]}")
        sys.stdout.flush()
    
    # Chocolatey-t kihagyjuk, mert interaktív lehet
    print("   [INFO] Chocolatey kihagyva (interaktiv lehet)")
    sys.stdout.flush()
    
    return False

def get_file_size(file_path):
    """Visszaadja a fájl méretét byte-ban"""
    return os.path.getsize(file_path)

def convert_webm_to_mp3(input_file, output_file, bitrate=128):
    """
    Konvertálja a WebM fájlt MP3-ra a megadott bitrate-tel
    
    Args:
        input_file: Bemeneti WebM fájl útvonala
        output_file: Kimeneti MP3 fájl útvonala
        bitrate: Audio bitrate kbps-ben (alapértelmezett: 128)
    
    Returns:
        True ha sikeres, False ha nem
    """
    try:
        # Abszolút útvonalak és Windows-kompatibilis formátum
        input_path = Path(input_file).resolve()
        output_path = Path(output_file).resolve()
        
        # Windows-on forward slash-okat használunk az ffmpeg számára
        input_str = str(input_path).replace('\\', '/')
        output_str = str(output_path).replace('\\', '/')
        
        cmd = [
            'ffmpeg',
            '-i', input_str,
            '-vn',  # Nincs video (csak audio)
            '-codec:a', 'libmp3lame',  # Audio codec
            '-b:a', f'{bitrate}k',  # Audio bitrate
            '-y',  # Felülírja a kimeneti fájlt ha létezik
            output_str
        ]
        
        result = subprocess.run(cmd, 
                      capture_output=True, 
                      check=True,
                      text=True,
                      encoding='utf-8',
                      errors='ignore',
                      timeout=600)  # 10 perc timeout nagy fájlokhoz
        return True
    except subprocess.CalledProcessError as e:
        # Az ffmpeg a stderr-re írja a hibákat és a verziót is
        error_msg = ''
        if e.stderr:
            if isinstance(e.stderr, bytes):
                error_msg = e.stderr.decode('utf-8', errors='ignore')
            else:
                error_msg = str(e.stderr)
        elif e.stdout:
            if isinstance(e.stdout, bytes):
                error_msg = e.stdout.decode('utf-8', errors='ignore')
            else:
                error_msg = str(e.stdout)
        else:
            error_msg = str(e)
        
        # Keresünk a hibaüzenetben releváns információkat (kihagyjuk a verziót)
        error_lines = error_msg.split('\n') if error_msg else []
        # Keresünk olyan sorokat, amelyek tartalmaznak hibát (nem csak verziót)
        relevant_errors = [line for line in error_lines if any(keyword in line.lower() for keyword in ['error', 'invalid', 'cannot', 'not found', 'no such', 'failed', 'unable'])]
        
        if relevant_errors:
            print(f"Hiba a konverzio soran:")
            for err_line in relevant_errors[:5]:  # Maximum 5 releváns hiba sor
                print(f"  {err_line}")
        else:
            # Ha nincs releváns hiba, mutassuk az utolsó sorokat
            last_lines = error_lines[-10:] if len(error_lines) > 10 else error_lines
            print(f"Hiba a konverzio soran (utolso sorok):")
            for err_line in last_lines:
                if err_line.strip():  # Csak nem üres sorokat
                    print(f"  {err_line}")
        
        return False

def convert_with_size_limit(input_file, output_file):
    """
    Konvertálja a WebM fájlt MP3-ra, biztosítva hogy ne legyen nagyobb 5 MB-nál
    
    Args:
        input_file: Bemeneti WebM fájl útvonala
        output_file: Kimeneti MP3 fájl útvonala
    """
    # Bitrate értékek kbps-ben (csökkenő sorrendben)
    bitrates = [192, 160, 128, 96, 64, 48, 32]
    
    for bitrate in bitrates:
        print(f"Probalokozas {bitrate} kbps bitrate-tel...")
        
        if convert_webm_to_mp3(input_file, output_file, bitrate):
            file_size = get_file_size(output_file)
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"Konvertalva! Fajlmeret: {file_size_mb:.2f} MB")
            
            if file_size <= MAX_FILE_SIZE_BYTES:
                print(f"[OK] Sikeres! A fajl merete ({file_size_mb:.2f} MB) kisebb mint {MAX_FILE_SIZE_MB} MB.")
                return True
            else:
                print(f"[FIGYELMEZTETES] A fajl meg mindig tul nagy ({file_size_mb:.2f} MB). Csokkentjuk a bitrate-et...")
        else:
            print(f"[FIGYELMEZTETES] Hiba tortent a {bitrate} kbps bitrate-tel valo konverzio soran.")
    
    # Ha még mindig túl nagy, próbáljuk meg a legalacsonyabb bitrate-tel
    print(f"\n[FIGYELMEZTETES] A fajl meg mindig tul nagy lehet a legalacsonyabb bitrate-tel is.")
    print(f"   Ellenorizd a kimeneti fajlt: {output_file}")
    return False

def main():
    """Fő függvény"""
    print("="*60)
    print("WebM to MP3 Converter")
    print("="*60)
    print()
    sys.stdout.flush()
    
    # Ellenőrizzük az ffmpeg telepítését
    print("Ellenőrzés: FFmpeg telepítve van-e...")
    sys.stdout.flush()
    
    if not check_ffmpeg():
        print("[HIBA] Az ffmpeg nincs telepítve vagy nem található!")
        sys.stdout.flush()
        
        # Próbáljuk meg automatikusan telepíteni
        if try_install_ffmpeg():
            print("\n[INFO] Varjunk egy pillanatot, majd ellenorizzuk ujra...")
            sys.stdout.flush()
            import time
            time.sleep(3)  # Több időt adunk
            
            # Újra ellenőrizzük
            print("Ujraellenorzes...")
            sys.stdout.flush()
            if check_ffmpeg():
                print("[OK] Az FFmpeg sikeresen telepítve es elerheto!")
                sys.stdout.flush()
            else:
                print("[FIGYELMEZTETES] Az FFmpeg telepítve lett, de meg nem elerheto a PATH-ban.")
                print("   Kerlek, indits ujra a terminalt, majd futtasd ujra ezt a scriptet.")
                sys.stdout.flush()
                sys.exit(1)
        else:
            print("\n" + "="*60)
            print("FFMPEG TELEPÍTÉSI ÚTMUTATÓ")
            print("="*60)
            print("\nAz automatikus telepítés nem sikerült.")
            print("\n1. MANUÁLIS TELEPÍTÉS:")
            print("   a) Winget-tel (Windows 10/11):")
            print("      winget install --id=Gyan.FFmpeg -e")
            print("   b) Chocolatey-vel (ha telepítve van):")
            print("      choco install ffmpeg -y")
            print("   c) Batch fájl:")
            print("      install_ffmpeg.bat")
            print("   d) Python script:")
            print("      python install_ffmpeg_python.py")
            print("\n2. MANUÁLIS TELEPÍTÉS (ha egyik sem működik):")
            print("   - Töltsd le: https://www.gyan.dev/ffmpeg/builds/")
            print("   - Csomagold ki és add hozzá a PATH-hoz")
            print("\n3. UTÁN:")
            print("   - Indíts újra a terminált")
            print("   - Futtasd újra ezt a scriptet")
            print("="*60)
            sys.stdout.flush()
            sys.exit(1)
    else:
        print("[OK] Az FFmpeg telepítve van es elerheto!")
        sys.stdout.flush()
    
    print()
    print("="*60)
    print("Fajlok keresese...")
    print("="*60)
    sys.stdout.flush()
    
    # Útvonalak beállítása
    # A script a script/Hang jegyzetek/ mappában van, szóval 2x parent = script, 3x parent = projekt gyökér
    base_dir = Path(__file__).parent.parent.parent
    mp3_dir = base_dir / 'MP3'
    
    print(f"Kereses a kovetkezo mappaban: {mp3_dir}")
    sys.stdout.flush()
    
    if not mp3_dir.exists():
        print(f"[HIBA] A {mp3_dir} mappa nem talalhato!")
        sys.stdout.flush()
        sys.exit(1)
    
    # WebM fájlok keresése
    webm_files = list(mp3_dir.glob('*.webm'))
    
    print(f"Talalt WebM fajlok: {len(webm_files)}")
    sys.stdout.flush()
    
    if not webm_files:
        print("[HIBA] Nincs WebM fajl az MP3 mappaban!")
        sys.stdout.flush()
        sys.exit(1)
    
    # Minden WebM fájlt konvertálunk
    for webm_file in webm_files:
        print(f"\n{'='*60}")
        print(f"Feldolgozás: {webm_file.name}")
        print(f"{'='*60}")
        sys.stdout.flush()
        
        # Kimeneti fájl neve (ugyanaz, csak .mp3 kiterjesztéssel)
        output_file = mp3_dir / f"{webm_file.stem}.mp3"
        
        # Ha már létezik az MP3 fájl, töröljük
        if output_file.exists():
            print(f"[FIGYELMEZTETES] A {output_file.name} mar letezik, felulirjuk...")
            sys.stdout.flush()
            output_file.unlink()
        
        # Konverzió
        print("Konverzio inditasa...")
        sys.stdout.flush()
        success = convert_with_size_limit(webm_file, output_file)
        
        if success:
            print(f"[OK] Sikeresen konvertalva: {output_file.name}")
            sys.stdout.flush()
        else:
            print(f"[FIGYELMEZTETES] {output_file.name} konverzioja befejezodott, de ellenorizd a meretet!")
            sys.stdout.flush()
    
    print(f"\n{'='*60}")
    print("Konverzio befejezve!")
    print(f"{'='*60}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()

