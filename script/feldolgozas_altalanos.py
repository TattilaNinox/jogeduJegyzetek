#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Általánosított feldolgozó szkript tananyag-generáláshoz
Használható bármilyen témában, csak a konfigurációt kell módosítani.
"""

import re
import os
from pathlib import Path

# ============================================================================
# KONFIGURÁCIÓ - Itt módosíthatod a specifikus beállításokat
# ============================================================================

# Rövidítések és kibontásaik
ROVIDITESEK = {
    'pl.': 'például',
    'Ptk.': 'Polgári Törvénykönyv',
    'stb.': 'és így tovább',
    'ld.': 'lásd',
    'vm.': 'valamely',
    'INY': 'ingatlan-nyilvántartás',
    # Itt lehet további rövidítéseket hozzáadni
}

# Latin kifejezések és fonetikus változataik
LATIN_KIFEJEZESEK = {
    'numerus clausus': 'numerusz klauzusz',
    'Nemo plus iuris': 'Nemo plusz jürisz',
    'Traditio': 'Tradíció',
    'Brevi manu traditio': 'Brevi manu tradíció',
    'Constitutum possessorium': 'Konstitútum possesszorium',
    'Longa manu traditio': 'Longa manu tradíció',
    'Cessi vindicatio': 'Cessi vindikáció',
    # Itt lehet további latin kifejezéseket hozzáadni
}

# Számok fonetikus formája
SZAMOK = {
    '1': 'egy', '2': 'kettő', '3': 'három', '4': 'négy', '5': 'öt',
    '6': 'hat', '7': 'hét', '8': 'nyolc', '9': 'kilenc', '10': 'tíz',
    '11': 'tizenegy', '12': 'tizenkettő', '13': 'tizenhárom', '14': 'tizennégy', '15': 'tizenöt',
    '16': 'tizenhat', '17': 'tizenhét', '18': 'tizennyolc', '19': 'tizenkilenc', '20': 'húsz',
    '21': 'huszonegy', '22': 'huszonkettő', '23': 'huszonhárom', '24': 'huszonnégy', '25': 'huszonöt',
    '26': 'huszonhat', '27': 'huszonhét', '28': 'huszonnyolc', '29': 'huszonkilenc', '30': 'harminc',
    '40': 'negyven', '50': 'ötven'
}

# Törvényi hivatkozások formátuma (pl. Ptk. 5:23. §)
TORVENYI_HIVATKOZAS_MINT = r'Polgári Törvénykönyv\s*(\d+):(\d+)\.\s*§\s*(\((\d+)\))?'

# ============================================================================
# FELDOLGOZÁSI FÜGGVÉNYEK
# ============================================================================

def fonetikus_szamok(szoveg, torvenyi_hivatkozas_mint=None):
    """Számokat fonetikusan írja ki"""
    szamok = SZAMOK.copy()
    
    # Ha van törvényi hivatkozás mint, akkor azt is kezeljük
    if torvenyi_hivatkozas_mint:
        def helyettesit_torvenyi_hivatkozas(match):
            konyv = match.group(1)
            paragrafus = match.group(2)
            bekezdes = match.group(4) if match.group(4) else ''
            
            konyv_szoveg = szamok.get(konyv, konyv)
            paragrafus_szoveg = szamok.get(paragrafus, paragrafus)
            
            if bekezdes:
                bekezdes_szoveg = szamok.get(bekezdes, bekezdes)
                return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {bekezdes_szoveg} bekezdése"
            else:
                return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusa"
        
        szoveg = re.sub(torvenyi_hivatkozas_mint, helyettesit_torvenyi_hivatkozas, szoveg)
    
    # Általános számok helyettesítése (pl. "A 2 bekezdés" -> "A kettő bekezdés")
    szoveg = re.sub(r'A\s*\((\d+)\)\s*bekezdés', 
                   lambda m: f"A {szamok.get(m.group(1), m.group(1))} bekezdés", 
                   szoveg)
    szoveg = re.sub(r'A\s+(\d+)\s+bekezdés', 
                   lambda m: f"A {szamok.get(m.group(1), m.group(1))} bekezdés", 
                   szoveg)
    
    return szoveg

def eltavolit_speciális_karakterek(szoveg):
    """Speciális karakterek eltávolítása vagy szöveggé alakítása"""
    # Zárójelek eltávolítása, tartalom megtartása
    szoveg = re.sub(r'\(([^)]+)\)', r'\1', szoveg)
    
    # Nyilak szöveggé alakítása
    szoveg = szoveg.replace('->', 'akkor következik')
    szoveg = szoveg.replace('→', 'akkor következik')
    
    return szoveg

def latin_fonetikus(szoveg, latin_kifejezesek=None):
    """Latin kifejezések fonetikusan"""
    if latin_kifejezesek is None:
        latin_kifejezesek = LATIN_KIFEJEZESEK
    
    for latin_kifejezes, fonetikus in latin_kifejezesek.items():
        szoveg = szoveg.replace(latin_kifejezes, fonetikus)
    
    return szoveg

def felsorolas_atalakit(szoveg):
    """Felsorolások folyó szöveggé alakítása"""
    # Listajeles pontok eltávolítása és átalakítása
    szoveg = re.sub(r'^\s*[-•*]\s+', '', szoveg, flags=re.MULTILINE)
    szoveg = re.sub(r'^\s*\d+\.\s+', '', szoveg, flags=re.MULTILINE)
    
    # a), b), c) stb. pontok átalakítása
    szoveg = re.sub(r'\s*([a-z])\)\s+', r' \1, ', szoveg)
    
    return szoveg

def rovidites_kibontas(szoveg, roviditesek=None):
    """Rövidítések kibontása"""
    if roviditesek is None:
        roviditesek = ROVIDITESEK
    
    for rovidites, kibontott in roviditesek.items():
        szoveg = szoveg.replace(rovidites, kibontott)
    
    return szoveg

def feldolgoz(szoveg, torvenyi_hivatkozas_mint=None):
    """Fő feldolgozási függvény"""
    # Rövidítések kibontása
    szoveg = rovidites_kibontas(szoveg)
    
    # Latin kifejezések fonetikusan
    szoveg = latin_fonetikus(szoveg)
    
    # Speciális karakterek
    szoveg = eltavolit_speciális_karakterek(szoveg)
    
    # Felsorolások átalakítása
    szoveg = felsorolas_atalakit(szoveg)
    
    # Számok fonetikusan (a hivatkozások után)
    szoveg = fonetikus_szamok(szoveg, torvenyi_hivatkozas_mint)
    
    # Többszörös szóközök eltávolítása
    szoveg = re.sub(r'\s+', ' ', szoveg)
    
    # Többszörös pontok eltávolítása
    szoveg = re.sub(r'\.{2,}', '.', szoveg)
    
    return szoveg.strip()

def beolvas_fajl(utvonal):
    """Fájl beolvasása"""
    with open(utvonal, 'r', encoding='utf-8') as f:
        return f.read()

def duplikaciok_eltavolitasa(mondatok):
    """Duplikált mondatok eltávolítása"""
    lathatott_mondatok = set()
    egyedi_mondatok = []
    for mondat in mondatok:
        mondat_rovid = mondat[:80].lower().strip() if len(mondat) > 80 else mondat.lower().strip()
        mondat_rovid = re.sub(r'\s+', ' ', mondat_rovid)
        if mondat_rovid not in lathatott_mondatok and len(mondat_rovid) > 10:
            lathatott_mondatok.add(mondat_rovid)
            egyedi_mondatok.append(mondat)
    return egyedi_mondatok

def narrativva_alakit(szoveg, mondatok_per_bekezdes=3):
    """Szöveget narratív formába alakítja, bekezdésekre tagolja"""
    # Mondatokra bontás
    mondatok = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÖŐÚÜŰ])', szoveg)
    mondatok = [m.strip() for m in mondatok if m.strip()]
    
    # Duplikációk eltávolítása
    mondatok = duplikaciok_eltavolitasa(mondatok)
    
    # Üres mondatok eltávolítása és végpontok biztosítása
    tiszta_mondatok = []
    for mondat in mondatok:
        mondat = mondat.strip()
        if mondat:
            if not re.search(r'[.!?]$', mondat):
                mondat += '.'
            tiszta_mondatok.append(mondat)
    
    # Bekezdésformázás
    bekezdesek = []
    jelenlegi_bekezdes = []
    for mondat in tiszta_mondatok:
        jelenlegi_bekezdes.append(mondat)
        if len(jelenlegi_bekezdes) >= mondatok_per_bekezdes or (len(jelenlegi_bekezdes) >= 2 and len(mondat) > 200):
            bekezdesek.append(' '.join(jelenlegi_bekezdes))
            jelenlegi_bekezdes = []
    if jelenlegi_bekezdes:
        bekezdesek.append(' '.join(jelenlegi_bekezdes))
    
    return '\n\n'.join(bekezdesek)

# ============================================================================
# FŐ FELDOLGOZÁS
# ============================================================================

def feldolgoz_fajlokat(kerdesek_utvonal, valaszok_utvonal, magyarazatok_utvonal, 
                      kimenet_utvonal, tetel_szama=50, konyvtar=''):
    """
    Fő feldolgozási függvény
    
    Args:
        kerdesek_utvonal: Kérdések fájl elérési útja
        valaszok_utvonal: Válaszok fájl elérési útja
        magyarazatok_utvonal: Magyarázatok fájl elérési útja
        kimenet_utvonal: Kimeneti fájl elérési útja
        tetel_szama: Feldolgozandó tételek száma
        konyvtar: Munkakönyvtár (opcionális)
    """
    # Fájlok beolvasása
    kerdesek = beolvas_fajl(os.path.join(konyvtar, kerdesek_utvonal) if konyvtar else kerdesek_utvonal)
    valaszok = beolvas_fajl(os.path.join(konyvtar, valaszok_utvonal) if konyvtar else valaszok_utvonal)
    magyarazatok = beolvas_fajl(os.path.join(konyvtar, magyarazatok_utvonal) if konyvtar else magyarazatok_utvonal)
    
    # Tételek szétválasztása
    kerdes_tetelek = re.split(r'^\s*\d+\.\s+', kerdesek, flags=re.MULTILINE)
    valasz_tetelek = re.split(r'^\s*\d+\.\s+', valaszok, flags=re.MULTILINE)
    magyarazat_tetelek = re.split(r'^\s*\d+\.\s+', magyarazatok, flags=re.MULTILINE)
    
    # Az első elem lehet üres
    if kerdes_tetelek and not kerdes_tetelek[0].strip():
        kerdes_tetelek = kerdes_tetelek[1:]
    if valasz_tetelek and not valasz_tetelek[0].strip():
        valasz_tetelek = valasz_tetelek[1:]
    if magyarazat_tetelek and not magyarazat_tetelek[0].strip():
        magyarazat_tetelek = magyarazat_tetelek[1:]
    
    kimenet = []
    
    for i in range(min(tetel_szama, len(kerdes_tetelek), len(valasz_tetelek), len(magyarazat_tetelek))):
        kerdes = kerdes_tetelek[i].strip() if i < len(kerdes_tetelek) else ''
        valasz = valasz_tetelek[i].strip() if i < len(valasz_tetelek) else ''
        magyarazat = magyarazat_tetelek[i].strip() if i < len(magyarazat_tetelek) else ''
        
        # Kombinálás - intelligens egyesítés
        if valasz and magyarazat:
            if valasz.strip() in magyarazat:
                kombinált = magyarazat.strip()
            else:
                kombinált = f"{valasz} {magyarazat}".strip()
        elif magyarazat:
            kombinált = magyarazat.strip()
        elif valasz:
            kombinált = valasz.strip()
        else:
            kombinált = ''
        
        # Feldolgozás
        feldolgozott = feldolgoz(kombinált, TORVENYI_HIVATKOZAS_MINT)
        
        # Narratívvá alakítás
        feldolgozott_szoveg = narrativva_alakit(feldolgozott)
        
        kimenet.append(feldolgozott_szoveg)
    
    # Kimenet írása
    kimeneti_szoveg = '\n\n\n'.join(kimenet)
    
    kimenet_vegleges_utvonal = os.path.join(konyvtar, kimenet_utvonal) if konyvtar else kimenet_utvonal
    os.makedirs(os.path.dirname(kimenet_vegleges_utvonal), exist_ok=True)
    
    with open(kimenet_vegleges_utvonal, 'w', encoding='utf-8') as f:
        f.write(kimeneti_szoveg)
    
    print(f"Feldolgozás kész! {len(kimenet)} tétel feldolgozva.")
    return len(kimenet)

# ============================================================================
# PÉLDA HASZNÁLAT
# ============================================================================

if __name__ == '__main__':
    # Példa konfiguráció
    konyvtar = '/Users/tolgyesiattila/Desktop/Polgári jog/Dologi_jog_fogalma_rendszere'
    
    feldolgoz_fajlokat(
        kerdesek_utvonal='kerdesek.txt',
        valaszok_utvonal='valaszok.txt',
        magyarazatok_utvonal='magyarazatok.txt',
        kimenet_utvonal='feldolgozott_tananyag/tananyag.txt',
        tetel_szama=50,
        konyvtar=konyvtar
    )

