"""
MP4 fájlok feldolgozása MP3-vá:
- 2 mp-nél hosszabb szünetek törlése (elején, végén, közben)
- 32 kbps bitrate formázás
- Max 7MB méret
"""

import os
import glob
import subprocess
import tempfile
import json
import shutil

def detect_silences_ffmpeg(input_file, min_silence_len=2000, silence_thresh=-50):
    """
    FFmpeg-gel észleli a szüneteket és visszaadja a nem szünetes részeket.
    
    Args:
        input_file: Bemeneti audio fájl
        min_silence_len: Minimum szünet hossz milliszekundumban (2000 ms = 2 mp)
        silence_thresh: Szünet küszöbérték dB-ben
    
    Returns:
        Lista a nem szünetes tartományokról [(start_ms, end_ms), ...]
    """
    # FFmpeg paranccsal szünetek észlelése
    # silencedetect filter használata
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-af', f'silencedetect=noise={silence_thresh}dB:d={min_silence_len/1000}',
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Szünetek kinyerése a stderr-ből
        silence_starts = []
        silence_ends = []
        
        for line in result.stderr.split('\n'):
            if 'silence_start' in line:
                # Formátum: silence_start: 5.234
                try:
                    time_str = line.split('silence_start:')[1].strip().split()[0]
                    silence_starts.append(float(time_str) * 1000)  # ms-re konvertálás
                except:
                    pass
            elif 'silence_end' in line:
                try:
                    time_str = line.split('silence_end:')[1].strip().split()[0]
                    silence_ends.append(float(time_str) * 1000)
                except:
                    pass
        
        # Ha nincs szünet, az egész fájl hangos
        if not silence_starts:
            # Fájl hosszának meghatározása
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_file
            ]
            duration_result = subprocess.run(
                duration_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                duration = float(duration_result.stdout.strip()) * 1000
                return [(0, duration)]
            except:
                return [(0, 0)]
        
        # Nem szünetes részek meghatározása
        nonsilent_ranges = []
        current_start = 0
        
        # Rendezzük a szüneteket
        all_silences = sorted(zip(silence_starts, silence_ends))
        
        for silence_start, silence_end in all_silences:
            if current_start < silence_start:
                nonsilent_ranges.append((current_start, silence_start))
            current_start = max(current_start, silence_end)
        
        # Utolsó rész hozzáadása, ha van
        duration_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        duration_result = subprocess.run(
            duration_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            duration = float(duration_result.stdout.strip()) * 1000
            if current_start < duration:
                nonsilent_ranges.append((current_start, duration))
        except:
            pass
        
        return nonsilent_ranges if nonsilent_ranges else [(0, 0)]
        
    except Exception as e:
        print(f"  - Hiba a szünetek észlelésekor: {str(e)}")
        # Ha hiba van, az egész fájlt visszaadjuk
        return None


def remove_long_silences_ffmpeg(input_file, output_file, min_silence_len=2000, silence_thresh=-50, bitrate=32):
    """
    FFmpeg-gel törli a 2 mp-nél hosszabb szüneteket.
    
    Args:
        input_file: Bemeneti fájl
        output_file: Kimeneti fájl
        min_silence_len: Minimum szünet hossz ms-ben
        silence_thresh: Szünet küszöbérték dB-ben
        bitrate: Bitrate kbps-ben
    """
    # Szünetek észlelése
    nonsilent_ranges = detect_silences_ffmpeg(input_file, min_silence_len, silence_thresh)
    
    if not nonsilent_ranges:
        # Ha nincs hang, egy rövid csendet hozunk létre
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-t', '0.1',
            '-c:a', 'libmp3lame',
            '-b:a', '32k',
            '-y',
            output_file
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return
    
    # Ha csak egy tartomány van és az az egész fájl, egyszerűen másoljuk
    if len(nonsilent_ranges) == 1:
        start_ms, end_ms = nonsilent_ranges[0]
        start_sec = start_ms / 1000
        duration = (end_ms - start_ms) / 1000
        
        # Fájl hosszának ellenőrzése
        duration_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        duration_result = subprocess.run(
            duration_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            total_duration = float(duration_result.stdout.strip())
            if start_sec == 0 and duration >= total_duration * 0.99:
                # Az egész fájl hangos, csak konvertáljuk (minőségi beállításokkal)
                cmd = [
                    'ffmpeg',
                    '-i', input_file,
                    '-c:a', 'libmp3lame',
                    '-b:a', f'{bitrate}k',  # CBR fix bitrate
                    '-ar', '22050',  # Sample rate normalizálás (32 kbps-nél ideális)
                    '-ac', '1',  # Mono (beszédhez elég, kisebb fájlméret)
                    '-y',
                    output_file
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                return
        except:
            pass
    
    # Több rész esetén összefűzzük őket
    # WAV formátumban dolgozunk, majd csak a végén konvertáljuk MP3-vá (megbízhatóbb)
    temp_files = []
    try:
        for i, (start_ms, end_ms) in enumerate(nonsilent_ranges):
            start_sec = start_ms / 1000
            duration = (end_ms - start_ms) / 1000
            
            # Temp fájl neve számozott sorrendben (WAV formátum)
            temp_file = os.path.join(tempfile.gettempdir(), f"audio_part_{i:04d}.wav")
            temp_files.append(temp_file)
            
            # Rész kivágása WAV formátumban (pontos vágás, sample rate normalizálás)
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-ss', str(start_sec),
                '-t', str(duration),
                '-acodec', 'pcm_s16le',
                '-ar', '22050',  # Sample rate normalizálás (32 kbps-nél ideális)
                '-ac', '1',  # Mono (beszédhez elég, kisebb fájlméret)
                '-y',
                temp_file
            ]
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=False
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else str(result.returncode)
                raise Exception(f"FFmpeg vágás hiba rész {i+1}: {error_msg[:200]}")
        
        # Fájlok összefűzése
        if len(temp_files) == 1:
            # Ellenőrizzük, hogy a temp fájl létezik-e
            if not os.path.exists(temp_files[0]):
                raise Exception(f"Temp fájl nem található: {temp_files[0]}")
            
            # Ha csak egy rész van, közvetlenül MP3-vá konvertáljuk (minőségi beállításokkal)
            cmd = [
                'ffmpeg',
                '-i', temp_files[0],
                '-c:a', 'libmp3lame',
                '-b:a', f'{bitrate}k',  # CBR fix bitrate
                '-ar', '22050',  # Sample rate normalizálás (32 kbps-nél ideális)
                '-ac', '1',  # Mono (beszédhez elég, kisebb fájlméret)
                '-y',
                output_file
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else str(result.returncode)
                # Teljes hibaüzenet kiírása
                print(f"FFmpeg parancs: {' '.join(cmd)}")
                print(f"FFmpeg hibaüzenet: {error_msg}")
                raise Exception(f"FFmpeg MP3 konverzió hiba: {error_msg}")
        else:
            # Ellenőrizzük, hogy minden temp fájl létezik-e
            for temp_file in temp_files:
                if not os.path.exists(temp_file):
                    raise Exception(f"Temp fájl nem található: {temp_file}")
            
            # Concat fájl létrehozása WAV fájlokhoz
            concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
            concat_path = concat_file.name
            
            for temp_file in temp_files:
                # Abszolút útvonal normalizálva
                abs_path = os.path.abspath(temp_file)
                # Windows path-ot forward slash-ra konvertáljuk
                abs_path_normalized = abs_path.replace('\\', '/')
                # Escape-eljük az apostrofokat és speciális karaktereket
                abs_path_escaped = abs_path_normalized.replace("'", "'\\''")
                concat_file.write(f"file '{abs_path_escaped}'\n")
            
            concat_file.close()
            
            # Először összefűzzük WAV formátumban
            temp_merged = os.path.join(tempfile.gettempdir(), "audio_merged.wav")
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_path,
                '-c', 'copy',
                '-y',
                temp_merged
            ]
            
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=False
            )
            
            if result.returncode != 0:
                # Ha a copy nem működik, újrakódoljuk
                cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_path,
                    '-acodec', 'pcm_s16le',
                    '-ar', '22050',  # Sample rate normalizálás
                    '-ac', '1',  # Mono
                    '-af', 'volume=1.0',  # Hangerő normalizálás az összefűzésnél
                    '-y',
                    temp_merged
                ]
                result = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=False
                )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else str(result.returncode)
                # Teljes hibaüzenet kiírása
                print(f"FFmpeg concat parancs: {' '.join(cmd)}")
                print(f"FFmpeg concat hibaüzenet: {error_msg}")
                # Concat fájl tartalmának kiírása debug céljából
                if os.path.exists(concat_path):
                    with open(concat_path, 'r', encoding='utf-8') as f:
                        print(f"Concat fájl tartalma:\n{f.read()}")
                os.remove(concat_path)
                raise Exception(f"FFmpeg concat hiba: {error_msg}")
            
            os.remove(concat_path)
            
            # Most MP3-vá konvertáljuk (minőségi beállításokkal)
            cmd = [
                'ffmpeg',
                '-i', temp_merged,
                '-c:a', 'libmp3lame',
                '-b:a', f'{bitrate}k',  # CBR fix bitrate
                '-ar', '22050',  # Sample rate normalizálás (32 kbps-nél ideális)
                '-ac', '1',  # Mono (beszédhez elég, kisebb fájlméret)
                '-y',
                output_file
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else str(result.returncode)
                # Teljes hibaüzenet kiírása
                print(f"FFmpeg parancs: {' '.join(cmd)}")
                print(f"FFmpeg hibaüzenet: {error_msg}")
                if os.path.exists(temp_merged):
                    os.remove(temp_merged)
                raise Exception(f"FFmpeg MP3 konverzió hiba: {error_msg}")
            
            if os.path.exists(temp_merged):
                os.remove(temp_merged)
        
        # Temp fájlok törlése
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
                
    except Exception as e:
        # Temp fájlok törlése hiba esetén
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        if 'temp_merged' in locals() and os.path.exists(temp_merged):
            try:
                os.remove(temp_merged)
            except:
                pass
        raise e


def process_mp4_to_mp3(input_file, output_file, target_bitrate=32, max_size_mb=7):
    """
    MP4 fájl feldolgozása MP3-vá:
    - Szünetek törlése (2 mp-nél hosszabb, elején, végén, közben)
    - 32 kbps bitrate (fix)
    - Max 7MB méret (tájékoztató)
    
    Args:
        input_file: Bemeneti MP4 fájl útvonala
        output_file: Kimeneti MP3 fájl útvonala
        target_bitrate: Cél bitrate kbps-ben (alapértelmezett: 16)
        max_size_mb: Maximális fájlméret MB-ban (tájékoztató)
    """
    print(f"Feldolgozás: {os.path.basename(input_file)}")
    
    try:
        # Eredeti fájl hosszának meghatározása
        duration_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        duration_result = subprocess.run(
            duration_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            original_duration = float(duration_result.stdout.strip())
            print(f"  - Eredeti hossz: {original_duration:.2f} másodperc")
        except:
            print("  - Eredeti hossz: ismeretlen")
        
        # Szünetek törlése és MP3 konverzió fix 16 kbps bitrate-tel
        print("  - Szünetek törlése (2 mp-nél hosszabb)...")
        
        # Szünetek törlése és konverzió 16 kbps bitrate-tel
        remove_long_silences_ffmpeg(
            input_file, 
            output_file, 
            min_silence_len=2000, 
            silence_thresh=-50,
            bitrate=target_bitrate
        )
        
        if not os.path.exists(output_file):
            raise Exception("A konverzió nem hozott létre fájlt")
        
        # Fájlméret ellenőrzése (csak tájékoztató)
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  - Bitrate: {target_bitrate} kbps")
        print(f"  - Fájlméret: {file_size_mb:.2f} MB", end="")
        if file_size_mb > max_size_mb:
            print(f" (FIGYELEM: meghaladja a {max_size_mb} MB-ot)")
        else:
            print(" (OK)")
        
        # Feldolgozott fájl hosszának meghatározása
        try:
            duration_result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    output_file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processed_duration = float(duration_result.stdout.strip())
            print(f"")
            print(f"  - Feldolgozott hossz: {processed_duration:.2f} másodperc")
        except:
            pass
        
        print(f"  - Kész: {os.path.basename(output_file)}")
            
    except subprocess.CalledProcessError as e:
        print(f"  - HIBA: FFmpeg hiba: {str(e)}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"  - Részletek: {e.stderr.decode('utf-8', errors='ignore')[:200]}")
        raise
    except Exception as e:
        print(f"  - HIBA: {str(e)}")
        raise


def check_ffmpeg():
    """Ellenőrzi, hogy FFmpeg telepítve van-e"""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Főprogram: MP3 mappában lévő összes MP4 fájl feldolgozása"""
    
    # FFmpeg ellenőrzése
    if not check_ffmpeg():
        print("HIBA: FFmpeg nincs telepítve vagy nem elérhető!")
        print("Kérjük, telepítse az FFmpeg-et: https://ffmpeg.org/download.html")
        print("Telepítés után győződjön meg róla, hogy az FFmpeg a PATH-ban van.")
        return
    
    # MP3 mappa útvonala
    mp3_folder = "MP3"
    
    if not os.path.exists(mp3_folder):
        print(f"HIBA: A '{mp3_folder}' mappa nem található!")
        return
    
    # Összes MP4 fájl keresése
    mp4_files = glob.glob(os.path.join(mp3_folder, "*.mp4"))
    
    if not mp4_files:
        print(f"Nincs MP4 fájl a '{mp3_folder}' mappában.")
        return
    
    print(f"{len(mp4_files)} MP4 fájl található.")
    print("-" * 60)
    
    # Minden MP4 fájl feldolgozása
    for mp4_file in mp4_files:
        # Kimeneti fájl neve (MP3 kiterjesztéssel)
        base_name = os.path.splitext(os.path.basename(mp4_file))[0]
        mp3_file = os.path.join(mp3_folder, f"{base_name}.mp3")
        
        # Ha már létezik az MP3 fájl, kérdezzük meg, hogy felülírjuk-e
        if os.path.exists(mp3_file):
            response = input(f"\nA '{os.path.basename(mp3_file)}' már létezik. Felülírja? (i/n): ")
            if response.lower() != 'i':
                print("  - Kihagyva.")
                continue
        
        try:
            process_mp4_to_mp3(mp4_file, mp3_file, target_bitrate=32, max_size_mb=7)
            print()
        except Exception as e:
            print(f"  - A feldolgozás sikertelen: {str(e)}\n")
            continue
    
    print("-" * 60)
    print("Feldolgozás befejezve!")


if __name__ == "__main__":
    main()
