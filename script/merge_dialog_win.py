#!/usr/bin/env python3
"""
Dialógus összefésülő szkript (Windows verzió).
Betölti a tanuló (1.mp4) és mentor (2.mp4) hangfelvételeket,
felismeri a 5 mp-es szüneteket, kivágja a blokkokat,
és váltakozva összeilleszti őket (tanuló 1, mentor 1, tanuló 2, mentor 2, ...).
A szüneteket eltávolítja, hogy gördülékeny dialógus legyen.
A fájl elején lévő szünetből 1.5 mp maradhat.
"""

import os
import subprocess
import argparse
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def detect_blocks_ffmpeg(audio_file, silence_thresh=-50.0, min_silence_len=5000, verbose=False):
    """
    FFmpeg-gel felismeri a hangblokkokat egy audio fájlban.
    Pontosan 5 mp-es szüneteket használ blokkok elválasztására.
    Eltávolítja a fájl elején és végén lévő szüneteket.
    
    Args:
        audio_file: Audio fájl elérési útja
        silence_thresh: Csend küszöbérték dB-ben (alapértelmezett -50 dB)
        min_silence_len: Minimális csend hossz ms-ben (5000ms = 5 mp)
        verbose: Ha True, részletes progress jelzéseket ír ki
    
    Returns:
        Lista a blokkokról [(start_ms, end_ms), ...] - szünetek nélkül
    """
    if verbose:
        print("    FFmpeg csend detektálás folyamatban...")
    
    # FFmpeg paranccsal szünetek észlelése
    cmd = [
        'ffmpeg',
        '-i', str(audio_file),
        '-af', f'silencedetect=noise={silence_thresh}dB:d={min_silence_len/1000}',
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=False
        )
        
        # Szünetek kinyerése a stderr-ből - UTF-8 encoding
        silence_starts = []
        silence_ends = []
        
        if result.stderr is None:
            if verbose:
                print("    Hiba: FFmpeg nem adott vissza kimenetet")
            return []
        
        stderr_text = result.stderr.decode('utf-8', errors='ignore')
        
        for line in stderr_text.split('\n'):
            if 'silence_start' in line:
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
        
        # Fájl hosszának meghatározása
        duration_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_file)
        ]
        duration_result = subprocess.run(
            duration_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            if duration_result.stdout is None:
                return []
            stdout_text = duration_result.stdout.decode('utf-8', errors='ignore')
            duration = float(stdout_text.strip()) * 1000  # ms
        except:
            return []
        
        # Ha nincs szünet, az egész fájl egy blokk
        if not silence_starts:
            return [(0, duration)]
        
        # Nem szünetes részek meghatározása
        # Csak azokat a szüneteket vesszük figyelembe, amelyek legalább 4.8 mp hosszúak (5 mp ± 0.2 mp tolerancia)
        blocks = []
        current_start = 0
        
        # Rendezzük a szüneteket és szűrjük a túl rövid szüneteket
        valid_silences = []
        for silence_start, silence_end in zip(silence_starts, silence_ends):
            silence_duration = silence_end - silence_start
            # Csak azokat a szüneteket vesszük figyelembe, amelyek legalább 4.8 mp hosszúak
            if silence_duration >= min_silence_len * 0.96:  # 4.8 mp = 4800ms
                valid_silences.append((silence_start, silence_end))
        
        # Ha nincs érvényes szünet, az egész fájl egy blokk
        if not valid_silences:
            return [(0, duration)]
        
        # Rendezzük az érvényes szüneteket
        all_silences = sorted(valid_silences)
        
        # A fájl elején lévő szünetet eltávolítjuk - az első blokk a szünet végénél kezdődik
        # De ha a szünet hosszabb mint 5 mp, akkor csak 1.5 mp-t hagyjunk meg
        if all_silences:
            first_silence_start, first_silence_end = all_silences[0]
            # Ha a szünet a fájl elején kezdődik (vagy nagyon közel az elejéhez)
            if first_silence_start < 1000:  # Ha a szünet az első 1 mp-ben kezdődik
                silence_duration = first_silence_end - first_silence_start
                # Ha a szünet hosszabb mint 5 mp, akkor csak 1.5 mp-t hagyjunk meg
                if silence_duration > 5000:  # Ha a szünet hosszabb mint 5 mp
                    current_start = first_silence_start + 1500  # 1.5 mp után kezdjük
                else:
                    # Ha rövidebb vagy egyenlő 5 mp-nél, teljesen eltávolítjuk (mint az eredeti scriptben)
                    current_start = first_silence_end  # A szünet végén kezdjük - teljes eltávolítás
                all_silences = all_silences[1:]
        
        for silence_start, silence_end in all_silences:
            if current_start < silence_start:
                # A blokk vége pontosan a szünet kezdeténél van - teljes szünet eltávolítása
                block_start = max(0, current_start)
                block_end = silence_start  # Pontosan a szünet kezdeténél
                if block_end > block_start:  # Csak ha van tartalom
                    blocks.append((block_start, block_end))
            # A következő blokk kezdete pontosan a szünet végénél van - teljes szünet eltávolítása
            current_start = silence_end  # Pontosan a szünet végénél
        
        # Utolsó rész hozzáadása, ha van (de csak ha nem szünet a végén)
        if current_start < duration:
            # Ha a fájl végén szünet van, ne vegyük bele
            last_silence_end = all_silences[-1][1] if all_silences else 0
            if current_start > last_silence_end or not all_silences:
                block_start = max(0, current_start)
                block_end = duration
                if block_end > block_start:  # Csak ha van tartalom
                    blocks.append((block_start, block_end))
        
        return blocks if blocks else []
        
    except Exception as e:
        if verbose:
            print(f"    Hiba: {str(e)}")
        return []


def detect_blocks(audio, silence_thresh=-50.0, min_silence_len=5000, verbose=False):
    """
    Felismeri a hangblokkokat egy audio fájlban.
    Pontosan 5 mp-es szüneteket használ blokkok elválasztására.
    Eltávolítja a fájl elején és végén lévő szüneteket.
    
    Args:
        audio: AudioSegment objektum
        silence_thresh: Csend küszöbérték dB-ben (alapértelmezett -50 dB)
        min_silence_len: Minimális csend hossz ms-ben (5000ms = 5 mp)
        verbose: Ha True, részletes progress jelzéseket ír ki
    
    Returns:
        Lista a blokkokról [(start_ms, end_ms), ...] - szünetek nélkül
    """
    if verbose:
        print("    Mono-ra konvertálás...")
    # Mono-ra konvertálás a csend detektáláshoz
    if audio.channels > 1:
        audio_mono = audio.set_channels(1)
    else:
        audio_mono = audio
    
    if verbose:
        print("    Csend detektálás folyamatban (ez eltarthat egy ideig)...")
    total_length = len(audio_mono)
    silence_thresh_linear = audio_mono.max_possible_amplitude * (10 ** (silence_thresh / 20))
    
    # Lépésenként haladunk végig - 100ms-es chunkokkal
    chunk_size = 100  # 100ms-es chunkok
    blocks = []
    current_block_start = None
    consecutive_silence = 0
    last_sound_pos = 0
    
    # Progress jelzés
    last_progress = 0
    
    for i in range(0, total_length, chunk_size):
        # Progress jelzés minden 10%-nál (csak verbose módban)
        if verbose:
            progress = int((i / total_length) * 100)
            if progress >= last_progress + 10:
                print(f"    {progress}%...", end="", flush=True)
                last_progress = progress
        
        chunk_end = min(i + chunk_size, total_length)
        chunk = audio_mono[i:chunk_end]
        
        if len(chunk) == 0:
            break
        
        # Ellenőrizzük, hogy csend van-e
        is_silent = chunk.rms < silence_thresh_linear
        
        if is_silent:
            consecutive_silence += len(chunk)
            
            # Ha elértük a 5 mp-es csend hosszát, blokk vége
            if consecutive_silence >= min_silence_len and current_block_start is not None:
                # Blokk vége az utolsó hang pozíciójánál
                blocks.append((current_block_start, last_sound_pos))
                current_block_start = None
                consecutive_silence = 0
        else:
            # Van hang
            if current_block_start is None:
                # Új blokk kezdete
                current_block_start = i
            last_sound_pos = chunk_end
            consecutive_silence = 0
    
    if verbose:
        print(" 100%")
    
    # Utolsó blokk hozzáadása, ha van (csak ha nem szünet a végén)
    if current_block_start is not None:
        blocks.append((current_block_start, last_sound_pos))
    
    return blocks


def trim_leading_trailing_silence_aggressive(audio, silence_thresh=-50.0):
    """
    Agresszíven eltávolítja a vezető és záró csendet egy audio blokkból.
    Az első blokkoknál használjuk, hogy ne maradjon szünet közöttük.
    
    Args:
        audio: AudioSegment objektum
        silence_thresh: Csend küszöbérték dB-ben
    
    Returns:
        Trimmed AudioSegment
    """
    if audio.channels > 1:
        audio_mono = audio.set_channels(1)
    else:
        audio_mono = audio
    
    silence_thresh_linear = audio_mono.max_possible_amplitude * (10 ** (silence_thresh / 20))
    
    # Vezető csend keresése - agresszív
    start_trim = 0
    for i in range(0, min(len(audio_mono), 3000), 50):  # Első 3 mp részletes ellenőrzése
        chunk = audio_mono[i:i+50]
        if len(chunk) == 0:
            break
        
        if chunk.rms < silence_thresh_linear:
            start_trim = i + 50
        else:
            break
    
    # Záró csend keresése - agresszív
    end_trim = len(audio)
    for i in range(len(audio_mono), max(0, len(audio_mono) - 3000), -50):  # Utolsó 3 mp részletes ellenőrzése
        chunk_start = max(0, i - 50)
        chunk = audio_mono[chunk_start:i]
        if len(chunk) == 0:
            break
        
        if chunk.rms < silence_thresh_linear:
            end_trim = chunk_start
        else:
            break
    
    return audio[start_trim:end_trim]


def trim_trailing_silence_only(audio, silence_thresh=-50.0):
    """
    Eltávolítja csak a záró csendet egy audio blokkból (mint az eredeti scriptben).
    Az elejét nem vágja, mert az már pontosan a szünet végénél van vágva.
    Az utolsó 2 mp-ben keresi a szüneteket és eltávolítja őket.
    
    Args:
        audio: AudioSegment objektum
        silence_thresh: Csend küszöbérték dB-ben
    
    Returns:
        Trimmed AudioSegment
    """
    if audio.channels > 1:
        audio_mono = audio.set_channels(1)
    else:
        audio_mono = audio
    
    silence_thresh_linear = audio_mono.max_possible_amplitude * (10 ** (silence_thresh / 20))
    
    # Záró csend keresése - részletesebb ellenőrzés (mint az eredeti scriptben)
    end_trim = len(audio)
    for i in range(len(audio_mono), max(0, len(audio_mono) - 2000), -50):  # Utolsó 2 mp részletes ellenőrzése
        chunk_start = max(0, i - 50)
        chunk = audio_mono[chunk_start:i]
        if len(chunk) == 0:
            break
        
        if chunk.rms < silence_thresh_linear:
            end_trim = chunk_start
        else:
            break
    
    return audio[:end_trim]


def merge_dialog_files(tanulo_file, mentor_file, output_file, tanulo_block_count=None, mentor_block_count=None):
    """
    Összefésüli a tanuló és mentor hangfelvételeket váltakozva.
    
    Args:
        tanulo_file: Tanuló hangfájl elérési útja
        mentor_file: Mentor hangfájl elérési útja
        output_file: Kimeneti MP3 fájl elérési útja
    """
    print(f"Betöltés: {tanulo_file.name}")
    tanulo_audio = AudioSegment.from_file(str(tanulo_file), format="mp4")
    print(f"  Tanuló hossz: {len(tanulo_audio) / 1000:.2f} mp")
    
    print(f"Betöltés: {mentor_file.name}")
    mentor_audio = AudioSegment.from_file(str(mentor_file), format="mp4")
    print(f"  Mentor hossz: {len(mentor_audio) / 1000:.2f} mp")
    
    # Blokkok felismerése - FFmpeg-gel pontosan 5 mp-es szüneteket keresünk
    print("\nBlokkok felismerése...")
    print("  Tanuló fájl feldolgozása...")
    
    # Ha megadták a blokkok számát, használjuk azt
    target_tanulo_blocks = tanulo_block_count if tanulo_block_count is not None else None
    
    # FFmpeg-gel blokkok felismerése
    print("    FFmpeg csend detektálás folyamatban (ez eltarthat egy ideig)...")
    tanulo_blocks = detect_blocks_ffmpeg(tanulo_file, silence_thresh=-50.0, min_silence_len=5000, verbose=True)
    
    # Ha megadták a cél blokkszámot és nem egyezik, próbáljuk meg finomítani (csak ha a különbség <= 2)
    if target_tanulo_blocks is not None and len(tanulo_blocks) != target_tanulo_blocks:
        diff = abs(len(tanulo_blocks) - target_tanulo_blocks)
        if diff <= 2:  # Csak akkor próbálkozzunk, ha a különbség kicsi
            print(f"    Talált: {len(tanulo_blocks)} blokk, cél: {target_tanulo_blocks} blokk, finomítás (max 3 próbálkozás)...")
            best_blocks = tanulo_blocks
            best_diff = diff
            tries = 0
            max_tries = 3
            
            # Csak néhány gyors próbálkozás
            for silence_thresh in [-50, -45]:
                if len(tanulo_blocks) == target_tanulo_blocks or tries >= max_tries:
                    break
                for min_silence in [4800, 5000, 5200]:  # Csak 3 érték
                    if len(tanulo_blocks) == target_tanulo_blocks or tries >= max_tries:
                        break
                    tries += 1
                    blocks = detect_blocks_ffmpeg(tanulo_file, silence_thresh=silence_thresh, min_silence_len=min_silence, verbose=False)
                    current_diff = abs(len(blocks) - target_tanulo_blocks)
                    if len(blocks) == target_tanulo_blocks:
                        tanulo_blocks = blocks
                        print(f"    Talált: {len(tanulo_blocks)} blokk (próbálkozás {tries}/{max_tries})")
                        break
                    elif current_diff < best_diff:
                        best_blocks = blocks
                        best_diff = current_diff
            
            if len(tanulo_blocks) != target_tanulo_blocks:
                tanulo_blocks = best_blocks
                print(f"    Legközelebbi: {len(tanulo_blocks)} blokk (cél: {target_tanulo_blocks}, {tries} próbálkozás)")
        else:
            print(f"    Talált: {len(tanulo_blocks)} blokk, cél: {target_tanulo_blocks} blokk (különbség: {diff}, túl nagy, finomítás kihagyva)")
    
    if len(tanulo_blocks) == 0:
        print("    Nem találtunk blokkot, az egész fájlt egy blokknak kezeljük...")
        tanulo_blocks = [(0, len(tanulo_audio))]
    
    print(f"    Végleges: {len(tanulo_blocks)} blokk")
    
    print("  Mentor fájl feldolgozása...")
    
    # Ha megadták a blokkok számát, használjuk azt
    target_mentor_blocks = mentor_block_count if mentor_block_count is not None else None
    
    # Ugyanaz a logika a mentor fájlhoz
    print("    FFmpeg csend detektálás folyamatban (ez eltarthat egy ideig)...")
    mentor_blocks = detect_blocks_ffmpeg(mentor_file, silence_thresh=-50.0, min_silence_len=5000, verbose=True)
    
    # Ha megadták a cél blokkszámot és nem egyezik, próbáljuk meg finomítani (csak ha a különbség <= 2)
    if target_mentor_blocks is not None and len(mentor_blocks) != target_mentor_blocks:
        diff = abs(len(mentor_blocks) - target_mentor_blocks)
        if diff <= 2:  # Csak akkor próbálkozzunk, ha a különbség kicsi
            print(f"    Talált: {len(mentor_blocks)} blokk, cél: {target_mentor_blocks} blokk, finomítás (max 3 próbálkozás)...")
            best_blocks = mentor_blocks
            best_diff = diff
            tries = 0
            max_tries = 3
            
            # Csak néhány gyors próbálkozás
            for silence_thresh in [-50, -45]:
                if len(mentor_blocks) == target_mentor_blocks or tries >= max_tries:
                    break
                for min_silence in [4800, 5000, 5200]:  # Csak 3 érték
                    if len(mentor_blocks) == target_mentor_blocks or tries >= max_tries:
                        break
                    tries += 1
                    blocks = detect_blocks_ffmpeg(mentor_file, silence_thresh=silence_thresh, min_silence_len=min_silence, verbose=False)
                    current_diff = abs(len(blocks) - target_mentor_blocks)
                    if len(blocks) == target_mentor_blocks:
                        mentor_blocks = blocks
                        print(f"    Talált: {len(mentor_blocks)} blokk (próbálkozás {tries}/{max_tries})")
                        break
                    elif current_diff < best_diff:
                        best_blocks = blocks
                        best_diff = current_diff
            
            if len(mentor_blocks) != target_mentor_blocks:
                mentor_blocks = best_blocks
                print(f"    Legközelebbi: {len(mentor_blocks)} blokk (cél: {target_mentor_blocks}, {tries} próbálkozás)")
        else:
            print(f"    Talált: {len(mentor_blocks)} blokk, cél: {target_mentor_blocks} blokk (különbség: {diff}, túl nagy, finomítás kihagyva)")
    
    
    if len(mentor_blocks) == 0:
        print("    Nem találtunk blokkot, az egész fájlt egy blokknak kezeljük...")
        mentor_blocks = [(0, len(mentor_audio))]
    
    print(f"    Végleges: {len(mentor_blocks)} blokk")
    
    print(f"\n  Tanuló blokkok száma: {len(tanulo_blocks)}")
    for i, (start, end) in enumerate(tanulo_blocks[:5], 1):  # Csak az első 5-öt mutatjuk
        print(f"    Blokk {i}: {start/1000:.2f}s - {end/1000:.2f}s ({(end-start)/1000:.2f}s)")
    if len(tanulo_blocks) > 5:
        print(f"    ... és még {len(tanulo_blocks) - 5} blokk")
    
    print(f"  Mentor blokkok száma: {len(mentor_blocks)}")
    for i, (start, end) in enumerate(mentor_blocks[:5], 1):  # Csak az első 5-öt mutatjuk
        print(f"    Blokk {i}: {start/1000:.2f}s - {end/1000:.2f}s ({(end-start)/1000:.2f}s)")
    if len(mentor_blocks) > 5:
        print(f"    ... és még {len(mentor_blocks) - 5} blokk")
    
    # Blokkok számának ellenőrzése
    if len(tanulo_blocks) != len(mentor_blocks):
        print(f"\n⚠ FIGYELMEZTETÉS: A blokkok száma nem egyezik!")
        print(f"  Tanuló: {len(tanulo_blocks)} blokk")
        print(f"  Mentor: {len(mentor_blocks)} blokk")
        
        # Ha a különbség kicsi, próbáljuk meg igazítani
        if abs(len(tanulo_blocks) - len(mentor_blocks)) <= 3:
            print(f"  A különbség kicsi ({abs(len(tanulo_blocks) - len(mentor_blocks))} blokk), folytatás a minimális számmal...")
        else:
            print(f"  A különbség nagyobb ({abs(len(tanulo_blocks) - len(mentor_blocks))} blokk), lehet hogy probléma van a detektálásban!")
            print(f"  Folytatás a minimális számmal, de ellenőrizd az eredményt!")
    
    # Ha a blokkok száma nem egyezik, próbáljuk meg intelligensen igazítani
    if len(tanulo_blocks) != len(mentor_blocks):
        print("\nBlokkok számának igazítása...")
        print(f"  Tanuló: {len(tanulo_blocks)} blokk")
        print(f"  Mentor: {len(mentor_blocks)} blokk")
        
        # Cél: a két fájl blokkjainak száma közel legyen egymáshoz
        # Használjuk a középértéket, de ha a különbség nagy, akkor a kisebbet
        target_count = min(len(tanulo_blocks), len(mentor_blocks))
        
        # Ha a különbség kicsi (1-2 blokk), akkor a kisebbet használjuk
        # Ha nagyobb, akkor próbáljuk meg eltávolítani a legrövidebb blokkokat
        if abs(len(tanulo_blocks) - len(mentor_blocks)) > 2:
            print(f"  Nagy különbség detektálva, igazítás a {target_count} blokkra...")
            
            # Ha több blokk van, eltávolítjuk a legrövidebbeket
            if len(tanulo_blocks) > target_count:
                print(f"    Tanuló: {len(tanulo_blocks)} -> {target_count} blokk")
                # Rendezzük hossz szerint és tartsuk meg a leghosszabbakat
                tanulo_blocks_with_length = [(end-start, start, end) for start, end in tanulo_blocks]
                tanulo_blocks_with_length.sort(reverse=True)
                tanulo_blocks = [(start, end) for _, start, end in tanulo_blocks_with_length[:target_count]]
                tanulo_blocks.sort(key=lambda x: x[0])  # Időrend szerint rendezés
            
            if len(mentor_blocks) > target_count:
                print(f"    Mentor: {len(mentor_blocks)} -> {target_count} blokk")
                # Rendezzük hossz szerint és tartsuk meg a leghosszabbakat
                mentor_blocks_with_length = [(end-start, start, end) for start, end in mentor_blocks]
                mentor_blocks_with_length.sort(reverse=True)
                mentor_blocks = [(start, end) for _, start, end in mentor_blocks_with_length[:target_count]]
                mentor_blocks.sort(key=lambda x: x[0])  # Időrend szerint rendezés
        else:
            print(f"  Kicsi különbség ({abs(len(tanulo_blocks) - len(mentor_blocks))} blokk), folytatás a minimális számmal")
    
    # Blokkok időrendi rendezése (biztonsági okokból)
    tanulo_blocks = sorted(tanulo_blocks, key=lambda x: x[0])
    mentor_blocks = sorted(mentor_blocks, key=lambda x: x[0])
    
    # Váltakozva összeillesztés
    print("\nBlokkok összeillesztése...")
    merged_audio = AudioSegment.empty()
    min_blocks = min(len(tanulo_blocks), len(mentor_blocks))
    
    print(f"  Összeillesztés {min_blocks} blokk párral...")
    print(f"  Sorrend: Tanuló 1 → Mentor 1 → Tanuló 2 → Mentor 2 → ...")
    
    for i in range(min_blocks):
        # Tanuló blokk
        tanulo_start, tanulo_end = tanulo_blocks[i]
        tanulo_block = tanulo_audio[tanulo_start:tanulo_end]
        
        # Az első blokknál agresszívabban vágjuk le a végét, hogy ne maradjon szünet
        if i == 0:
            # Az első blokknál mindkét oldalról vágjuk le a szüneteket agresszíven
            tanulo_block = trim_leading_trailing_silence_aggressive(tanulo_block)
        else:
            # A többi blokknál csak a végét vágjuk le
            tanulo_block = trim_trailing_silence_only(tanulo_block)
        
        if (i + 1) % 10 == 0 or i < 5:  # Minden 10. blokknál és az első 5-nél
            print(f"  [{i+1}/{min_blocks}] Tanuló blokk ({len(tanulo_block)/1000:.2f}s)")
        merged_audio += tanulo_block
        
        # Mentor blokk
        mentor_start, mentor_end = mentor_blocks[i]
        mentor_block = mentor_audio[mentor_start:mentor_end]
        
        # Az első blokknál agresszívabban vágjuk le az elejét, hogy ne maradjon szünet a tanuló után
        if i == 0:
            # Az első blokknál mindkét oldalról vágjuk le a szüneteket agresszíven
            mentor_block = trim_leading_trailing_silence_aggressive(mentor_block)
        else:
            # A többi blokknál csak a végét vágjuk le
            mentor_block = trim_trailing_silence_only(mentor_block)
        
        if (i + 1) % 10 == 0 or i < 5:  # Minden 10. blokknál és az első 5-nél
            print(f"  [{i+1}/{min_blocks}] Mentor blokk ({len(mentor_block)/1000:.2f}s)")
        merged_audio += mentor_block
    
    # Ha több blokk van az egyik fájlban, hozzáadjuk a maradékot
    if len(tanulo_blocks) > len(mentor_blocks):
        print(f"\nHozzáadás {len(tanulo_blocks) - len(mentor_blocks)} extra tanuló blokk...")
        for i in range(len(mentor_blocks), len(tanulo_blocks)):
            start, end = tanulo_blocks[i]
            block = tanulo_audio[start:end]
            block = trim_trailing_silence_only(block)
            merged_audio += block
    
    elif len(mentor_blocks) > len(tanulo_blocks):
        print(f"\nHozzáadás {len(mentor_blocks) - len(tanulo_blocks)} extra mentor blokk...")
        for i in range(len(tanulo_blocks), len(mentor_blocks)):
            start, end = mentor_blocks[i]
            block = mentor_audio[start:end]
            block = trim_trailing_silence_only(block)
            merged_audio += block
    
    # MP3 exportálás
    print(f"\nExportálás MP3 formátumba: {output_file.name}")
    print(f"  Végleges hossz: {len(merged_audio) / 1000:.2f} mp")
    
    merged_audio.export(
        str(output_file),
        format="mp3",
        bitrate="128k"
    )
    
    output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"  Fájlméret: {output_size_mb:.2f} MB")
    print(f"  ✓ Kész!\n")


def main():
    """Fő függvény."""
    parser = argparse.ArgumentParser(
        description='Dialógus összefésülő szkript (Windows verzió)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Példa használat:
  python script/merge_dialog_win.py
  python script/merge_dialog_win.py --tanulo-blokkok 22 --mentor-blokkok 21
        """
    )
    parser.add_argument(
        '--tanulo-blokkok',
        type=int,
        default=None,
        help='A tanuló fájlban lévő blokkok száma (opcionális, gyorsítja a folyamatot)'
    )
    parser.add_argument(
        '--mentor-blokkok',
        type=int,
        default=None,
        help='A mentor fájlban lévő blokkok száma (opcionális, gyorsítja a folyamatot)'
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    mp3_dir = project_root / "MP3"
    
    tanulo_file = mp3_dir / "1.mp4"
    mentor_file = mp3_dir / "2.mp4"
    
    if not tanulo_file.exists():
        print(f"Hiba: {tanulo_file.name} nem található az MP3 mappában!")
        print(f"  Kereselt útvonal: {tanulo_file}")
        return
    
    if not mentor_file.exists():
        print(f"Hiba: {mentor_file.name} nem található az MP3 mappában!")
        print(f"  Kereselt útvonal: {mentor_file}")
        return
    
    output_file = mp3_dir / "merged_dialog.mp3"
    
    print("="*60)
    print("DIALÓGUS ÖSSZEFÉSÜLŐ SZKRIPT")
    print("="*60)
    if args.tanulo_blokkok is not None or args.mentor_blokkok is not None:
        print(f"Megadott blokkszámok:")
        if args.tanulo_blokkok is not None:
            print(f"  Tanuló: {args.tanulo_blokkok} blokk")
        if args.mentor_blokkok is not None:
            print(f"  Mentor: {args.mentor_blokkok} blokk")
        print()
    
    merge_dialog_files(tanulo_file, mentor_file, output_file, args.tanulo_blokkok, args.mentor_blokkok)
    
    print("="*60)
    print("KÉSZ!")
    print("="*60)


if __name__ == "__main__":
    main()

