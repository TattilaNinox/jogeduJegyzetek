#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS Dialógus Összeállító Script - FFmpeg verzió
================================================

Ez a script WEBM hangfájlokat (kérdések és válaszok) dolgoz fel FFmpeg közvetlen használatával.
Python 3.13 kompatibilis (nem igényel audioop modult).

Használat:
    python webm_dialogus_osszeallito_ffmpeg.py --kerdesek kerdesek.webm --valaszok valaszok.webm --kimenet Audio/

Követelmények:
    - FFmpeg (telepítve és PATH-ban)
    - Python 3.7+
"""

import os
import sys
import argparse
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime


class DialogusOsszeallitoLogger:
    """Egyszerű logger a folyamat követésére"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
        self.messages = []
    
    def log(self, message, level="INFO"):
        """Üzenet naplózása"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {level}: {message}"
        print(formatted)
        self.messages.append(formatted)
    
    def save(self):
        """Log fájl mentése"""
        if self.log_file:
            # Mappa létrehozása ha nem létezik
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.messages))


def check_ffmpeg():
    """Ellenőrzi, hogy az FFmpeg telepítve van-e"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_audio_duration(file_path):
    """Visszaadja az audio fájl hosszát másodpercekben"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
        return None
    except Exception as e:
        return None


def detect_silence_with_ffmpeg(audio_file, min_silence_len=4.0, silence_thresh=-40, logger=None):
    """
    Csend detektálás FFmpeg-gel.
    
    Args:
        audio_file: Audio fájl elérési útja
        min_silence_len: Minimális csend hossza másodpercekben
        silence_thresh: Csend küszöbérték dB-ben
        logger: Logger objektum
    
    Returns:
        Lista a (start, end) tuple-ökről másodpercekben
    """
    if logger:
        logger.log(f"Fájl betöltése: {audio_file}")
    
    # FFmpeg silence detektor használata
    # Ez egy olyan filter, ami detektálja a csendes szakaszokat
    cmd = [
        'ffmpeg',
        '-i', audio_file,
        '-af', f'silencedetect=noise={silence_thresh}dB:d={min_silence_len}',
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignorálja az encoding hibákat
            timeout=300  # 5 perc timeout
        )
        
        # FFmpeg a stderr-re írja a silence detektálás eredményét
        output = result.stderr
        
        if logger:
            duration = get_audio_duration(audio_file)
            if duration:
                logger.log(f"Fájl hossza: {duration:.2f} másodperc")
            logger.log(f"Csend detektálás paraméterek: min_silence={min_silence_len}s, thresh={silence_thresh}dB")
        
        # Parse-oljuk a silence detektálás eredményét
        # Formátum: silence_start: 5.123
        #           silence_end: 10.456
        silence_starts = []
        silence_ends = []
        
        for line in output.split('\n'):
            if 'silence_start:' in line:
                match = re.search(r'silence_start:\s*([\d.]+)', line)
                if match:
                    silence_starts.append(float(match.group(1)))
            elif 'silence_end:' in line:
                match = re.search(r'silence_end:\s*([\d.]+)', line)
                if match:
                    silence_ends.append(float(match.group(1)))
        
        # Szegmensek kinyerése (beszéd részek = nem csendes részek)
        segments = []
        duration = get_audio_duration(audio_file)
        
        if not duration:
            if logger:
                logger.log("⚠️  Nem sikerült meghatározni a fájl hosszát!", "WARNING")
            return []
        
        # Ha nincs csend detektálva, az egész fájl egy szegmens
        if not silence_starts and not silence_ends:
            segments.append((0.0, duration))
            if logger:
                logger.log(f"  Szegmens #1: 0.00s - {duration:.2f}s (hossz: {duration:.2f}s)")
            return segments
        
        # Első szegmens: fájl eleje -> első csend kezdete
        if silence_starts and silence_starts[0] > 0.1:  # Ha van beszéd az elején
            segments.append((0.0, silence_starts[0]))
            if logger:
                logger.log(f"  Szegmens #1: 0.00s - {silence_starts[0]:.2f}s (hossz: {silence_starts[0]:.2f}s)")
        
        # Köztes szegmensek: csend vége -> következő csend kezdete
        for i in range(len(silence_ends)):
            start = silence_ends[i]
            if i + 1 < len(silence_starts):
                end = silence_starts[i + 1]
            else:
                # Utolsó szegmens: utolsó csend vége -> fájl vége
                end = duration
            
            if end - start > 0.1:  # Csak ha van valódi beszéd
                segments.append((start, end))
                if logger:
                    logger.log(f"  Szegmens #{len(segments)}: {start:.2f}s - {end:.2f}s (hossz: {end-start:.2f}s)")
        
        if logger:
            logger.log(f"Talált szegmensek száma: {len(segments)}")
        
        return segments
        
    except subprocess.TimeoutExpired:
        if logger:
            logger.log("❌ HIBA: Az FFmpeg túl sokáig futott!", "ERROR")
        return []
    except Exception as e:
        if logger:
            logger.log(f"❌ HIBA: Csend detektálás sikertelen: {e}", "ERROR")
        return []


def extract_segment(input_file, output_file, start_time, end_time, logger=None):
    """
    Kinyer egy szegmenst az audio fájlból FFmpeg-gel.
    
    Args:
        input_file: Bemeneti fájl
        output_file: Kimeneti fájl
        start_time: Kezdési idő másodpercekben
        end_time: Végidő másodpercekben
        logger: Logger objektum
    
    Returns:
        True ha sikeres, False ha nem
    """
    duration = end_time - start_time
    
    # Abszolút útvonalak biztosítása
    abs_input = os.path.abspath(input_file)
    abs_output = os.path.abspath(output_file)
    
    cmd = [
        'ffmpeg',
        '-i', abs_input,
        '-ss', str(start_time),
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-ab', '192k',
        '-y',  # Felülírás engedélyezése
        abs_output
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignorálja az encoding hibákat
            timeout=60
        )
        if result.returncode != 0:
            if logger:
                logger.log(f"❌ HIBA: Szegmens kinyerés sikertelen ({start_time:.2f}-{end_time:.2f}s)", "ERROR")
                logger.log(f"   FFmpeg hiba: {result.stderr[:200]}", "ERROR")
            return False
        return True
    except Exception as e:
        if logger:
            logger.log(f"❌ HIBA: Szegmens kinyerés sikertelen ({start_time:.2f}-{end_time:.2f}s): {e}", "ERROR")
        return False


def concatenate_audio_files(file1, file2, output_file, logger=None):
    """
    Összefűz két audio fájlt FFmpeg-gel.
    
    Args:
        file1: Első fájl
        file2: Második fájl
        output_file: Kimeneti fájl
        logger: Logger objektum
    """
    # FFmpeg concat fájl létrehozása
    concat_file = output_file + '.concat.txt'
    # Abszolút útvonalak szükségesek FFmpeg-hez
    abs_file1 = os.path.abspath(file1).replace('\\', '/')
    abs_file2 = os.path.abspath(file2).replace('\\', '/')
    with open(concat_file, 'w', encoding='utf-8') as f:
        f.write(f"file '{abs_file1}'\n")
        f.write(f"file '{abs_file2}'\n")
    
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-acodec', 'libmp3lame',
        '-ab', '192k',
        '-y',
        output_file
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignorálja az encoding hibákat
            timeout=120
        )
        
        # Töröljük a concat fájlt
        try:
            os.remove(concat_file)
        except:
            pass
        
        if result.returncode != 0:
            if logger:
                logger.log(f"❌ HIBA: Fájlok összefűzése sikertelen", "ERROR")
                logger.log(f"   FFmpeg hiba: {result.stderr[:200]}", "ERROR")
            return False
        
        return True
    except Exception as e:
        if logger:
            logger.log(f"❌ HIBA: Fájlok összefűzése sikertelen: {e}", "ERROR")
        return False


def pair_questions_answers(questions_file, answers_file, min_silence_len=4.0, 
                           silence_thresh=-40, logger=None):
    """
    Kérdések és válaszok fájljainak párosítása.
    """
    if logger:
        logger.log("\n" + "="*60)
        logger.log("KÉRDÉSEK FELDOLGOZÁSA")
        logger.log("="*60)
    
    questions_segments = detect_silence_with_ffmpeg(
        questions_file, min_silence_len, silence_thresh, logger
    )
    
    if logger:
        logger.log("\n" + "="*60)
        logger.log("VÁLASZOK FELDOLGOZÁSA")
        logger.log("="*60)
    
    answers_segments = detect_silence_with_ffmpeg(
        answers_file, min_silence_len, silence_thresh, logger
    )
    
    # Ellenőrzés
    if len(questions_segments) != len(answers_segments):
        if logger:
            logger.log(f"\n⚠️  FIGYELMEZTETÉS: A kérdések ({len(questions_segments)}) és válaszok ({len(answers_segments)}) száma eltér!", "WARNING")
            logger.log(f"   A párosítás a rövidebb lista hosszáig fog menni.")
    
    # Párosítás
    paired = []
    min_count = min(len(questions_segments), len(answers_segments))
    
    for i in range(min_count):
        paired.append((questions_segments[i], answers_segments[i]))
    
    if logger:
        logger.log(f"\n✓ Sikeresen párosított szegmensek: {len(paired)}")
    
    return paired, questions_file, answers_file


def create_individual_pairs(paired_segments, questions_file, answers_file, output_dir, 
                            tetel_nev="tetel", logger=None):
    """
    Egyedi MP3 fájlok létrehozása minden kérdés-válasz párhoz.
    """
    # Egyéni mappa létrehozása
    individual_dir = Path(output_dir) / "Egyéni"
    individual_dir.mkdir(parents=True, exist_ok=True)
    
    # Temp mappa a szegmenseknek
    temp_dir = Path(output_dir) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    if logger:
        logger.log("\n" + "="*60)
        logger.log("EGYEDI PÁROK LÉTREHOZÁSA")
        logger.log("="*60)
        logger.log(f"Kimeneti mappa: {individual_dir}")
    
    created_files = []
    
    for i, ((q_start, q_end), (a_start, a_end)) in enumerate(paired_segments, 1):
        # Temp fájlok
        temp_q = temp_dir / f"temp_q_{i}.mp3"
        temp_a = temp_dir / f"temp_a_{i}.mp3"
        final_file = individual_dir / f"Q{i:02d}_{tetel_nev}.mp3"
        
        # Kérdés szegmens kinyerése
        if not extract_segment(questions_file, str(temp_q), q_start, q_end, logger):
            if logger:
                logger.log(f"  ⚠️  Kihagyva Q{i:02d}: kérdés kinyerés sikertelen", "WARNING")
            continue
        
        # Válasz szegmens kinyerése
        if not extract_segment(answers_file, str(temp_a), a_start, a_end, logger):
            if logger:
                logger.log(f"  ⚠️  Kihagyva Q{i:02d}: válasz kinyerés sikertelen", "WARNING")
            # Temp fájlok törlése
            try:
                temp_q.unlink()
            except:
                pass
            continue
        
        # Összefűzés
        if concatenate_audio_files(str(temp_q), str(temp_a), str(final_file), logger):
            created_files.append(str(final_file))
            if logger:
                duration = (q_end - q_start) + (a_end - a_start)
                logger.log(f"  ✓ Létrehozva: Q{i:02d}_{tetel_nev}.mp3 (hossz: {duration:.2f}s)")
        else:
            if logger:
                logger.log(f"  ⚠️  Kihagyva Q{i:02d}: összefűzés sikertelen", "WARNING")
        
        # Temp fájlok törlése
        try:
            temp_q.unlink()
            temp_a.unlink()
        except:
            pass
    
    # Temp mappa törlése
    try:
        temp_dir.rmdir()
    except:
        pass
    
    if logger:
        logger.log(f"\n✓ Összesen {len(created_files)} egyedi fájl létrehozva")
    
    return created_files


def create_full_dialogue(paired_segments, questions_file, answers_file, output_file, logger=None):
    """
    Teljes dialógus MP3 létrehozása.
    """
    if logger:
        logger.log("\n" + "="*60)
        logger.log("TELJES DIALÓGUS LÉTREHOZÁSA")
        logger.log("="*60)
    
    # Temp mappa
    temp_dir = Path(output_file).parent / "temp_full"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Összes szegmens kinyerése és összefűzése
    temp_files = []
    
    for i, ((q_start, q_end), (a_start, a_end)) in enumerate(paired_segments, 1):
        temp_q = temp_dir / f"q_{i}.mp3"
        temp_a = temp_dir / f"a_{i}.mp3"
        
        extract_segment(questions_file, str(temp_q), q_start, q_end, logger)
        extract_segment(answers_file, str(temp_a), a_start, a_end, logger)
        
        temp_files.append(str(temp_q))
        temp_files.append(str(temp_a))
        
        if logger and i % 10 == 0:
            logger.log(f"  Feldolgozva: {i}/{len(paired_segments)} pár")
    
    # Összes fájl összefűzése
    concat_file = temp_dir / "concat.txt"
    with open(concat_file, 'w', encoding='utf-8') as f:
        for temp_file in temp_files:
            # Abszolút útvonal szükséges FFmpeg-hez
            abs_path = os.path.abspath(temp_file).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-acodec', 'libmp3lame',
        '-ab', '192k',
        '-y',
        output_file
    ]
    
    if logger:
        logger.log(f"\nMP3 export indítása: {output_file}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignorálja az encoding hibákat
            timeout=600
        )
        
        if result.returncode == 0:
            # Temp fájlok törlése
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            duration = sum((q_end - q_start) + (a_end - a_start) 
                          for (q_start, q_end), (a_start, a_end) in paired_segments)
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            if logger:
                logger.log(f"✓ Teljes dialógus létrehozva: {minutes}:{seconds:02d} perc")
                logger.log(f"  Fájl: {output_file}")
            
            return str(output_file)
        else:
            if logger:
                logger.log(f"❌ HIBA: FFmpeg hiba: {result.stderr}", "ERROR")
            return None
            
    except Exception as e:
        if logger:
            logger.log(f"❌ HIBA: Teljes dialógus létrehozása sikertelen: {e}", "ERROR")
        return None


def main():
    """Fő program logika"""
    parser = argparse.ArgumentParser(
        description="TTS Dialógus Összeállító - FFmpeg verzió (Python 3.13 kompatibilis)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Példa használat:
    python webm_dialogus_osszeallito_ffmpeg.py \\
        --kerdesek MP3/kerdesek.webm \\
        --valaszok MP3/valaszok.webm \\
        --kimenet Tételek/A_cselekvokepesseg/Dialógus/Audio \\
        --tetel A_cselekvokepesseg
        """
    )
    
    parser.add_argument("--kerdesek", required=True, help="Kérdések WEBM fájlja")
    parser.add_argument("--valaszok", required=True, help="Válaszok WEBM fájlja")
    parser.add_argument("--kimenet", required=True, help="Kimeneti mappa")
    parser.add_argument("--tetel", default="tetel", help="Tétel neve")
    parser.add_argument("--csend-hossz", type=float, default=4.0, help="Minimális csend hossza másodpercekben")
    parser.add_argument("--csend-kuszob", type=int, default=-40, help="Csend küszöbérték dB-ben")
    parser.add_argument("--no-egyeni", action="store_true", help="Ne hozza létre az egyedi fájlokat")
    parser.add_argument("--no-teljes", action="store_true", help="Ne hozza létre a teljes dialógust")
    
    args = parser.parse_args()
    
    # FFmpeg ellenőrzés
    if not check_ffmpeg():
        print("❌ HIBA: FFmpeg nincs telepítve vagy nincs a PATH-ban!")
        print("Telepítsd: winget install --id=Gyan.FFmpeg -e")
        sys.exit(1)
    
    # Fájlok ellenőrzése
    if not os.path.exists(args.kerdesek):
        print(f"❌ HIBA: A kérdések fájl nem található: {args.kerdesek}")
        sys.exit(1)
    
    if not os.path.exists(args.valaszok):
        print(f"❌ HIBA: A válaszok fájl nem található: {args.valaszok}")
        sys.exit(1)
    
    # Logger
    output_dir = Path(args.kimenet)
    log_file = output_dir / "feldolgozas_log.txt"
    logger = DialogusOsszeallitoLogger(log_file)
    
    logger.log("="*60)
    logger.log("TTS DIALÓGUS ÖSSZEÁLLÍTÓ - FFmpeg verzió")
    logger.log("="*60)
    logger.log(f"Kérdések fájl: {args.kerdesek}")
    logger.log(f"Válaszok fájl: {args.valaszok}")
    logger.log(f"Kimeneti mappa: {args.kimenet}")
    logger.log(f"Tétel neve: {args.tetel}")
    logger.log(f"Csend detektálás: {args.csend_hossz}s @ {args.csend_kuszob}dB")
    
    try:
        # Párosítás
        paired, questions_file, answers_file = pair_questions_answers(
            args.kerdesek,
            args.valaszok,
            min_silence_len=args.csend_hossz,
            silence_thresh=args.csend_kuszob,
            logger=logger
        )
        
        if not paired:
            logger.log("❌ HIBA: Nem sikerült egyetlen szegmenst sem párosítani!", "ERROR")
            sys.exit(1)
        
        # Egyedi fájlok
        if not args.no_egyeni:
            create_individual_pairs(
                paired,
                questions_file,
                answers_file,
                args.kimenet,
                tetel_nev=args.tetel,
                logger=logger
            )
        
        # Teljes dialógus
        if not args.no_teljes:
            full_dialogue_file = output_dir / f"Teljes_Dialogus_{args.tetel}.mp3"
            create_full_dialogue(
                paired,
                questions_file,
                answers_file,
                full_dialogue_file,
                logger=logger
            )
        
        # Összegzés
        logger.log("\n" + "="*60)
        logger.log("FELDOLGOZÁS BEFEJEZVE")
        logger.log("="*60)
        logger.log(f"✓ Párosított szegmensek: {len(paired)}")
        if not args.no_egyeni:
            logger.log(f"✓ Egyedi fájlok: {output_dir / 'Egyéni'}")
        if not args.no_teljes:
            logger.log(f"✓ Teljes dialógus: {full_dialogue_file}")
        logger.log(f"✓ Log fájl: {log_file}")
        
        logger.save()
        print("\n✅ Sikeres feldolgozás!")
        
    except Exception as e:
        logger.log(f"\n❌ HIBA: {str(e)}", "ERROR")
        logger.save()
        raise


if __name__ == "__main__":
    main()

