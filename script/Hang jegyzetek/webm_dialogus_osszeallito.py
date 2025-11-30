#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS Dialógus Összeállító Script
================================

Ez a script WEBM hangfájlokat (kérdések és válaszok) dolgoz fel:
1. Csend alapján szegmentálja őket
2. Párosítja a kérdéseket és válaszokat
3. Létrehozza az egyedi MP3 fájlokat minden kérdés-válasz párhoz
4. Létrehozza a teljes dialógus MP3-at

Használat:
    python webm_dialogus_osszeallito.py --kerdesek kerdesek.webm --valaszok valaszok.webm --kimenet Audio/

Követelmények:
    - pydub (pip install pydub)
    - numpy (pip install numpy)
    - FFmpeg (telepítve és PATH-ban)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    # Python 3.13 workaround: próbáljuk meg telepíteni a pyaudioop-ot ha hiányzik
    try:
        import audioop
    except ImportError:
        try:
            import pyaudioop as audioop
        except ImportError:
            # Ha nincs audioop és pyaudioop sem, próbáljuk meg telepíteni
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudioop-win"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import pyaudioop as audioop
            except:
                pass  # Folytatjuk, lehet hogy nem kell
    
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
except ImportError as e:
    print("❌ HIBA: A pydub nincs telepítve vagy nem kompatibilis Python 3.13-mal!")
    print(f"Részletes hiba: {e}")
    print("\nPróbáld meg:")
    print("    1. pip install --upgrade pydub")
    print("    2. VAGY használj Python 3.12-t")
    print("    3. VAGY telepítsd: pip install pyaudioop-win")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("❌ HIBA: A numpy nincs telepítve!")
    print("Telepítsd a következő paranccsal:")
    print("    pip install numpy")
    sys.exit(1)


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
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.messages))


def detect_silence_segments(audio_file, min_silence_len=4000, silence_thresh=-40, logger=None):
    """
    Hangfájl szegmentálása csendes szakaszok alapján.
    
    Args:
        audio_file: A feldolgozandó audio fájl elérési útja
        min_silence_len: Minimális csend hossza ms-ben (alapértelmezett: 4000 = 4 mp)
        silence_thresh: Csend küszöbérték dB-ben (alapértelmezett: -40)
        logger: Logger objektum
    
    Returns:
        Lista az audio szegmensekről (AudioSegment objektumok)
    """
    if logger:
        logger.log(f"Fájl betöltése: {audio_file}")
    
    # Audio betöltése
    audio = AudioSegment.from_file(audio_file)
    
    if logger:
        logger.log(f"Fájl hossza: {len(audio) / 1000:.2f} másodperc")
        logger.log(f"Csend detektálás paraméterek: min_silence={min_silence_len}ms, thresh={silence_thresh}dB")
    
    # Nem csendes (beszéd) szakaszok detektálása
    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=100  # 100ms-onként vizsgálja
    )
    
    if logger:
        logger.log(f"Talált szegmensek száma: {len(nonsilent_ranges)}")
    
    # Szegmensek kinyerése
    segments = []
    for i, (start, end) in enumerate(nonsilent_ranges):
        segment = audio[start:end]
        segments.append(segment)
        
        if logger:
            logger.log(f"  Szegmens #{i+1}: {start/1000:.2f}s - {end/1000:.2f}s (hossz: {(end-start)/1000:.2f}s)")
    
    return segments


def pair_questions_answers(questions_file, answers_file, min_silence_len=4000, 
                           silence_thresh=-40, logger=None):
    """
    Kérdések és válaszok fájljainak párosítása.
    
    Args:
        questions_file: Kérdések WEBM fájlja
        answers_file: Válaszok WEBM fájlja
        min_silence_len: Minimális csend hossza
        silence_thresh: Csend küszöbérték
        logger: Logger objektum
    
    Returns:
        Lista a párosított (kérdés, válasz) tuple-ökről
    """
    if logger:
        logger.log("\n" + "="*60)
        logger.log("KÉRDÉSEK FELDOLGOZÁSA")
        logger.log("="*60)
    
    questions = detect_silence_segments(questions_file, min_silence_len, silence_thresh, logger)
    
    if logger:
        logger.log("\n" + "="*60)
        logger.log("VÁLASZOK FELDOLGOZÁSA")
        logger.log("="*60)
    
    answers = detect_silence_segments(answers_file, min_silence_len, silence_thresh, logger)
    
    # Ellenőrzés
    if len(questions) != len(answers):
        if logger:
            logger.log(f"\n⚠️  FIGYELMEZTETÉS: A kérdések ({len(questions)}) és válaszok ({len(answers)}) száma eltér!", "WARNING")
            logger.log(f"   A párosítás a rövidebb lista hosszáig fog menni.")
    
    # Párosítás
    paired = []
    min_count = min(len(questions), len(answers))
    
    for i in range(min_count):
        paired.append((questions[i], answers[i]))
    
    if logger:
        logger.log(f"\n✓ Sikeresen párosított szegmensek: {len(paired)}")
    
    return paired


def create_individual_pairs(paired_segments, output_dir, tetel_nev="tetel", logger=None):
    """
    Egyedi MP3 fájlok létrehozása minden kérdés-válasz párhoz.
    
    Args:
        paired_segments: Lista a (kérdés, válasz) tuple-ökről
        output_dir: Kimeneti mappa
        tetel_nev: Tétel neve a fájlnév generáláshoz
        logger: Logger objektum
    
    Returns:
        Lista a létrehozott fájlnevekről
    """
    # Egyéni mappa létrehozása
    individual_dir = Path(output_dir) / "Egyéni"
    individual_dir.mkdir(parents=True, exist_ok=True)
    
    if logger:
        logger.log("\n" + "="*60)
        logger.log("EGYEDI PÁROK LÉTREHOZÁSA")
        logger.log("="*60)
        logger.log(f"Kimeneti mappa: {individual_dir}")
    
    created_files = []
    
    for i, (question, answer) in enumerate(paired_segments, 1):
        # Kérdés és válasz összefűzése (gördülékeny átmenet, nincs szünet)
        combined = question + answer
        
        # Fájlnév generálása
        filename = f"Q{i:02d}_{tetel_nev}.mp3"
        filepath = individual_dir / filename
        
        # MP3 export
        combined.export(
            filepath,
            format="mp3",
            bitrate="192k",
            parameters=["-q:a", "0"]  # VBR, legjobb minőség
        )
        
        created_files.append(str(filepath))
        
        if logger:
            duration = len(combined) / 1000
            logger.log(f"  ✓ Létrehozva: {filename} (hossz: {duration:.2f}s)")
    
    if logger:
        logger.log(f"\n✓ Összesen {len(created_files)} egyedi fájl létrehozva")
    
    return created_files


def create_full_dialogue(paired_segments, output_file, logger=None):
    """
    Teljes dialógus MP3 létrehozása az összes kérdés-válasz pár összefűzésével.
    
    Args:
        paired_segments: Lista a (kérdés, válasz) tuple-ökről
        output_file: Kimeneti fájl elérési útja
        logger: Logger objektum
    
    Returns:
        A létrehozott fájl elérési útja
    """
    if logger:
        logger.log("\n" + "="*60)
        logger.log("TELJES DIALÓGUS LÉTREHOZÁSA")
        logger.log("="*60)
    
    # Összes szegmens összefűzése
    full_dialogue = AudioSegment.empty()
    
    for i, (question, answer) in enumerate(paired_segments, 1):
        # Kérdés hozzáadása
        full_dialogue += question
        # Válasz hozzáadása (gördülékeny átmenet)
        full_dialogue += answer
        
        if logger and i % 10 == 0:
            logger.log(f"  Feldolgozva: {i}/{len(paired_segments)} pár")
    
    # Kimeneti mappa létrehozása
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # MP3 export
    if logger:
        logger.log(f"\nMP3 export indítása: {output_file}")
    
    full_dialogue.export(
        output_file,
        format="mp3",
        bitrate="192k",
        parameters=["-q:a", "0"]  # VBR, legjobb minőség
    )
    
    if logger:
        total_duration = len(full_dialogue) / 1000
        minutes = int(total_duration // 60)
        seconds = int(total_duration % 60)
        logger.log(f"✓ Teljes dialógus létrehozva: {minutes}:{seconds:02d} perc")
        logger.log(f"  Fájl: {output_file}")
    
    return str(output_file)


def main():
    """Fő program logika"""
    parser = argparse.ArgumentParser(
        description="TTS Dialógus Összeállító - WEBM fájlok feldolgozása és MP3 generálás",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Példa használat:
    python webm_dialogus_osszeallito.py \\
        --kerdesek MP3/kerdesek.webm \\
        --valaszok MP3/valaszok.webm \\
        --kimenet Tételek/A_cselekvokepesseg/Dialógus/Audio \\
        --tetel A_cselekvokepesseg

Paraméter finomhangolás:
    python webm_dialogus_osszeallito.py \\
        --kerdesek kerdesek.webm \\
        --valaszok valaszok.webm \\
        --kimenet Audio/ \\
        --csend-hossz 5000 \\
        --csend-kuszob -35
        """
    )
    
    parser.add_argument(
        "--kerdesek",
        required=True,
        help="Kérdések WEBM fájlja"
    )
    
    parser.add_argument(
        "--valaszok",
        required=True,
        help="Válaszok WEBM fájlja"
    )
    
    parser.add_argument(
        "--kimenet",
        required=True,
        help="Kimeneti mappa az MP3 fájloknak"
    )
    
    parser.add_argument(
        "--tetel",
        default="tetel",
        help="Tétel neve a fájlnevek generálásához (alapértelmezett: tetel)"
    )
    
    parser.add_argument(
        "--csend-hossz",
        type=int,
        default=4000,
        help="Minimális csend hossza ms-ben (alapértelmezett: 4000)"
    )
    
    parser.add_argument(
        "--csend-kuszob",
        type=int,
        default=-40,
        help="Csend küszöbérték dB-ben (alapértelmezett: -40)"
    )
    
    parser.add_argument(
        "--no-egyeni",
        action="store_true",
        help="Ne hozza létre az egyedi fájlokat, csak a teljes dialógust"
    )
    
    parser.add_argument(
        "--no-teljes",
        action="store_true",
        help="Ne hozza létre a teljes dialógust, csak az egyedi fájlokat"
    )
    
    args = parser.parse_args()
    
    # Ellenőrzések
    if not os.path.exists(args.kerdesek):
        print(f"❌ HIBA: A kérdések fájl nem található: {args.kerdesek}")
        sys.exit(1)
    
    if not os.path.exists(args.valaszok):
        print(f"❌ HIBA: A válaszok fájl nem található: {args.valaszok}")
        sys.exit(1)
    
    # Logger inicializálása
    output_dir = Path(args.kimenet)
    log_file = output_dir / "feldolgozas_log.txt"
    logger = DialogusOsszeallitoLogger(log_file)
    
    # Program indítása
    logger.log("="*60)
    logger.log("TTS DIALÓGUS ÖSSZEÁLLÍTÓ")
    logger.log("="*60)
    logger.log(f"Kérdések fájl: {args.kerdesek}")
    logger.log(f"Válaszok fájl: {args.valaszok}")
    logger.log(f"Kimeneti mappa: {args.kimenet}")
    logger.log(f"Tétel neve: {args.tetel}")
    logger.log(f"Csend detektálás: {args.csend_hossz}ms @ {args.csend_kuszob}dB")
    
    try:
        # Párosítás
        paired = pair_questions_answers(
            args.kerdesek,
            args.valaszok,
            min_silence_len=args.csend_hossz,
            silence_thresh=args.csend_kuszob,
            logger=logger
        )
        
        if not paired:
            logger.log("❌ HIBA: Nem sikerült egyetlen szegmenst sem párosítani!", "ERROR")
            sys.exit(1)
        
        # Egyedi fájlok létrehozása
        if not args.no_egyeni:
            create_individual_pairs(
                paired,
                args.kimenet,
                tetel_nev=args.tetel,
                logger=logger
            )
        
        # Teljes dialógus létrehozása
        if not args.no_teljes:
            full_dialogue_file = output_dir / f"Teljes_Dialogus_{args.tetel}.mp3"
            create_full_dialogue(
                paired,
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
        
        # Log mentése
        logger.save()
        
        print("\n✅ Sikeres feldolgozás!")
        
    except Exception as e:
        logger.log(f"\n❌ HIBA: {str(e)}", "ERROR")
        logger.save()
        raise


if __name__ == "__main__":
    main()

