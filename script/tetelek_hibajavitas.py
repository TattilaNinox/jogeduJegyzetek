#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS feldolgozott szövegek hibajavító szkripte
Automatikusan javítja a valódi hibákat (duplikációk, formázási hibák),
miközben megtartja a jogászi kifejezésmódokat és hosszú hivatkozásokat.

Használat:
    python script/tetelek_hibajavitas.py input.txt output.txt
    vagy
    python script/tetelek_hibajavitas.py Tételek/
"""

import re
import os
import sys
from pathlib import Path


def duplikalt_szavak_javitas(szoveg):
    """
    Duplikált szavak/kifejezések eltávolítása.
    
    Példa: "A Polgári Törvénykönyv Polgári Törvénykönyv a következőképpen"
    -> "A Polgári Törvénykönyv a következőképpen"
    """
    # Speciális eset: "A A" -> "A" (először ezt kezeljük)
    szoveg = re.sub(r'\bA\s+A\s+', 'A ', szoveg)
    szoveg = re.sub(r'\ba\s+a\s+', 'a ', szoveg)
    
    # Duplikált szavak/kifejezések (1-5 szavas kifejezések)
    # Minta: "Polgári Törvénykönyv Polgári Törvénykönyv"
    
    # Először a rövid duplikációk (1 szó) - nagybetűvel kezdődő
    szoveg = re.sub(r'\b([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+)\s+\1\b', r'\1', szoveg)
    
    # 2 szavas kifejezések: "Polgári Törvénykönyv Polgári Törvénykönyv"
    szoveg = re.sub(r'\b([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+\s+[a-záéíóöőúüű]+)\s+\1\b', r'\1', szoveg)
    
    # 3 szavas kifejezések
    szoveg = re.sub(r'\b([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+(?:\s+[a-záéíóöőúüű]+){2})\s+\1\b', r'\1', szoveg)
    
    # 4 szavas kifejezések
    szoveg = re.sub(r'\b([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+(?:\s+[a-záéíóöőúüű]+){3})\s+\1\b', r'\1', szoveg)
    
    # 5 szavas kifejezések
    szoveg = re.sub(r'\b([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+(?:\s+[a-záéíóöőúüű]+){4})\s+\1\b', r'\1', szoveg)
    
    return szoveg


def ismetlodo_szavak_javitas(szoveg):
    """
    Ismétlődő szavak javítása, ahol ugyanaz a szó kétszer következik egymás után.
    
    Példa: "második bekezdése bekezdés" -> "második bekezdése"
    Példa: "paragrafusának paragrafusának" -> "paragrafusának"
    """
    # Gyakori ismétlődések: "bekezdése bekezdés", "paragrafusának paragrafusának"
    
    # "bekezdése bekezdés" -> "bekezdése" (a "bekezdés" rész ismétlődik)
    # Minta: "bekezdése" + szóköz + "bekezdés" (a "bekezdés" a "bekezdése" része)
    szoveg = re.sub(r'\b(bekezdése)\s+bekezdés\b', r'\1', szoveg, flags=re.IGNORECASE)
    
    # "bekezdés bekezdés" -> "bekezdés"
    szoveg = re.sub(r'\b(bekezdés)\s+\1\b', r'\1', szoveg, flags=re.IGNORECASE)
    
    # "paragrafusának paragrafusának" -> "paragrafusának"
    szoveg = re.sub(r'\b(paragrafusának)\s+\1\b', r'\1', szoveg, flags=re.IGNORECASE)
    
    # "paragrafusa paragrafusa" -> "paragrafusa"
    szoveg = re.sub(r'\b(paragrafusa)\s+\1\b', r'\1', szoveg, flags=re.IGNORECASE)
    
    # "második bekezdése bekezdés" -> "második bekezdése"
    # Általános minta: bármilyen szó + "bekezdése" + szóköz + "bekezdés"
    szoveg = re.sub(r'\b([a-záéíóöőúüű]+)\s+(bekezdése)\s+bekezdés\b', r'\1 \2', szoveg, flags=re.IGNORECASE)
    
    # Általános ismétlődés észlelése (legalább 4 karakter hosszú szavaknál)
    # De csak akkor, ha a szó teljes egészében ismétlődik
    szoveg = re.sub(r'\b([a-záéíóöőúüű]{4,})\s+\1\b', r'\1', szoveg, flags=re.IGNORECASE)
    
    return szoveg


def tobbszoros_szokozok_javitas(szoveg):
    """Többszörös szóközök normalizálása egyetlen szóközre"""
    szoveg = re.sub(r'\s+', ' ', szoveg)
    return szoveg.strip()


def tobbszoros_irasjelek_javitas(szoveg):
    """Többszörös írásjelek normalizálása"""
    # Többszörös pontok -> egy pont
    szoveg = re.sub(r'\.{2,}', '.', szoveg)
    # Többszörös vesszők -> egy vessző
    szoveg = re.sub(r',{2,}', ',', szoveg)
    # Többszörös kérdőjelek -> egy kérdőjel
    szoveg = re.sub(r'\?{2,}', '?', szoveg)
    # Többszörös felkiáltójelek -> egy felkiáltójel
    szoveg = re.sub(r'!{2,}', '!', szoveg)
    return szoveg


def szoveg_tisztitas(szoveg):
    """
    Összefoglaló tisztítási függvény, amely minden hibajavítást elvégzi.
    Sorrend: duplikációk -> ismétlődések -> szóközök -> írásjelek
    """
    # 1. Duplikált szavak/kifejezések eltávolítása
    szoveg = duplikalt_szavak_javitas(szoveg)
    
    # 2. Ismétlődő szavak javítása
    szoveg = ismetlodo_szavak_javitas(szoveg)
    
    # 3. Többszörös szóközök normalizálása
    szoveg = tobbszoros_szokozok_javitas(szoveg)
    
    # 4. Többszörös írásjelek normalizálása
    szoveg = tobbszoros_irasjelek_javitas(szoveg)
    
    return szoveg


def fajl_feldolgozas(bemenet_utvonal, kimenet_utvonal=None):
    """
    Egyetlen fájl feldolgozása és hibajavítása.
    
    Args:
        bemenet_utvonal: A bemeneti fájl elérési útja
        kimenet_utvonal: A kimeneti fájl elérési útja (opcionális)
    """
    try:
        with open(bemenet_utvonal, 'r', encoding='utf-8') as f:
            szoveg = f.read()
    except FileNotFoundError:
        print(f"Hiba: A fájl nem található: {bemenet_utvonal}")
        return False
    
    # Hibajavítás
    javitott_szoveg = szoveg_tisztitas(szoveg)
    
    # Kimenet meghatározása
    if kimenet_utvonal is None:
        # Ha nincs megadva kimenet, a bemeneti fájl neve + "_javított" kiterjesztéssel
        bemenet_path = Path(bemenet_utvonal)
        kimenet_utvonal = bemenet_path.parent / f"{bemenet_path.stem}_javított{bemenet_path.suffix}"
    
    # Kimenet írása
    try:
        with open(kimenet_utvonal, 'w', encoding='utf-8') as f:
            f.write(javitott_szoveg)
        print(f"✓ Feldolgozva: {bemenet_utvonal} -> {kimenet_utvonal}")
        return True
    except Exception as e:
        print(f"Hiba a fájl írása során: {e}")
        return False


def mappa_feldolgozas(mappa_utvonal, kimenet_mappa=None):
    """
    Egy mappa összes .txt fájljának feldolgozása.
    
    Args:
        mappa_utvonal: A mappa elérési útja
        kimenet_mappa: A kimeneti mappa elérési útja (opcionális)
    """
    mappa_path = Path(mappa_utvonal)
    
    if not mappa_path.is_dir():
        print(f"Hiba: A mappa nem létezik: {mappa_utvonal}")
        return
    
    # Kimenet mappa meghatározása
    if kimenet_mappa is None:
        kimenet_mappa = mappa_path / "javított"
    else:
        kimenet_mappa = Path(kimenet_mappa)
    
    # Kimenet mappa létrehozása
    kimenet_mappa.mkdir(parents=True, exist_ok=True)
    
    # Összes .txt fájl feldolgozása
    txt_fajlok = list(mappa_path.glob("*.txt"))
    
    if not txt_fajlok:
        print(f"Figyelem: Nem található .txt fájl a mappában: {mappa_utvonal}")
        return
    
    print(f"Feldolgozás indítása: {len(txt_fajlok)} fájl...")
    print(f"Kimeneti mappa: {kimenet_mappa}\n")
    
    sikeres = 0
    for txt_fajl in txt_fajlok:
        kimenet_fajl = kimenet_mappa / txt_fajl.name
        if fajl_feldolgozas(txt_fajl, kimenet_fajl):
            sikeres += 1
    
    print(f"\n✓ Feldolgozás kész: {sikeres}/{len(txt_fajlok)} fájl sikeresen feldolgozva")


def main():
    """Fő függvény"""
    if len(sys.argv) < 2:
        print("Használat:")
        print("  python script/tetelek_hibajavitas.py <bemenet_fájl> [kimenet_fájl]")
        print("  python script/tetelek_hibajavitas.py <mappa_utvonal>")
        print("\nPéldák:")
        print("  python script/tetelek_hibajavitas.py input.txt output.txt")
        print("  python script/tetelek_hibajavitas.py Tételek/")
        sys.exit(1)
    
    bemenet = sys.argv[1]
    bemenet_path = Path(bemenet)
    
    # Ha fájl
    if bemenet_path.is_file():
        kimenet = sys.argv[2] if len(sys.argv) > 2 else None
        fajl_feldolgozas(bemenet, kimenet)
    # Ha mappa
    elif bemenet_path.is_dir():
        kimenet_mappa = sys.argv[2] if len(sys.argv) > 2 else None
        mappa_feldolgozas(bemenet, kimenet_mappa)
    else:
        print(f"Hiba: A megadott útvonal nem létezik: {bemenet}")
        sys.exit(1)


if __name__ == '__main__':
    main()

