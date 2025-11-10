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
            # Ha a szünet a fájl elején van (0-hoz közel)
            if first_silence_start < SILENCE_THRESHOLD + 1:
                # Keressük meg a hozzá tartozó silence_end-et
                for silence_end in silence_ends:
                    if float(silence_end) > first_silence_start:
                        end_of_first_silence = float(silence_end)
                        if end_of_first_silence - first_silence_start >= SILENCE_THRESHOLD:
                            start_time = end_of_first_silence
                        break
        
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
    
    # Detektáljuk az összes szünetet és vágjuk ki őket
    print("  Osszes szunet detektalasa (4 mp-nel hosszabb)...")
    sys.stdout.flush()
    
    # Detektáljuk az összes szünetet
    all_silences = detect_all_silences(input_file)
    
    if all_silences and len(all_silences) > 0:
        print(f"  {len(all_silences)} szunet talalva")
        sys.stdout.flush()
        
        # Számoljuk ki a fájl hosszát
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
        total_duration = float(result_dur.stdout.strip())
        
        # Számoljuk ki a szegmenseket (a szünetek között)
        segments = []
        current_start = 0.0
        MIN_SEGMENT_DURATION = 0.5  # Minimum 0.5 másodperc szegmens hosszúság
        
        for silence_start, silence_end in sorted(all_silences):
            # Ha van hanganyag a jelenlegi pozíció és a szünet között
            if current_start < silence_start:
                seg_duration = silence_start - current_start
                # Csak akkor adjuk hozzá, ha elég hosszú (nem csak zaj)
                if seg_duration >= MIN_SEGMENT_DURATION:
                    segments.append((current_start, silence_start))
                else:
                    print(f"  Figyelmeztetes: Tul rovid szegmens kihagyva: {current_start:.2f}s - {silence_start:.2f}s ({seg_duration:.2f}s)")
                    sys.stdout.flush()
            current_start = silence_end
        
        # Utolsó szegmens (az utolsó szünet után)
        if current_start < total_duration:
            seg_duration = total_duration - current_start
            # Csak akkor adjuk hozzá, ha elég hosszú
            if seg_duration >= MIN_SEGMENT_DURATION:
                segments.append((current_start, total_duration))
            else:
                print(f"  Figyelmeztetes: Tul rovid vegso szegmens kihagyva: {current_start:.2f}s - {total_duration:.2f}s ({seg_duration:.2f}s)")
                sys.stdout.flush()
        
        if len(segments) == 0:
            print("  Figyelmeztetes: Nincs eleg hosszu hanganyag szegmens a szunetek utan")
            sys.stdout.flush()
            return False
        
        print(f"  {len(segments)} szegmens lesz osszefuzve")
        sys.stdout.flush()
        
        # Vágjuk ki a szegmenseket és fűzzük össze
        temp_dir = output_file.parent / 'temp_segments'
        temp_dir.mkdir(exist_ok=True)
        
        segment_files = []
        for i, (seg_start, seg_end) in enumerate(segments):
            seg_duration = seg_end - seg_start
            if seg_duration <= 0:
                continue
                
            seg_file = temp_dir / f"segment_{i:03d}.webm"
            print(f"  Szegmens {i+1}/{len(segments)}: {seg_start:.2f}s - {seg_end:.2f}s")
            sys.stdout.flush()
            
            # Vágjuk ki a szegmenst
            cmd = [
                'ffmpeg',
                '-ss', str(seg_start),
                '-i', str(input_file),
                '-t', str(seg_duration),
                '-c', 'copy',  # Copy codec, gyors
                '-y',
                str(seg_file)
            ]
            
            try:
                subprocess.run(cmd,
                             capture_output=True,
                             check=True,
                             encoding='utf-8',
                             errors='ignore',
                             timeout=30)
                segment_files.append(seg_file)
            except:
                # Ha copy codec nem működik, újraencodeoljuk
                cmd = [
                    'ffmpeg',
                    '-ss', str(seg_start),
                    '-i', str(input_file),
                    '-t', str(seg_duration),
                    '-c:a', 'libopus',
                    '-b:a', '128k',
                    '-y',
                    str(seg_file)
                ]
                subprocess.run(cmd,
                             capture_output=True,
                             check=True,
                             encoding='utf-8',
                             errors='ignore',
                             timeout=timeout_seconds)
                segment_files.append(seg_file)
        
        if len(segment_files) == 0:
            print("  Hiba: Nem sikerult szegmenseket letrehozni")
            sys.stdout.flush()
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False
        
        # Összefűzzük a szegmenseket
        print("  Szegmensek osszefuzese...")
        sys.stdout.flush()
        
        # Létrehozzuk a fájllistát
        filelist_path = temp_dir / 'filelist.txt'
        with open(filelist_path, 'w', encoding='utf-8') as f:
            for seg_file in segment_files:
                abs_path = Path(seg_file).resolve()
                f.write(f"file '{abs_path}'\n")
        
        # Összefűzés
        cmd_concat = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(filelist_path),
            '-c', 'copy',
            '-y',
            str(output_file)
        ]
        
        try:
            subprocess.run(cmd_concat,
                         capture_output=True,
                         check=True,
                         encoding='utf-8',
                         errors='ignore',
                         timeout=timeout_seconds)
        except:
            # Ha copy codec nem működik, újraencodeoljuk
            cmd_concat = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(filelist_path),
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-y',
                str(output_file)
            ]
            subprocess.run(cmd_concat,
                         capture_output=True,
                         check=True,
                         encoding='utf-8',
                         errors='ignore',
                         timeout=timeout_seconds)
        
        # Töröljük az ideiglenes fájlokat
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        print("  Szunetek kivagva es szegmensek osszefuzve!")
        sys.stdout.flush()
        return True
    
    # Ha nem találtunk szüneteket, próbáljuk meg a régi módszert
    print("  Nem talalhato szunet, regi modszer probalasa...")
    sys.stdout.flush()
    
    # Detektáljuk a szüneteket (csak eleji és végső)
    start_time, end_time = detect_silence(input_file)
    
    if start_time is not None and end_time is not None and start_time < end_time:
        # Ha sikerült detektálni, vágjuk pontosan
        duration = end_time - start_time
        if duration > 0 and duration < file_duration:
            print(f"  Szunetek detektalva: kezdet {start_time:.2f}s, veg {end_time:.2f}s")
            print(f"  Vagas: {start_time:.2f}s - {end_time:.2f}s ({duration:.2f}s)")
            sys.stdout.flush()
            
            # Próbáljuk meg copy codec-cel először (ha csak audio van)
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', str(input_file),
                '-t', str(duration),
                '-map', '0:a',  # Csak audio
                '-c:a', 'copy',  # Copy codec
                '-vn',
                '-y',
                str(output_file)
            ]
            
            try:
                result = subprocess.run(cmd,
                                      capture_output=True,
                                      check=True,
                                      encoding='utf-8',
                                      errors='ignore',
                                      timeout=30)
                print("  Szunetek eltavolitva (copy codec, pontos vagas)!")
                sys.stdout.flush()
                return True
            except:
                # Ha copy codec nem működik, újraencodeoljuk
                pass
            
            # Újraencodeolás gyors codec-cel
            print("  Copy codec nem mukodott, ujraencodeolas gyors codec-cel...")
            sys.stdout.flush()
            
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', str(input_file),
                '-t', str(duration),
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-y',
                str(output_file)
            ]
            
            try:
                result = subprocess.run(cmd,
                                      capture_output=True,
                                      check=True,
                                      encoding='utf-8',
                                      errors='ignore',
                                      timeout=timeout_seconds)
                print("  Szunetek eltavolitva (ujraencodeolas, pontos vagas)!")
                sys.stdout.flush()
                return True
            except Exception as e:
                print(f"  Vagas sikertelen: {str(e)[:100]}")
                sys.stdout.flush()
                start_time = None
        else:
            # Ha nincs szünet vagy rossz értékek, próbáljuk meg a silenceremove filtert
            start_time = None
    else:
        # Ha nem sikerült detektálni, próbáljuk meg a silenceremove filtert (egyszerűbb paraméterekkel)
        start_time = None
    
    if start_time is None:
        # Ha nem sikerült detektálni vagy vágni, próbáljuk meg a silenceremove filtert
        print("  Szunet detektalas nem sikerult, silenceremove filter probalasa...")
        sys.stdout.flush()
        
        # Silenceremove filter: először az eleji szüneteket távolítjuk el,
        # aztán megfordítjuk, eltávolítjuk a végső szüneteket, majd visszafordítjuk
        # Ez biztosítja, hogy mindkét oldalról eltávolítjuk a szüneteket
        temp_reversed = output_file.parent / f"temp_reversed_{output_file.name}"
        
        try:
            # Először az eleji szüneteket távolítjuk el
            print("  Eleji szunetek eltavolitasa...")
            sys.stdout.flush()
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
            cmd = [
                'ffmpeg',
                '-i', str(temp_reversed),
                '-af', f'areverse,silenceremove=start_periods=1:start_duration={SILENCE_THRESHOLD}:start_threshold=-50dB:detection=peak,areverse',
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-y',
                str(output_file)
            ]
            
            # Futtatjuk a második lépést
            result2 = subprocess.run(cmd,
                                   capture_output=True,
                                   check=True,
                                   encoding='utf-8',
                                   errors='ignore',
                                   timeout=timeout_seconds)
            
            # Töröljük az ideiglenes fájlt
            if temp_reversed.exists():
                temp_reversed.unlink()
            
            print("  Szunetek eltavolitva (silenceremove filterrel, mindket oldalrol)!")
            sys.stdout.flush()
            return True
                
        except Exception as e:
            # Ha a fordított módszer nem működik, próbáljuk meg csak az eleji szüneteket eltávolítani
            if temp_reversed.exists():
                temp_reversed.unlink()
            
            print("  Egyszeru silenceremove probalasa (csak eleji szunetek)...")
            sys.stdout.flush()
            
            # Egyszerűbb silenceremove paraméterek (kompatibilis az ffmpeg verzióval)
            cmd = [
                'ffmpeg',
                '-i', str(input_file),
                '-af', f'silenceremove=start_periods=1:start_duration={SILENCE_THRESHOLD}:start_threshold=-50dB:detection=peak',
                '-c:a', 'libopus',  # Gyors codec webm-hez
                '-b:a', '128k',  # Alacsony bitrate gyorsabb feldolgozásért
                '-y',
                str(output_file)
            ]
    
    try:
        result = subprocess.run(cmd,
                              capture_output=True,
                              check=True,
                              encoding='utf-8',
                              errors='ignore',
                              timeout=timeout_seconds)
        print("  Szunetek eltavolitva (silenceremove filterrel)!")
        sys.stdout.flush()
        return True
    except subprocess.TimeoutExpired:
        print("  Silenceremove filter tul lassu, masik modszert hasznalunk...")
        sys.stdout.flush()
    except subprocess.CalledProcessError as e:
        # Kiírjuk a pontos hibát debug céljából
        error_msg = ''
        if e.stderr:
            if isinstance(e.stderr, bytes):
                error_msg = e.stderr.decode('utf-8', errors='ignore')
            else:
                error_msg = str(e.stderr)
        
        # Keresünk a hibaüzenetben releváns információkat
        error_lines = error_msg.split('\n')[-10:] if error_msg else []
        relevant_error = [line for line in error_lines if any(keyword in line.lower() for keyword in ['error', 'invalid', 'cannot', 'not supported', 'codec'])]
        if relevant_error:
            print(f"  Silenceremove hiba: {relevant_error[0][:100]}")
            sys.stdout.flush()
        
        # Ha a silenceremove nem működik, próbáljuk meg másik codec-cel vagy beállításokkal
        print("  Silenceremove filter nem mukodott, alternativ modszert probalunk...")
        sys.stdout.flush()
        
        # Próbáljuk meg másik codec-cel vagy beállításokkal
        try:
            print("  Alternativ silenceremove probalasa (masik codec)...")
            sys.stdout.flush()
            
            # Próbáljuk meg másik codec-cel
            cmd = [
                'ffmpeg',
                '-i', str(input_file),
                '-af', f'silenceremove=start_periods=1:start_duration={SILENCE_THRESHOLD}:start_threshold=-50dB:detection=peak:end_periods=1:end_duration={SILENCE_THRESHOLD}:end_threshold=-50dB',
                '-c:a', 'libvorbis',  # Alternatív codec
                '-b:a', '128k',
                '-y',
                str(output_file)
            ]
            
            result = subprocess.run(cmd,
                                  capture_output=True,
                                  check=True,
                                  encoding='utf-8',
                                  errors='ignore',
                                  timeout=timeout_seconds)
            print("  Szunetek eltavolitva (alternativ codec-cel)!")
            sys.stdout.flush()
            return True
        except:
            # Ha semmi sem működik, csak újraencodeoljuk anélkül, hogy vágunk
            print("  Fallback: teljes fajl ujraencodeolasa szunetek nelkul...")
            print("  Figyelmeztetes: Ez nem fogja eltavolitani a szuneteket, csak ujraencodeolja a fajlt.")
            sys.stdout.flush()
            
            try:
                cmd = [
                    'ffmpeg',
                    '-i', str(input_file),
                    '-c:a', 'libopus',
                    '-b:a', '128k',
                    '-y',
                    str(output_file)
                ]
                
                import threading
                import time
                
                # Indítjuk az ffmpeg-et
                process = subprocess.Popen(cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         encoding='utf-8',
                                         errors='ignore')
                
                # Időzített visszajelzés
                start_time = time.time()
                progress_printed = False
                
                def print_progress():
                    nonlocal progress_printed
                    elapsed = 0
                    while process.poll() is None:
                        time.sleep(10)  # Minden 10 másodpercben
                        elapsed = int(time.time() - start_time)
                        if elapsed > 0:
                            print(f"  Még fut... ({elapsed} masodperc eltelt)")
                            sys.stdout.flush()
                            progress_printed = True
                
                progress_thread = threading.Thread(target=print_progress, daemon=True)
                progress_thread.start()
                
                # Várjuk meg a folyamat befejeződését
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                
                if process.returncode == 0:
                    if progress_printed:
                        elapsed = int(time.time() - start_time)
                        print(f"  Befejezve! ({elapsed} masodperc alatt)")
                    print("  Fajl ujraencodeolva (szunetek nelkul)!")
                    sys.stdout.flush()
                    return True
                else:
                    # Hiba esetén kiírjuk az utolsó sorokat
                    stderr_lines = stderr.split('\n') if stderr else []
                    error_output = '\n'.join(stderr_lines[-10:])
                    raise subprocess.CalledProcessError(process.returncode, cmd, stderr=error_output)
                    
            except subprocess.TimeoutExpired:
                print("  Hiba: Az ujraencodeolas tul lassu volt (timeout)")
                print(f"  A timeout {timeout_seconds} masodperc volt, de a feldolgozas nem fejezodott be.")
                sys.stdout.flush()
                return False
            except subprocess.CalledProcessError as fallback_error:
                error_str = ''
                if fallback_error.stderr:
                    if isinstance(fallback_error.stderr, bytes):
                        error_str = fallback_error.stderr.decode('utf-8', errors='ignore')
                    else:
                        error_str = str(fallback_error.stderr)
                elif fallback_error.stdout:
                    if isinstance(fallback_error.stdout, bytes):
                        error_str = fallback_error.stdout.decode('utf-8', errors='ignore')
                    else:
                        error_str = str(fallback_error.stdout)
                else:
                    error_str = str(fallback_error)
                print(f"  Fallback is sikertelen: {error_str[:300]}")
                sys.stdout.flush()
                return False
        
        print(f"Hiba a szunet eltavolitasa soran: {error_msg[:500]}")
        sys.stdout.flush()
        return False

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
    base_dir = Path(__file__).parent.parent
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
        print(f"[HIBA] A {file2.name} fajl nem talalhato!")
        sys.stdout.flush()
        sys.exit(1)
    
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
    
    # Lépés 3: Végleges szünet eltávolítása a végéről (ha van)
    print(f"\n{'='*60}")
    print("Lepes 3: Vegso szunet ellenorzese...")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    final_webm = temp_dir / 'final.webm'
    
    # Ellenőrizzük, van-e szünet a végén
    all_silences = detect_all_silences(concatenated_file)
    
    if all_silences and len(all_silences) > 0:
        # Van szünet, próbáljuk meg eltávolítani
        print("  Szunetek talalhatok, eltavolitas...")
        sys.stdout.flush()
        if remove_silence_from_file(concatenated_file, final_webm):
            print("[OK] Vegso szunet eltavolitva!")
            sys.stdout.flush()
        else:
            print("[FIGYELMEZTETES] Nem sikerult eltavolitani a vegso szuneteket, folytatjuk...")
            sys.stdout.flush()
            final_webm = concatenated_file
    else:
        # Nincs szünet, csak másoljuk a fájlt
        print("  Nincs szunet a vegere, fajl masolasa...")
        sys.stdout.flush()
        import shutil
        shutil.copy2(concatenated_file, final_webm)
        print("[OK] Fajl masolva (nincs szunet a vegere)")
        sys.stdout.flush()
    
    # Lépés 4: MP3-re konvertálás méretkorláttal
    print(f"\n{'='*60}")
    print("Lepes 4: MP3 konverzio (max {MAX_FILE_SIZE_MB} MB)...")
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

