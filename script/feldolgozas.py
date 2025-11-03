#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feldolgozó szkript a dologi jog tananyag generálásához
Használat: python3 feldolgozas.py [mappa_utvonal]
Példa: python3 feldolgozas.py "/Users/tolgyesiattila/Desktop/Polgári jog/Családjog"
"""

import re
import os

def fonetikus_szamok(szoveg):
    """Számokat fonetikusan írja ki"""
    # Alanyeset (alapértelmezett)
    szamok = {
        '1': 'egy', '2': 'kettő', '3': 'három', '4': 'négy', '5': 'öt',
        '6': 'hat', '7': 'hét', '8': 'nyolc', '9': 'kilenc', '10': 'tíz',
        '11': 'tizenegy', '12': 'tizenkettő', '13': 'tizenhárom', '14': 'tizennégy', '15': 'tizenöt',
        '16': 'tizenhat', '17': 'tizenhét', '18': 'tizennyolc', '19': 'tizenkilenc', '20': 'húsz',
        '21': 'huszonegy', '22': 'huszonkettő', '23': 'huszonhárom', '24': 'huszonnégy', '25': 'huszonöt',
        '26': 'huszonhat', '27': 'huszonhét', '28': 'huszonnyolc', '29': 'huszonkilenc', '30': 'harminc',
        '40': 'negyven', '50': 'ötven'
    }
    
    # Melléknévi alakok (törvényi hivatkozásokhoz)
    szamok_melleknevi = {
        '1': 'első', '2': 'második', '3': 'harmadik', '4': 'negyedik', '5': 'ötödik',
        '6': 'hatodik', '7': 'hetedik', '8': 'nyolcadik', '9': 'kilencedik', '10': 'tizedik',
        '11': 'tizenegyedik', '12': 'tizenkettedik', '13': 'tizenharmadik', '14': 'tizennegyedik', '15': 'tizenötödik',
        '16': 'tizenhatodik', '17': 'tizenhetedik', '18': 'tizennyolcadik', '19': 'tizenkilencedik', '20': 'huszadik',
        '21': 'huszonegyedik', '22': 'huszonkettedik', '23': 'huszonharmadik', '24': 'huszonnegyedik', '25': 'huszonötödik',
        '26': 'huszonhatodik', '27': 'huszonhetedik', '28': 'huszonnyolcadik', '29': 'huszonkilencedik', '30': 'harmincadik',
        '31': 'harmincegyedik', '37': 'harminchetedik', '40': 'negyvenedik', '50': 'ötvenedik', '52': 'ötvenkettedik',
        '54': 'ötvennegyedik', '58': 'ötvennyolcadik', '69': 'hatvankilencedik', '89': 'nyolcvankilencedik',
        '90': 'kilencvenedik', '137': 'százharminchetedik', '156': 'százötvenhatodik', '163': 'százhatvanharmadik',
        '169': 'százhatvankilencedik', '179': 'százhetvenkilencedik', '193': 'százkilencvenharmadik',
        '215': 'kétszáztizenötödik', '519': 'ötszáztizenkilencedik', '520': 'ötszázhuszadik',
        '523': 'ötszázharmadik', '563': 'ötszázhatvanharmadik', '587': 'ötszáznyolcvanhetedik'
    }
    
    # Segédfüggvény: szám melléknévi alakjának generálása
    def szam_melleknevi(szam_str):
        """Szám melléknévi alakjának generálása"""
        if szam_str in szamok_melleknevi:
            return szamok_melleknevi[szam_str]
        
        # Nagyobb számok kezelése (egyelőre visszatérünk a számmal)
        # Jövőben itt lehetne algoritmus a számok melléknévi alakjának generálására
        try:
            szam = int(szam_str)
            # Ha nincs a szótárban, használjuk az alanyeseti alakot + "edik" végződés
            if szam <= 100:
                return szamok.get(szam_str, szam_str) + 'edik'
        except:
            pass
        return szam_str
    
    # Segédfüggvény: szám melléknévi alakjának generálása
    def szam_melleknevi(szam_str):
        """Szám melléknévi alakjának generálása"""
        if szam_str in szamok_melleknevi:
            return szamok_melleknevi[szam_str]
        # Ha nincs a szótárban, használjuk az alanyeseti alakot (a nagy számoknál)
        return szamok.get(szam_str, szam_str)
    
    # Ptk. 5:23. § mintájú hivatkozások kezelése - MELLÉKNÉVI alakban!
    def helyettesit_ptk_hivatkozas(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        bekezdes = match.group(4) if match.group(4) else ''  # A 4. csoport a zárójelben lévő szám
        
        # Melléknévi alakokat használunk a törvényi hivatkozásokban
        konyv_szoveg = szam_melleknevi(konyv)
        paragrafus_szoveg = szam_melleknevi(paragrafus)
        
        if bekezdes:
            # A bekezdés számát is melléknévi alakban írjuk
            bekezdes_szoveg = szam_melleknevi(bekezdes)
            return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {bekezdes_szoveg} bekezdése"
        else:
            return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusa"
    
    # Ptk. 5:23. § hivatkozások - kezeljük MINDKÉT formátumot: "Ptk." és "Polgári Törvénykönyv"
    # Először a rövidített formátumot (Ptk.) kezeljük
    def helyettesit_ptk_rovid(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        bekezdes = match.group(4) if match.group(4) else ''
        
        konyv_szoveg = szamok_melleknevi.get(konyv, konyv)
        paragrafus_szoveg = szamok_melleknevi.get(paragrafus, paragrafus)
        
        if bekezdes:
            bekezdes_szoveg = szamok_melleknevi.get(bekezdes, bekezdes)
            return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {bekezdes_szoveg} bekezdése"
        else:
            return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusa"
    
    # Ptk. rövidített formátum kezelése (még mielőtt a rovidites_kibontas átalakítaná)
    # Kezeljük a "§-a" és "§-e" formátumokat is (ragok)
    def helyettesit_ptk_rovid_rag(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        konyv_szoveg = szam_melleknevi(konyv)
        paragrafus_szoveg = szam_melleknevi(paragrafus)
        return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusa"
    
    # Ptk. 4:21. § (2)-(3) bekezdései formátum (több bekezdésre hivatkozás)
    def helyettesit_ptk_tobb_bekezdes(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        elso_bekezdes = match.group(3)
        masodik_bekezdes = match.group(4)
        konyv_szoveg = szam_melleknevi(konyv)
        paragrafus_szoveg = szam_melleknevi(paragrafus)
        elso_szoveg = szam_melleknevi(elso_bekezdes)
        masodik_szoveg = szam_melleknevi(masodik_bekezdes)
        return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {elso_szoveg}-től {masodik_szoveg} bekezdései"
    
    # Ptk. 4:21. § (2)-(3) bekezdései formátum kezelése
    szoveg = re.sub(r'Ptk\.\s*(\d+):(\d+)\.\s*§\s*\((\d+)\)-\((\d+)\)\s*bekezdései', helyettesit_ptk_tobb_bekezdes, szoveg)
    
    # Ptk. 6:587. §-a formátum (raggal)
    szoveg = re.sub(r'Ptk\.\s*(\d+):(\d+)\.\s*§-[ae]\s', helyettesit_ptk_rovid_rag, szoveg)
    
    # Ptk. 2:8. § (1) formátum (zárójeles bekezdéssel - egyetlen bekezdés)
    szoveg = re.sub(r'Ptk\.\s*(\d+):(\d+)\.\s*§\s*(\((\d+)\))?', helyettesit_ptk_rovid, szoveg)
    
    # Most már "Polgári Törvénykönyv" formátum kezelése (ha a rovidites_kibontas már átalakította)
    szoveg = re.sub(r'Polgári Törvénykönyv\s*(\d+):(\d+)\.\s*§\s*(\((\d+)\))?', helyettesit_ptk_hivatkozas, szoveg)
    
    # Dupla "A A" javítása
    szoveg = re.sub(r'A\s+A\s+Polgári', 'A Polgári', szoveg)
    
    # "paragrafusa alapján" előtti dupla "A" javítása
    szoveg = re.sub(r'\sa\s+A\s+Polgári', ' a Polgári', szoveg)
    szoveg = re.sub(r'\.\s+A\s+Polgári', '. A Polgári', szoveg)
    
    # Polgári Törvénykönyv (2)-(3) bekezdései formátum (több bekezdésre hivatkozás)
    def helyettesit_polgar_tobb_bekezdes(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        elso_bekezdes = match.group(3)
        masodik_bekezdes = match.group(4)
        konyv_szoveg = szam_melleknevi(konyv)
        paragrafus_szoveg = szam_melleknevi(paragrafus)
        elso_szoveg = szam_melleknevi(elso_bekezdes)
        masodik_szoveg = szam_melleknevi(masodik_bekezdes)
        return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {elso_szoveg}-től {masodik_szoveg} bekezdései"
    
    # Polgári Törvénykönyv (2)-(3) bekezdései formátum kezelése
    szoveg = re.sub(r'Polgári Törvénykönyv\s*(\d+):(\d+)\.\s*§\s*\((\d+)\)-\((\d+)\)\s*bekezdései', helyettesit_polgar_tobb_bekezdes, szoveg)
    
    # Ptk. 5:17. § (1) bekezdése formátum - MELLÉKNÉVI alakban!
    # Figyeljünk, hogy ne legyen dupla "bekezdése"!
    szoveg = re.sub(r'Polgári Törvénykönyv\s*(\d+):(\d+)\.\s*§\s*\((\d+)\)\s*bekezdése(?:\s+bekezdése)?', 
                   lambda m: f"A Polgári Törvénykönyv {szam_melleknevi(m.group(1))} könyvének {szam_melleknevi(m.group(2))} paragrafusának {szam_melleknevi(m.group(3))} bekezdése", 
                   szoveg)
    
    # A (2) bekezdés formátum - MELLÉKNÉVI alakban!
    szoveg = re.sub(r'A\s*\((\d+)\)\s*bekezdés', 
                   lambda m: f"A {szam_melleknevi(m.group(1))} bekezdés", 
                   szoveg)
    
    # "paragrafusa1 bekezdése" -> "paragrafusának első bekezdése" javítás - MELLÉKNÉVI alakban!
    szoveg = re.sub(r'paragrafusa(\d+)', lambda m: f"paragrafusának {szam_melleknevi(m.group(1))}", szoveg)
    
    # "58 paragrafusának" -> "ötvennyolcadik paragrafusának" javítás (szóközzel elválasztva)
    szoveg = re.sub(r'\s+(\d+)\s+paragrafus', lambda m: f" {szam_melleknevi(m.group(1))} paragrafus", szoveg)
    
    # "A 2 bekezdés" -> "A második bekezdés" - MELLÉKNÉVI alakban!
    szoveg = re.sub(r'A\s+(\d+)\s+bekezdés', lambda m: f"A {szam_melleknevi(m.group(1))} bekezdés", szoveg)
    
    # Dupla "bekezdése" javítása
    szoveg = re.sub(r'\s+bekezdése\s+bekezdése', ' bekezdése', szoveg)
    
    # "paragrafusa-alapján" -> "paragrafusa alapján" (szóköz hiánya)
    szoveg = re.sub(r'paragrafusa([a-z])', r'paragrafusa \1', szoveg)
    
    # "paragrafusa-a" -> "paragrafusa" (felesleges kötőjel)
    szoveg = re.sub(r'paragrafusa-\s*a\s', 'paragrafusa ', szoveg)
    
    return szoveg

def eltavolit_speciális_karakterek(szoveg):
    """Speciális karakterek eltávolítása vagy szöveggé alakítása"""
    # Zárójelek eltávolítása, tartalom megtartása
    szoveg = re.sub(r'\(([^)]+)\)', r'\1', szoveg)
    
    # Nyilak szöveggé alakítása
    szoveg = szoveg.replace('->', 'akkor következik')
    szoveg = szoveg.replace('→', 'akkor következik')
    
    return szoveg

def latin_fonetikus(szoveg):
    """Latin kifejezések fonetikusan"""
    latin = {
        'numerus clausus': 'numerusz klauzusz',
        'Nemo plus iuris': 'Nemo plusz jürisz',
        'Traditio': 'Tradíció',
        'Brevi manu traditio': 'Brevi manu tradíció',
        'Constitutum possessorium': 'Konstitútum possesszorium',
        'Longa manu traditio': 'Longa manu tradíció',
        'Cessi vindicatio': 'Cessi vindikáció'
    }
    
    for latin_kifejezes, fonetikus in latin.items():
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

def rovidites_kibontas(szoveg):
    """Rövidítések kibontása"""
    roviditesek = {
        'pl.': 'például',
        'Ptk.': 'Polgári Törvénykönyv',
        'stb.': 'és így tovább',
        'ld.': 'lásd',
        'vm.': 'valamely',
        'INY': 'ingatlan-nyilvántartás'
    }
    
    for rovidites, kibontott in roviditesek.items():
        szoveg = szoveg.replace(rovidites, kibontott)
    
    return szoveg

def feldolgoz(szoveg):
    """Fő feldolgozási függvény"""
    # FONTOS SORREND: Először a törvényi hivatkozások kezelése (Ptk. formátumban),
    # majd a rövidítések kibontása, végül a többi feldolgozás
    
    # 1. Törvényi hivatkozások kezelése FONETIKUSAN (még Ptk. formátumban)
    # Ez MEGELŐZI a rövidítések kibontását!
    szoveg = fonetikus_szamok(szoveg)
    
    # 2. Rövidítések kibontása (már feldolgozott törvényi hivatkozásokkal)
    szoveg = rovidites_kibontas(szoveg)
    
    # 3. Latin kifejezések fonetikusan
    szoveg = latin_fonetikus(szoveg)
    
    # 4. Speciális karakterek
    szoveg = eltavolit_speciális_karakterek(szoveg)
    
    # 5. Felsorolások átalakítása
    szoveg = felsorolas_atalakit(szoveg)
    
    # 6. Többszörös szóközök eltávolítása
    szoveg = re.sub(r'\s+', ' ', szoveg)
    
    # 7. Többszörös pontok eltávolítása
    szoveg = re.sub(r'\.{2,}', '.', szoveg)
    
    return szoveg.strip()

def beolvas_fajl(utvonal):
    """Fájl beolvasása"""
    with open(utvonal, 'r', encoding='utf-8') as f:
        return f.read()

def main(mappa_utvonal=None):
    """
    Fő feldolgozási függvény
    
    Args:
        mappa_utvonal: A mappa elérési útja, ahol a kerdesek.txt, valaszok.txt és magyarazatok.txt található
                      Ha None, akkor a jelenlegi mappát használja
    """
    import sys
    
    # Ha nincs megadva mappa, próbáljuk a parancssori argumentumokat
    if mappa_utvonal is None:
        if len(sys.argv) > 1:
            mappa_utvonal = sys.argv[1]
        else:
            # Alapértelmezett: jelenlegi szkript mappája
            mappa_utvonal = os.path.dirname(os.path.abspath(__file__))
    
    # Normalizáljuk az útvonalat
    mappa_utvonal = os.path.abspath(mappa_utvonal)
    
    # Ellenőrizzük, hogy létezik-e a mappa
    if not os.path.isdir(mappa_utvonal):
        print(f"Hiba: A megadott mappa nem létezik: {mappa_utvonal}")
        return
    
    # Fájlok útvonalai
    kerdesek_utvonal = os.path.join(mappa_utvonal, 'kerdesek.txt')
    valaszok_utvonal = os.path.join(mappa_utvonal, 'valaszok.txt')
    magyarazatok_utvonal = os.path.join(mappa_utvonal, 'magyarazatok.txt')
    kimenet_utvonal = os.path.join(mappa_utvonal, 'feldolgozott_tananyag', 'tananyag.txt')
    
    # Ellenőrizzük, hogy léteznek-e a bemeneti fájlok
    for fajl_utvonal, fajl_nev in [(kerdesek_utvonal, 'kerdesek.txt'), 
                                    (valaszok_utvonal, 'valaszok.txt'), 
                                    (magyarazatok_utvonal, 'magyarazatok.txt')]:
        if not os.path.isfile(fajl_utvonal):
            print(f"Figyelem: A {fajl_nev} fájl nem található a mappában: {mappa_utvonal}")
    
    print(f"Feldolgozás indítása...")
    print(f"Mappa: {mappa_utvonal}")
    
    # Fájlok beolvasása
    kerdesek = beolvas_fajl(kerdesek_utvonal)
    valaszok = beolvas_fajl(valaszok_utvonal)
    magyarazatok = beolvas_fajl(magyarazatok_utvonal)
    
    # Tételek szétválasztása - jobb regex: szám pont szóköz a sor elején
    kerdes_tetelek = re.split(r'^\s*\d+\.\s+', kerdesek, flags=re.MULTILINE)
    valasz_tetelek = re.split(r'^\s*\d+\.\s+', valaszok, flags=re.MULTILINE)
    magyarazat_tetelek = re.split(r'^\s*\d+\.\s+', magyarazatok, flags=re.MULTILINE)
    
    # Az első elem lehet üres, ha van sorszám a legelején
    if kerdes_tetelek and not kerdes_tetelek[0].strip():
        kerdes_tetelek = kerdes_tetelek[1:]
    if valasz_tetelek and not valasz_tetelek[0].strip():
        valasz_tetelek = valasz_tetelek[1:]
    if magyarazat_tetelek and not magyarazat_tetelek[0].strip():
        magyarazat_tetelek = magyarazat_tetelek[1:]
    
    kimenet = []
    javitasok = []
    
    for i in range(min(50, len(kerdes_tetelek), len(valasz_tetelek), len(magyarazat_tetelek))):
        kerdes = kerdes_tetelek[i].strip() if i < len(kerdes_tetelek) else ''
        valasz = valasz_tetelek[i].strip() if i < len(valasz_tetelek) else ''
        magyarazat = magyarazat_tetelek[i].strip() if i < len(magyarazat_tetelek) else ''
        
        # Kombinálás - intelligens egyesítés: ha a magyarázat tartalmazza a választ, csak a magyarázatot használjuk
        # Különben kombináljuk őket
        if valasz and magyarazat:
            # Ha a válasz benne van a magyarázatban, csak a magyarázatot használjuk
            if valasz.strip() in magyarazat:
                kombinált = magyarazat.strip()
            else:
                # Egyesítés narratív formában
                kombinált = f"{valasz} {magyarazat}".strip()
        elif magyarazat:
            kombinált = magyarazat.strip()
        elif valasz:
            kombinált = valasz.strip()
        else:
            kombinált = ''
        
        # Feldolgozás
        feldolgozott = feldolgoz(kombinált)
        
        # Duplikált mondatok eltávolítása
        mondatok = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÖŐÚÜŰ])', feldolgozott)
        mondatok = [m.strip() for m in mondatok if m.strip()]
        
        # Duplikációk eltávolítása - jobb algoritmus: hasonlóság alapján
        lathatott_mondatok = set()
        egyedi_mondatok = []
        for mondat in mondatok:
            mondat_rovid = mondat[:80].lower().strip() if len(mondat) > 80 else mondat.lower().strip()  # Első 80 karakter normalizálva
            mondat_rovid = re.sub(r'\s+', ' ', mondat_rovid)  # Szóközök normalizálása
            if mondat_rovid not in lathatott_mondatok and len(mondat_rovid) > 10:  # Minimum hossz
                lathatott_mondatok.add(mondat_rovid)
                egyedi_mondatok.append(mondat)
        
        mondatok = egyedi_mondatok
        
        # Üres mondatok eltávolítása és végpontok biztosítása
        tiszta_mondatok = []
        for mondat in mondatok:
            mondat = mondat.strip()
            if mondat:
                # Ha nincs végpont, adjunk hozzá
                if not re.search(r'[.!?]$', mondat):
                    mondat += '.'
                tiszta_mondatok.append(mondat)
        
        # Bekezdésformázás - FONTOS: Egy tétel minden mondatát egyetlen folyamatos bekezdésbe foglaljuk!
        # Nincs bekezdésformázás a mondatok száma alapján, mert minden tétel egy logikai blokk!
        # Egyetlen bekezdés: minden mondat szóközzel elválasztva, NINCS üres sor a blokkon belül!
        feldolgozott_szoveg = ' '.join(tiszta_mondatok)
        # Többszörös szóközök normalizálása
        feldolgozott_szoveg = re.sub(r'\s+', ' ', feldolgozott_szoveg)
        feldolgozott_szoveg = feldolgozott_szoveg.strip()
        
        kimenet.append(feldolgozott_szoveg)
    
    # Kimenet írása
    kimeneti_szoveg = '\n\n\n'.join(kimenet)
    
    # Kimeneti mappa létrehozása, ha nem létezik
    kimenet_mappa = os.path.dirname(kimenet_utvonal)
    os.makedirs(kimenet_mappa, exist_ok=True)
    
    with open(kimenet_utvonal, 'w', encoding='utf-8') as f:
        f.write(kimeneti_szoveg)
    
    # Javítások fájl (ha van)
    if javitasok:
        javitasok_utvonal = os.path.join(kimenet_mappa, 'javitasok.txt')
        with open(javitasok_utvonal, 'w', encoding='utf-8') as f:
            f.write('\n'.join(javitasok))
    
    # Blokkok számának meghatározása (nem üres blokkok)
    blokkok_szama = len([b for b in kimenet if b.strip()])
    
    print(f"Feldolgozás kész! {len(kimenet)} tétel feldolgozva.")
    print(f"Létrehozott blokkok száma a dokumentumban: {blokkok_szama}")
    print(f"Kimeneti fájl: {kimenet_utvonal}")

if __name__ == '__main__':
    main()

