#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebM fájlok összeállító script
Összeállítja a 1.webm, 2.webm és esetleg 3.webm fájlokat,
eltávolítja a szüneteket (több mint 4 mp) minden fájl elejéről és végéről,
és MP3-re konvertálja maximum 7 MB mérettel.
"""

import os
import subprocess
import sys
import glob
import re
import time
import threading
from pathlib import Path

# Maximum fájlméret: 7 MB
MAX_FILE_SIZE_MB = 7
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Szünet küszöbérték másodpercben (több mint 4 mp = 4.1 mp)
SILENCE_THRESHOLD = 4.1

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

def get_file_size(file_path):
    """Visszaadja a fájl méretét byte-ban"""
    return os.path.getsize(file_path)

def detect_all_silences(input_file):
    """
    Detektálja az összes szünetet a fájlban, amelyek hosszabbak mint a küszöbérték
    
    Args:
        input_file: Bemeneti fájl útvonala
    
    Returns:
        Lista a szünetekről: [(start, end), ...] vagy None ha hiba
    """
    try:
        # Először megkapjuk a fájl teljes hosszát
        cmd_duration = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(input_file)
        ]
        
        result = subprocess.run(cmd_duration, 
                              capture_output=True, 
                              check=True,
                              text=True,
                              encoding='utf-8',
                              errors='ignore',
                              timeout=30)
        total_duration = float(result.stdout.strip())
        
        # Detektáljuk az összes szünetet
        print(f"  Szunet detektalas folyamatban (kuszobertek: {SILENCE_THRESHOLD}s)...")
        sys.stdout.flush()
        
        cmd_detect = [
            'ffmpeg',
            '-i', str(input_file),
            '-af', f'silencedetect=noise=-50dB:d={SILENCE_THRESHOLD}',
            '-f', 'null',
            '-'
        ]
        
        timeout_seconds = max(300, int(total_duration * 2))
        
        result = subprocess.run(cmd_detect, 
                              capture_output=True, 
                              check=False,
                              text=True,
                              encoding='utf-8',
                              errors='ignore',
                              timeout=timeout_seconds)
        
        output = result.stderr if result.stderr else ''
        if not output and result.stdout:
            output = result.stdout
        
        if not output:
            print("  Nincs kimenet a szunet detektalasbol")
            sys.stdout.flush()
            return None
        
        # Keresünk minden silence_start és silence_end párost a kimenetben
        silences = []
        lines = output.split('\n')
        
        current_start = None
        for line in lines:
            # Keressük a silence_start-et
            start_match = re.search(r'silence_start: ([\d.]+)', line)
            if start_match:
                current_start = float(start_match.group(1))
            
            # Keressük a silence_end-et
            end_match = re.search(r'silence_end: ([\d.]+)', line)
            if end_match and current_start is not None:
                end = float(end_match.group(1))
                duration = end - current_start
                if duration >= SILENCE_THRESHOLD:
                    silences.append((current_start, end))
                    print(f"    Szunet talalva: {current_start:.2f}s - {end:.2f}s ({duration:.2f}s)")
                    sys.stdout.flush()
                current_start = None
        
        if len(silences) == 0:
            print("  Nem talalhato 4 mp-nel hosszabb szunet")
            sys.stdout.flush()
            return None
        
        print(f"  Osszesen {len(silences)} szunet talalva")
        sys.stdout.flush()
        return silences
    except subprocess.TimeoutExpired:
        print("  Szunet detektalas timeout")
        sys.stdout.flush()
        return None
    except Exception as e:
        print(f"  Hiba a szunet detektalas soran: {str(e)[:100]}")
        sys.stdout.flush()
        return None

def detect_silence(input_file):
    """
    Detektálja a szüneteket a fájlban és visszaadja a kezdő és vég időpontokat
    
    Args:
        input_file: Bemeneti fájl útvonala
    
    Returns:
        (start_time, end_time) tuple másodpercben, vagy (None, None) ha hiba
    """
    try:
        print("  Fajl hosszanak meghatarozasa...")
        sys.stdout.flush()
        
        # Először megkapjuk a fájl teljes hosszát
        cmd_duration = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(input_file)
        ]
        
        result = subprocess.run(cmd_duration, 
                              capture_output=True, 
                              check=True,
                              text=True,
                              encoding='utf-8',
                              errors='ignore',
                              timeout=30)
        total_duration = float(result.stdout.strip())
        print(f"  Fajl hossza: {total_duration:.2f} masodperc")
        sys.stdout.flush()
        
        # Most detektáljuk a szüneteket (timeout-tal, hogy ne akadjon el)
        print("  Szunetek detektalasa (ez eltarthat egy ideig)...")
        sys.stdout.flush()
        
        cmd_detect = [
            'ffmpeg',
            '-i', str(input_file),
            '-af', f'silencedetect=noise=-50dB:d={SILENCE_THRESHOLD}',
            '-f', 'null',
            '-'
        ]
        
        # Timeout: maximum 5 perc nagy fájloknál is
        timeout_seconds = max(300, int(total_duration * 2))  # Legalább 5 perc, vagy 2x a fájl hossza
        
        result = subprocess.run(cmd_detect, 
                              capture_output=True, 
                              check=False,  # Ne dobjon hibát, mert az ffmpeg stderr-re ír
                              text=True,
                              encoding='utf-8',
                              errors='ignore',
                              timeout=timeout_seconds)
        
        # Keresünk silence_start és silence_end értékeket
        # Az ffmpeg a stderr-re írja a kimenetét
        output = result.stderr if result.stderr else ''
        if not output and result.stdout:
            output = result.stdout
        
        start_time = 0.0
        end_time = total_duration
        
        # Keresünk kezdeti szünetet
        if not output:
            return (None, None)
            
        silence_starts = re.findall(r'silence_start: ([\d.]+)', output)
        silence_ends = re.findall(r'silence_end: ([\d.]+)', output)
        
        # Ha van kezdeti szünet és az hosszabb mint a küszöbérték
        if silence_starts:
            first_silence_start = float(silence_starts[0])
            # Ha a szünet a fájl elején van (0-hoz közel, legfeljebb 5 másodperc)
            # Fontos: még akkor is kezeljük, ha pontosan 0-tól kezdődik
            if first_silence_start <= SILENCE_THRESHOLD + 1:
                # Keressük meg a hozzá tartozó silence_end-et
                for silence_end in silence_ends:
                    end_val = float(silence_end)
                    if end_val > first_silence_start:
                        end_of_first_silence = end_val
                        silence_duration = end_of_first_silence - first_silence_start
                        # Ha a szünet hosszabb mint a küszöbérték, távolítsuk el
                        if silence_duration >= SILENCE_THRESHOLD:
                            start_time = end_of_first_silence
                            print(f"  Eleji szunet detektalva: {first_silence_start:.2f}s - {end_of_first_silence:.2f}s ({silence_duration:.2f}s)")
                            sys.stdout.flush()
                        break
                # Ha nem találtunk megfelelő silence_end-et, de a szünet a fájl elején van,
                # akkor is próbáljuk meg eltávolítani, ha a szünet hosszabb mint a küszöbérték
                if start_time == 0.0 and first_silence_start <= 0.5:
                    # Ha a szünet pontosan a fájl elején van, és nincs silence_end,
                    # akkor próbáljuk meg a következő silence_start-et használni
                    if len(silence_starts) > 1:
                        next_silence_start = float(silence_starts[1])
                        if next_silence_start - first_silence_start >= SILENCE_THRESHOLD:
                            start_time = next_silence_start
                            print(f"  Eleji szunet detektalva (alternativ modszer): {first_silence_start:.2f}s - {next_silence_start:.2f}s")
                            sys.stdout.flush()
        
        # Ha van végső szünet
        if silence_ends:
            last_silence_end = float(silence_ends[-1])
            # Ha a szünet a fájl végén van
            if last_silence_end > total_duration - SILENCE_THRESHOLD - 1:
                # Keressük meg a hozzá tartozó silence_start-et
                for silence_start in reversed(silence_starts):
                    if float(silence_start) < last_silence_end:
                        start_of_last_silence = float(silence_start)
                        if last_silence_end - start_of_last_silence >= SILENCE_THRESHOLD:
                            end_time = start_of_last_silence
                        break
        
        print("  Szunet detektalas befejezve")
        sys.stdout.flush()
        return (start_time, end_time)
    except subprocess.TimeoutExpired:
        print(f"  Figyelmeztetes: Szunet detektalas tul lassu volt (timeout), egyszerubb modszert hasznalunk")
        sys.stdout.flush()
        return (None, None)
    except Exception as e:
        print(f"  Figyelmeztetes: Nem sikerult detektalni a szuneteket: {str(e)[:100]}")
        sys.stdout.flush()
        return (None, None)

def remove_silence_with_filter(input_file, output_file, timeout_seconds):
    """
    Eltávolítja az eleji és végső szüneteket silenceremove filterrel
    (gyorsabb mint teljes újraencodeolás)
    """
    temp_reversed = output_file.parent / f"temp_reversed_{output_file.name}"
    try:
        # Silenceremove filter: először az eleji szüneteket távolítjuk el,
        # aztán megfordítjuk, eltávolítjuk a végső szüneteket, majd visszafordítjuk
        
        # Először az eleji szüneteket távolítjuk el
        print("  Eleji szunetek eltavolitasa...")
        sys.stdout.flush()
        cmd1 = [
            'ffmpeg',
            '-i', str(input_file),
            '-af', f'silenceremove=start_periods=1:start_duration={SILENCE_THRESHOLD}:start_threshold=-50dB:detection=peak',
            '-c:a', 'copy',  # Copy codec ha lehet (gyorsabb)
            '-y',
            str(temp_reversed)
        ]
        
        try:
            result1 = subprocess.run(cmd1,
                                  capture_output=True,
                                  check=True,
                                  encoding='utf-8',
                                  errors='ignore',
                                  timeout=timeout_seconds)
        except:
            # Ha copy codec nem működik, újraencodeoljuk
            cmd1 = [
                'ffmpeg',
                '-i', str(input_file),
                '-af', f'silenceremove=start_periods=1:start_duration={SILENCE_THRESHOLD}:start_threshold=-50dB:detection=peak',
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-y',
                str(temp_reversed)
            ]
            result1 = subprocess.run(cmd1,
                                  capture_output=True,
                                  check=True,
                                  encoding='utf-8',
                                  errors='ignore',
                                  timeout=timeout_seconds)
        
        # Most megfordítjuk, eltávolítjuk a végső szüneteket (amik most az elején vannak), majd visszafordítjuk
        print("  Vegso szunetek eltavolitasa...")
        sys.stdout.flush()
        cmd2 = [
            'ffmpeg',
            '-i', str(temp_reversed),
            '-af', f'areverse,silenceremove=start_periods=1:start_duration={SILENCE_THRESHOLD}:start_threshold=-50dB:detection=peak,areverse',
            '-c:a', 'libopus',
            '-b:a', '128k',
            '-y',
            str(output_file)
        ]
        
        result2 = subprocess.run(cmd2,
                               capture_output=True,
                               check=True,
                               encoding='utf-8',
                               errors='ignore',
                               timeout=timeout_seconds)
        
        # Töröljük az ideiglenes fájlt
        if temp_reversed.exists():
            temp_reversed.unlink()
        
        print("  Szunetek eltavolitva (silenceremove filterrel)!")
        sys.stdout.flush()
        return True
    except Exception as e:
        if temp_reversed.exists():
            temp_reversed.unlink()
        print(f"  Hiba a silenceremove filterrel: {str(e)[:100]}")
        sys.stdout.flush()
        return False

def remove_silence_from_file(input_file, output_file):
    """
    Eltávolítja a szüneteket (több mint 4 mp) a fájl elejéről és végéről
    
    Args:
        input_file: Bemeneti fájl útvonala
        output_file: Kimeneti fájl útvonala
    
    Returns:
        True ha sikeres, False ha nem
    """
    # Először megkapjuk a fájl hosszát
    print("  Fajl hosszanak meghatarozasa...")
    sys.stdout.flush()
    
    try:
        cmd_duration = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(input_file)
        ]
        result_dur = subprocess.run(cmd_duration, 
                                  capture_output=True, 
                                  check=True,
                                  text=True,
                                  encoding='utf-8',
                                  errors='ignore',
                                  timeout=30)
        file_duration = float(result_dur.stdout.strip())
        print(f"  Fajl hossza: {file_duration:.2f} masodperc")
        sys.stdout.flush()
    except Exception as e:
        print(f"  Hiba a fajl hosszanak meghatarozasa soran: {str(e)[:100]}")
        sys.stdout.flush()
        return False
    
    timeout_seconds = max(300, int(file_duration * 2))
    
    # Mivel szünet mindig van, közvetlenül a silenceremove filtert használjuk
    # (gyorsabb mint a detektálás + vágás kombinációja)
    print("  Eleji es vegso szunetek eltavolitasa silenceremove filterrel...")
    sys.stdout.flush()
    
    return remove_silence_with_filter(input_file, output_file, timeout_seconds)

def concatenate_files(file_list, output_file):
    """
    Összefűzi a fájlokat egybe
    
    Args:
        file_list: Fájlok listája
        output_file: Kimeneti fájl útvonala
    
    Returns:
        True ha sikeres, False ha nem
    """
    try:
        # Létrehozunk egy ideiglenes fájllistát az ffmpeg concat demuxer számára
        base_dir = Path(output_file).parent
        filelist_path = base_dir / 'temp_filelist.txt'
        
        # Fájllista írása
        with open(filelist_path, 'w', encoding='utf-8') as f:
            for file_path in file_list:
                # Abszolút útvonalat használunk és escape-eljük az aposztrofokat
                abs_path = Path(file_path).resolve()
                f.write(f"file '{abs_path}'\n")
        
        # Összefűzés az ffmpeg concat demuxer-rel
        print("  Fajlok osszefuzese folyamatban...")
        sys.stdout.flush()
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(filelist_path),
            '-c', 'copy',  # Copy codec, gyorsabb mint újraencodeolni
            '-y',
            str(output_file)
        ]
        
        # Számoljuk ki a timeout-ot a fájlok összes hossza alapján
        total_duration = 0
        try:
            for file_path in file_list:
                cmd_duration = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(file_path)
                ]
                result_dur = subprocess.run(cmd_duration, 
                                          capture_output=True, 
                                          check=True,
                                          text=True,
                                          encoding='utf-8',
                                          errors='ignore',
                                          timeout=30)
                total_duration += float(result_dur.stdout.strip())
            timeout_seconds = max(300, int(total_duration * 2))
        except:
            timeout_seconds = 600
        
        result = subprocess.run(cmd, 
                      capture_output=True, 
                      check=True,
                      encoding='utf-8',
                      errors='ignore',
                      timeout=timeout_seconds)
        
        print("  Fajlok osszefuzve!")
        sys.stdout.flush()
        
        # Töröljük az ideiglenes fájllistát
        if filelist_path.exists():
            filelist_path.unlink()
        
        return True
    except subprocess.TimeoutExpired:
        print("  Hiba: Az osszefuzes tul lassu volt (timeout)")
        sys.stdout.flush()
        if filelist_path.exists():
            filelist_path.unlink()
        return False
    except subprocess.CalledProcessError as e:
        error_msg = ''
        if e.stderr:
            if isinstance(e.stderr, bytes):
                error_msg = e.stderr.decode('utf-8', errors='ignore')
            else:
                error_msg = str(e.stderr)
        else:
            error_msg = str(e)
        print(f"Hiba a fajlok osszefuzese soran: {error_msg[:200]}")
        sys.stdout.flush()
        # Töröljük az ideiglenes fájllistát hiba esetén is
        if filelist_path.exists():
            filelist_path.unlink()
        return False

def convert_to_mp3(input_file, output_file, bitrate=128):
    """
    Konvertálja a fájlt MP3-ra a megadott bitrate-tel
    
    Args:
        input_file: Bemeneti fájl útvonala
        output_file: Kimeneti MP3 fájl útvonala
        bitrate: Audio bitrate kbps-ben (alapértelmezett: 128)
    
    Returns:
        True ha sikeres, False ha nem
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            '-b:a', f'{bitrate}k',
            '-y',  # Felülírja a kimeneti fájlt ha létezik
            str(output_file)
        ]
        
        # Számoljuk ki a timeout-ot
        try:
            cmd_duration = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(input_file)
            ]
            result_dur = subprocess.run(cmd_duration, 
                                      capture_output=True, 
                                      check=True,
                                      text=True,
                                      encoding='utf-8',
                                      errors='ignore',
                                      timeout=30)
            file_duration = float(result_dur.stdout.strip())
            timeout_seconds = max(300, int(file_duration * 3))
        except:
            timeout_seconds = 600
        
        result = subprocess.run(cmd, 
                      capture_output=True, 
                      check=True,
                      encoding='utf-8',
                      errors='ignore',
                      timeout=timeout_seconds)
        return True
    except subprocess.TimeoutExpired:
        print(f"  Hiba: A konverzio tul lassu volt (timeout)")
        sys.stdout.flush()
        return False
    except subprocess.CalledProcessError as e:
        error_msg = ''
        if e.stderr:
            if isinstance(e.stderr, bytes):
                error_msg = e.stderr.decode('utf-8', errors='ignore')
            else:
                error_msg = str(e.stderr)
        else:
            error_msg = str(e)
        print(f"Hiba a konverzio soran: {error_msg[:200]}")
        sys.stdout.flush()
        return False

def convert_with_size_limit(input_file, output_file):
    """
    Konvertálja a fájlt MP3-ra 32 kbps bitrate-tel
    
    Args:
        input_file: Bemeneti fájl útvonala
        output_file: Kimeneti MP3 fájl útvonala
    """
    # Mindig 32 kbps bitrate-et használunk
    bitrate = 32
    
    print(f"MP3 konverzio {bitrate} kbps bitrate-tel...")
    sys.stdout.flush()
    
    if convert_to_mp3(input_file, output_file, bitrate):
        file_size = get_file_size(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"Konvertalva! Fajlmeret: {file_size_mb:.2f} MB")
        sys.stdout.flush()
        
        if file_size <= MAX_FILE_SIZE_BYTES:
            print(f"[OK] Sikeres! A fajl merete ({file_size_mb:.2f} MB) kisebb mint {MAX_FILE_SIZE_MB} MB.")
            sys.stdout.flush()
            return True
        else:
            print(f"[FIGYELMEZTETES] A fajl meg mindig tul nagy ({file_size_mb:.2f} MB) a {bitrate} kbps bitrate-tel.")
            print(f"   Ellenorizd a kimeneti fajlt: {output_file}")
            sys.stdout.flush()
            return False
    else:
        print(f"[FIGYELMEZTETES] Hiba tortent a {bitrate} kbps bitrate-tel valo konverzio soran.")
        sys.stdout.flush()
        return False

def main():
    """Fő függvény"""
    print("="*60)
    print("WebM fájlok összeállító script")
    print("="*60)
    print()
    sys.stdout.flush()
    
    # Ellenőrizzük az ffmpeg telepítését
    print("Ellenőrzés: FFmpeg telepítve van-e...")
    sys.stdout.flush()
    
    if not check_ffmpeg():
        print("[HIBA] Az ffmpeg nincs telepítve vagy nem található!")
        print("Telepítsd az ffmpeg-et a webm_to_mp3.py script segítségével vagy manuálisan.")
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
    
    # Fájlok keresése: 1.webm, 2.webm, esetleg 3.webm
    file1 = mp3_dir / '1.webm'
    file2 = mp3_dir / '2.webm'
    file3 = mp3_dir / '3.webm'
    
    input_files = []
    if file1.exists():
        input_files.append(file1)
        print(f"[OK] Megtalalva: {file1.name}")
    else:
        print(f"[HIBA] A {file1.name} fajl nem talalhato!")
        sys.stdout.flush()
        sys.exit(1)
    
    if file2.exists():
        input_files.append(file2)
        print(f"[OK] Megtalalva: {file2.name}")
    else:
        print(f"[INFO] A {file2.name} fajl nem talalhato, csak 1 fajlt fogunk feldolgozni.")
    
    if file3.exists():
        input_files.append(file3)
        print(f"[OK] Megtalalva: {file3.name}")
    else:
        print(f"[INFO] A {file3.name} fajl nem talalhato, csak 2 fajlt fogunk osszeallitani.")
    
    sys.stdout.flush()
    
    print(f"\nOsszesen {len(input_files)} fajl lesz osszeallitva.")
    print()
    
    # Lépés 1: Szünetek eltávolítása minden fájlból
    print("="*60)
    print("Lepes 1: Szunetek eltavolitasa...")
    print("="*60)
    sys.stdout.flush()
    
    processed_files = []
    temp_dir = mp3_dir / 'temp_processed'
    temp_dir.mkdir(exist_ok=True)
    
    for i, input_file in enumerate(input_files, 1):
        print(f"\nFeldolgozas: {input_file.name}")
        sys.stdout.flush()
        
        temp_output = temp_dir / f"processed_{i}.webm"
        
        if remove_silence_from_file(input_file, temp_output):
            print(f"[OK] Szunetek eltavolitva: {input_file.name}")
            processed_files.append(temp_output)
        else:
            print(f"[HIBA] Nem sikerult eltavolitani a szuneteket: {input_file.name}")
            sys.stdout.flush()
            # Töröljük az ideiglenes mappát (ha lehet)
            import shutil
            import time
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except (PermissionError, OSError):
                    # Ha nem sikerül, nem baj, csak figyelmeztetünk
                    print(f"[FIGYELMEZTETES] Nem sikerult torolni az ideiglenes mappat: {temp_dir}")
                    sys.stdout.flush()
            sys.exit(1)
    
    # Lépés 2: Fájlok összefűzése
    print(f"\n{'='*60}")
    print("Lepes 2: Fajlok osszefuzese...")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    concatenated_file = temp_dir / 'concatenated.webm'
    
    if concatenate_files(processed_files, concatenated_file):
        print("[OK] Fajlok sikeresen osszefuzve!")
        sys.stdout.flush()
    else:
        print("[HIBA] Nem sikerult osszefuzni a fajlokat!")
        sys.stdout.flush()
        # Töröljük az ideiglenes mappát
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        sys.exit(1)
    
    # Lépés 3: MP3-re konvertálás méretkorláttal
    final_webm = concatenated_file
    
    print(f"\n{'='*60}")
    print("Lepes 3: MP3 konverzio (max {MAX_FILE_SIZE_MB} MB)...")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    output_file = mp3_dir / 'osszeallitott.mp3'
    
    # Ha már létezik az MP3 fájl, töröljük
    if output_file.exists():
        print(f"[FIGYELMEZTETES] A {output_file.name} mar letezik, felulirjuk...")
        sys.stdout.flush()
        output_file.unlink()
    
    success = convert_with_size_limit(final_webm, output_file)
    
    # Töröljük az ideiglenes fájlokat
    print(f"\n{'='*60}")
    print("Ideiglenes fajlok torlese...")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    import shutil
    import time
    if temp_dir.exists():
        # Próbáljuk meg törölni, ha nem sikerül, várunk egy kicsit és újrapróbáljuk
        max_retries = 5
        for retry in range(max_retries):
            try:
                shutil.rmtree(temp_dir)
                print("[OK] Ideiglenes fajlok torolve!")
                break
            except PermissionError:
                if retry < max_retries - 1:
                    print(f"  Varakozas a fajlok felszabadulasara... ({retry + 1}/{max_retries})")
                    sys.stdout.flush()
                    time.sleep(1)  # Várunk 1 másodpercet
                else:
                    print("[FIGYELMEZTETES] Nem sikerult torolni az ideiglenes fajlokat, de a script sikeresen befejezodott.")
                    print(f"  Manuálisan torold ki: {temp_dir}")
                    sys.stdout.flush()
            except Exception as e:
                print(f"[FIGYELMEZTETES] Hiba az ideiglenes fajlok torlese soran: {str(e)[:100]}")
                sys.stdout.flush()
                break
    
    if success:
        file_size = get_file_size(output_file)
        file_size_mb = file_size / (1024 * 1024)
        print(f"\n{'='*60}")
        print("Sikeresen befejezve!")
        print(f"{'='*60}")
        print(f"Kimeneti fajl: {output_file.name}")
        print(f"Fajlmeret: {file_size_mb:.2f} MB")
        print(f"{'='*60}")
        sys.stdout.flush()
    else:
        print(f"\n{'='*60}")
        print("Befejezve, de ellenorizd a kimeneti fajlt!")
        print(f"{'='*60}")
        print(f"Kimeneti fajl: {output_file.name}")
        sys.stdout.flush()

if __name__ == '__main__':
    main()

