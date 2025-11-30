#!/usr/bin/env python3
"""
Dialógus összefésülő szkript.
Betölti a tanuló (1.mov) és mentor (2.mov) hangfelvételeket,
felismeri a 5 mp-es szüneteket, kivágja a blokkokat,
és váltakozva összeilleszti őket (tanuló 1, mentor 1, tanuló 2, mentor 2, ...).
A szüneteket eltávolítja, hogy gördülékeny dialógus legyen.
"""

import os
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def detect_blocks(audio, silence_thresh=-50.0, min_silence_len=4800, verbose=False):
    """
    Felismeri a hangblokkokat egy audio fájlban.
    A 5 mp-es (vagy hosszabb) szüneteket használja blokkok elválasztására.
    Gyors, egyedi algoritmus, ami lépésenként halad végig.
    
    Args:
        audio: AudioSegment objektum
        silence_thresh: Csend küszöbérték dB-ben (alapértelmezett -50 dB)
        min_silence_len: Minimális csend hossz ms-ben (4800ms = 4.8 mp)
        verbose: Ha True, részletes progress jelzéseket ír ki
    
    Returns:
        Lista a blokkokról [(start_ms, end_ms), ...]
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
    
    # Lépésenként haladunk végig - 500ms-es chunkokkal (gyorsabb)
    chunk_size = 500  # 500ms-es chunkok
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
            
            # Ha elértük a minimális csend hosszát, blokk vége
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
    
    # Utolsó blokk hozzáadása, ha van
    if current_block_start is not None:
        blocks.append((current_block_start, last_sound_pos))
    
    # Ha nincs blokk, az egész fájl egy blokk
    if not blocks:
        return [(0, total_length)]
    
    return blocks


def trim_leading_trailing_silence(audio, silence_thresh=-50.0):
    """
    Eltávolítja a vezető és záró csendet egy audio blokkból.
    
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
    
    # Vezető csend keresése - részletesebb ellenőrzés
    start_trim = 0
    silence_thresh_linear = audio_mono.max_possible_amplitude * (10 ** (silence_thresh / 20))
    
    for i in range(0, min(len(audio_mono), 2000), 50):  # Első 2 mp részletes ellenőrzése
        chunk = audio_mono[i:i+50]
        if len(chunk) == 0:
            break
        
        if chunk.rms < silence_thresh_linear:
            start_trim = i + 50
        else:
            break
    
    # Záró csend keresése - részletesebb ellenőrzés
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
    
    return audio[start_trim:end_trim]


def merge_dialog_files(tanulo_file, mentor_file, output_file):
    """
    Összefésüli a tanuló és mentor hangfelvételeket váltakozva.
    
    Args:
        tanulo_file: Tanuló hangfájl elérési útja
        mentor_file: Mentor hangfájl elérési útja
        output_file: Kimeneti MP3 fájl elérési útja
    """
    print(f"Betöltés: {tanulo_file.name}")
    tanulo_audio = AudioSegment.from_file(str(tanulo_file), format="mov")
    print(f"  Tanuló hossz: {len(tanulo_audio) / 1000:.2f} mp")
    
    print(f"Betöltés: {mentor_file.name}")
    mentor_audio = AudioSegment.from_file(str(mentor_file), format="mov")
    print(f"  Mentor hossz: {len(mentor_audio) / 1000:.2f} mp")
    
    # Blokkok felismerése - többféle paraméterrel próbálkozunk, hogy megtaláljuk a legjobb detektálást
    print("\nBlokkok felismerése...")
    print("  Tanuló fájl feldolgozása...")
    
    # Próbáljuk meg többféle paraméterrel - keressük a legjobb egyensúlyt
    # Tágabb tartomány: lehet, hogy a szünetek rövidebbek vagy hosszabbak
    tanulo_candidates = []
    for min_silence in [3000, 3500, 4000, 4200, 4500, 4800, 5000, 5200, 5500, 6000, 6500]:
        blocks = detect_blocks(tanulo_audio, min_silence_len=min_silence, verbose=False)
        if len(blocks) > 0:
            # Számoljuk az átlagos blokk hosszát
            avg_length = sum(end - start for start, end in blocks) / len(blocks)
            # Számoljuk a minimális blokk hosszát is
            min_length = min(end - start for start, end in blocks)
            tanulo_candidates.append({
                'blocks': blocks,
                'count': len(blocks),
                'min_silence': min_silence,
                'avg_length': avg_length,
                'min_length': min_length
            })
    
    # Válasszuk ki a legjobbat: preferáljuk a több blokkot (minél több, annál jobb, ha ésszerű hosszúságúak)
    tanulo_blocks = None
    best_score = -1
    for candidate in tanulo_candidates:
        # Szűrés: túl rövid blokkokat ne fogadjuk el
        if candidate['min_length'] < 500:  # 0.5 mp-nél rövidebb blokk = valószínűleg hiba
            continue
        if candidate['avg_length'] < 1000:  # Átlagosan 1 mp-nél rövidebb = rossz
            continue
        if candidate['count'] < 10:  # Túl kevés blokk = rossz
            continue
        
        # Pontszám: preferáljuk a több blokkot (minél több, annál jobb, de max 60-ig)
        # és az ésszerű átlagos hosszúságot (3-15 mp között)
        count_score = min(100, candidate['count'] * 2)  # Több blokk = jobb pontszám
        if candidate['count'] > 60:  # Túl sok blokk = rossz
            count_score = 100 - (candidate['count'] - 60) * 2
        
        # Hosszúság pontszám: 3-15 mp között optimális
        if 3000 <= candidate['avg_length'] <= 15000:
            length_score = 100
        elif candidate['avg_length'] < 3000:
            length_score = (candidate['avg_length'] / 3000) * 100
        else:
            length_score = max(0, 100 - ((candidate['avg_length'] - 15000) / 1000) * 10)
        
        score = count_score * 0.7 + length_score * 0.3  # Több súly a blokkszámra
        
        if score > best_score:
            best_score = score
            tanulo_blocks = candidate['blocks']
    
    if tanulo_blocks is None:
        # Ha nem találtunk jó megoldást, használjuk az alapértelmezettet
        tanulo_blocks = detect_blocks(tanulo_audio, verbose=True)
    
    print(f"    Választott: {len(tanulo_blocks)} blokk (min_silence: {[c['min_silence'] for c in tanulo_candidates if c['blocks'] == tanulo_blocks][0] if tanulo_blocks in [c['blocks'] for c in tanulo_candidates] else 'N/A'}ms)")
    
    print("  Mentor fájl feldolgozása...")
    
    # Ugyanaz a logika a mentor fájlhoz
    mentor_candidates = []
    for min_silence in [3000, 3500, 4000, 4200, 4500, 4800, 5000, 5200, 5500, 6000, 6500]:
        blocks = detect_blocks(mentor_audio, min_silence_len=min_silence, verbose=False)
        if len(blocks) > 0:
            avg_length = sum(end - start for start, end in blocks) / len(blocks)
            min_length = min(end - start for start, end in blocks)
            mentor_candidates.append({
                'blocks': blocks,
                'count': len(blocks),
                'min_silence': min_silence,
                'avg_length': avg_length,
                'min_length': min_length
            })
    
    mentor_blocks = None
    best_score = -1
    for candidate in mentor_candidates:
        if candidate['min_length'] < 500:
            continue
        if candidate['avg_length'] < 1000:
            continue
        if candidate['count'] < 10:
            continue
        
        count_score = min(100, candidate['count'] * 2)
        if candidate['count'] > 60:
            count_score = 100 - (candidate['count'] - 60) * 2
        
        if 3000 <= candidate['avg_length'] <= 15000:
            length_score = 100
        elif candidate['avg_length'] < 3000:
            length_score = (candidate['avg_length'] / 3000) * 100
        else:
            length_score = max(0, 100 - ((candidate['avg_length'] - 15000) / 1000) * 10)
        
        score = count_score * 0.7 + length_score * 0.3
        
        if score > best_score:
            best_score = score
            mentor_blocks = candidate['blocks']
    
    if mentor_blocks is None:
        mentor_blocks = detect_blocks(mentor_audio, verbose=True)
    
    print(f"    Választott: {len(mentor_blocks)} blokk (min_silence: {[c['min_silence'] for c in mentor_candidates if c['blocks'] == mentor_blocks][0] if mentor_blocks in [c['blocks'] for c in mentor_candidates] else 'N/A'}ms)")
    
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
        tanulo_block = trim_leading_trailing_silence(tanulo_block)
        
        if (i + 1) % 10 == 0 or i < 5:  # Minden 10. blokknál és az első 5-nél
            print(f"  [{i+1}/{min_blocks}] Tanuló blokk ({len(tanulo_block)/1000:.2f}s)")
        merged_audio += tanulo_block
        
        # Mentor blokk - közvetlenül a tanuló után, szünet nélkül
        mentor_start, mentor_end = mentor_blocks[i]
        mentor_block = mentor_audio[mentor_start:mentor_end]
        mentor_block = trim_leading_trailing_silence(mentor_block)
        
        if (i + 1) % 10 == 0 or i < 5:  # Minden 10. blokknál és az első 5-nél
            print(f"  [{i+1}/{min_blocks}] Mentor blokk ({len(mentor_block)/1000:.2f}s)")
        merged_audio += mentor_block
    
    # Ha több blokk van az egyik fájlban, hozzáadjuk a maradékot
    if len(tanulo_blocks) > len(mentor_blocks):
        print(f"\nHozzáadás {len(tanulo_blocks) - len(mentor_blocks)} extra tanuló blokk...")
        for i in range(len(mentor_blocks), len(tanulo_blocks)):
            start, end = tanulo_blocks[i]
            block = tanulo_audio[start:end]
            block = trim_leading_trailing_silence(block)
            merged_audio += block
    
    elif len(mentor_blocks) > len(tanulo_blocks):
        print(f"\nHozzáadás {len(mentor_blocks) - len(tanulo_blocks)} extra mentor blokk...")
        for i in range(len(tanulo_blocks), len(mentor_blocks)):
            start, end = mentor_blocks[i]
            block = mentor_audio[start:end]
            block = trim_leading_trailing_silence(block)
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
    script_dir = Path(__file__).parent
    
    tanulo_file = script_dir / "1.mov"
    mentor_file = script_dir / "2.mov"
    
    if not tanulo_file.exists():
        print(f"Hiba: {tanulo_file.name} nem található!")
        return
    
    if not mentor_file.exists():
        print(f"Hiba: {mentor_file.name} nem található!")
        return
    
    output_file = script_dir / "merged_dialog.mp3"
    
    print("="*60)
    print("DIALÓGUS ÖSSZEFÉSÜLŐ SZKRIPT")
    print("="*60)
    print()
    
    merge_dialog_files(tanulo_file, mentor_file, output_file)
    
    print("="*60)
    print("KÉSZ!")
    print("="*60)


if __name__ == "__main__":
    main()

