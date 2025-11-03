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
    
    # Melléknévi alakok (törvényi hivatkozásokhoz) - 1-900 közötti összes szám
    # Generálva a szamok_generalas.py segítségével
    from szamok_generalas import general_melleknevi_alakok
    szamok_melleknevi = general_melleknevi_alakok(900)
    
    # Segédfüggvény: szám melléknévi alakjának generálása
    def szam_melleknevi(szam_str):
        """Szám melléknévi alakjának generálása"""
        if szam_str in szamok_melleknevi:
            return szamok_melleknevi[szam_str]
        # Ha nincs a szótárban (900 felett), használjuk az alanyeseti alakot
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
    
    # Ptk. 4:21. § (2)-(3) bekezdései/bekezdése formátum (több bekezdésre hivatkozás)
    def helyettesit_ptk_tobb_bekezdes(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        elso_bekezdes = match.group(3)
        masodik_bekezdes = match.group(4)
        konyv_szoveg = szam_melleknevi(konyv)
        paragrafus_szoveg = szam_melleknevi(paragrafus)
        elso_num = int(elso_bekezdes)
        masodik_num = int(masodik_bekezdes)
        
        # Felsorolás létrehozása: "második és harmadik" vagy "második, harmadik és negyedik"
        bekezdes_lista = []
        for num in range(elso_num, masodik_num + 1):
            bekezdes_szoveg = szam_melleknevi(str(num))
            bekezdes_lista.append(bekezdes_szoveg)
        
        # Felsorolás formázása
        if len(bekezdes_lista) == 2:
            bekezdes_felsorolas = f"{bekezdes_lista[0]} és {bekezdes_lista[1]}"
        else:
            # Több mint 2: "második, harmadik és negyedik"
            bekezdes_felsorolas = ', '.join(bekezdes_lista[:-1]) + ' és ' + bekezdes_lista[-1]
        
        return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {bekezdes_felsorolas} bekezdése"
    
    # Ptk. 4:21. § (2)-(3) bekezdései/bekezdése formátum kezelése - MINDKÉT formátumot!
    # Fontos: ez MEGELŐZI az egyszerű (2) bekezdése formátum kezelését!
    szoveg = re.sub(r'Ptk\.\s*(\d+):(\d+)\.\s*§\s*\((\d+)\)-\((\d+)\)\s*(bekezdései?)\b', helyettesit_ptk_tobb_bekezdes, szoveg)
    
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
    
    # Polgári Törvénykönyv (2)-(3) bekezdései/bekezdése formátum (több bekezdésre hivatkozás)
    def helyettesit_polgar_tobb_bekezdes(match):
        konyv = match.group(1)
        paragrafus = match.group(2)
        elso_bekezdes = match.group(3)
        masodik_bekezdes = match.group(4)
        ige = match.group(5) if match.group(5) else 'bekezdései'  # "bekezdése" vagy "bekezdései"
        konyv_szoveg = szam_melleknevi(konyv)
        paragrafus_szoveg = szam_melleknevi(paragrafus)
        elso_szoveg = szam_melleknevi(elso_bekezdes)
        masodik_szoveg = szam_melleknevi(masodik_bekezdes)
        # Ha "bekezdése" van (egyes szám), akkor "bekezdései"-re változtatjuk (többes szám)
        if 'bekezdése' == ige and 'bekezdései' != ige:
            ige = 'bekezdései'
        return f"A Polgári Törvénykönyv {konyv_szoveg} könyvének {paragrafus_szoveg} paragrafusának {elso_szoveg}-től {masodik_szoveg} {ige}"
    
    # Polgári Törvénykönyv (2)-(3) bekezdései/bekezdése formátum kezelése - MINDKÉT formátumot!
    # Fontos: ez MEGELŐZI az egyszerű (2) bekezdése formátum kezelését!
    szoveg = re.sub(r'Polgári Törvénykönyv\s*(\d+):(\d+)\.\s*§\s*\((\d+)\)-\((\d+)\)\s*(bekezdései?)\b', helyettesit_polgar_tobb_bekezdes, szoveg)
    
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

def melleknevi_to_szam(melleknevi_szoveg):
    """Melléknévi alak visszakonverziója számmá"""
    # Dinamikus generálás a szamok_generalas.py segítségével
    from szamok_generalas import general_melleknevi_alakok
    szamok_melleknevi_temp = general_melleknevi_alakok(900)
    
    # Fordított lookup - minden értéket kulccá teszünk
    for szam, alak in szamok_melleknevi_temp.items():
        if alak == melleknevi_szoveg:
            return szam
    return None

def torveny_fajl_beolvasas(torveny_fajl_utvonal):
    """Beolvassa és strukturálja a törvényi fájlt"""
    torveny_index = {}
    
    try:
        with open(torveny_fajl_utvonal, 'r', encoding='utf-8') as f:
            sorok = f.readlines()
    except FileNotFoundError:
        print(f"Figyelem: A törvényi fájl nem található: {torveny_fajl_utvonal}")
        return torveny_index
    
    # Paragrafusok keresése: KÖNYV:PARAGRAFUS. § formátum
    # Példa: "4:32. § [Cím]" vagy "2:8. § [A cselekvőképesség]"
    paragrafus_pattern = r'^(\d+):(\d+)\.\s*§\s*(?:\[[^\]]+\])?\s*'
    
    jelenlegi_paragrafus = None
    jelenlegi_bekezdes = None
    jelenlegi_szoveg = []
    
    i = 0
    while i < len(sorok):
        sor = sorok[i].rstrip()  # Csak jobbról vágjuk le a whitespace-t
        
        # Paragrafus azonosítás
        paragrafus_match = re.match(paragrafus_pattern, sor)
        if paragrafus_match:
            # Előző bekezdés vagy paragrafus mentése
            if jelenlegi_paragrafus:
                kulcs = f"{jelenlegi_paragrafus['konyv']}:{jelenlegi_paragrafus['paragrafus']}"
                if kulcs not in torveny_index:
                    torveny_index[kulcs] = {}
                
                if jelenlegi_szoveg:
                    szoveg = ' '.join(jelenlegi_szoveg).strip()
                    szoveg = re.sub(r'\s+', ' ', szoveg)  # Többszörös szóközök eltávolítása
                    if szoveg:
                        if jelenlegi_bekezdes:
                            torveny_index[kulcs][jelenlegi_bekezdes] = szoveg
                        else:
                            torveny_index[kulcs][""] = szoveg
            
            # Új paragrafus kezdése
            jelenlegi_paragrafus = {
                'konyv': paragrafus_match.group(1),
                'paragrafus': paragrafus_match.group(2)
            }
            jelenlegi_bekezdes = None
            jelenlegi_szoveg = []
            i += 1
            continue
        
        # Bekezdés azonosítás: (1), (2), stb.
        bekezdes_match = re.match(r'^\((\d+)\)\s*(.*)$', sor)
        if bekezdes_match:
            # Előző bekezdés mentése (ha van)
            if jelenlegi_paragrafus and jelenlegi_bekezdes is not None and jelenlegi_szoveg:
                kulcs = f"{jelenlegi_paragrafus['konyv']}:{jelenlegi_paragrafus['paragrafus']}"
                if kulcs not in torveny_index:
                    torveny_index[kulcs] = {}
                
                szoveg = ' '.join(jelenlegi_szoveg).strip()
                szoveg = re.sub(r'\s+', ' ', szoveg)
                if szoveg:
                    torveny_index[kulcs][jelenlegi_bekezdes] = szoveg
            
            # Új bekezdés kezdése
            jelenlegi_bekezdes = bekezdes_match.group(1)
            kezdo_szoveg = bekezdes_match.group(2).strip()
            jelenlegi_szoveg = [kezdo_szoveg] if kezdo_szoveg else []
            i += 1
            continue
        
        # Szöveg sor hozzáadása (ha van paragrafus aktív)
        if jelenlegi_paragrafus:
            # Szűrünk: kihagyjuk a formázási, HTML/PDF export maradványokat
            if sor.strip():
                # Kiszűrünk:
                # - URL-ek (https://, http://)
                # - HTML/PDF export maradványok (njt.hu, getPrintWindow)
                # - Oldalszámozás (- N -)
                # - Dátum formátumok (YYYY. MM. DD. HH:MM)
                # - Hatályossági információk (Hatályos:, Lekérdezés ideje:)
                # - Törvény címek külön sorban (2013. évi V. törvény)
                # - Hivatkozási megjegyzések (169A, 170A + paragrafus hivatkozás + "a 2020: CLXVI. törvény")
                
                sor_clean = sor.strip()
                
                # URL-ek és HTML/PDF export maradványok
                if re.search(r'https?://|njt\.hu|getPrintWindow', sor_clean, re.IGNORECASE):
                    i += 1
                    continue
                
                # Oldalszámozás: "- N -" vagy "- NN -"
                if re.match(r'^-\s*\d+\s*-$', sor_clean):
                    i += 1
                    continue
                
                # Dátum formátumok: "2025. 11. 01. 11:54" vagy hasonló
                if re.match(r'^\d{4}\.\s+\d{1,2}\.\s+\d{1,2}\.\s+\d{1,2}:\d{2}', sor_clean):
                    i += 1
                    continue
                
                # Hatályossági információk
                if re.match(r'^Hatályos:|^Lekérdezés ideje:', sor_clean, re.IGNORECASE):
                    i += 1
                    continue
                
                # Törvény címek külön sorban (nem paragrafus)
                if re.match(r'^\d{4}\.\s+évi\s+[IVX]+\.\s+törvény', sor_clean, re.IGNORECASE):
                    i += 1
                    continue
                
                if re.match(r'^a\s+Polgári\s+Törvénykönyvről$', sor_clean, re.IGNORECASE):
                    i += 1
                    continue
                
                # Hivatkozási megjegyzések: "169A 4:27. § ..." vagy "170A ..." + "a 2020: CLXVI. törvény"
                if re.match(r'^\d+[A-Z]\s+\d+:\d+\.', sor_clean):
                    i += 1
                    continue
                
                if re.search(r'\d{4}:\s*[IVX]+\.\s+törvény\s+\d+\.\s*§', sor_clean):
                    i += 1
                    continue
                
                # Ha minden rendben, hozzáadjuk
                jelenlegi_szoveg.append(sor_clean)
            # Ha üres sor és van már szöveg, azt is megtartjuk (szóközként)
        
        i += 1
    
    # Utolsó bekezdés/paragrafus mentése
    if jelenlegi_paragrafus:
        kulcs = f"{jelenlegi_paragrafus['konyv']}:{jelenlegi_paragrafus['paragrafus']}"
        if kulcs not in torveny_index:
            torveny_index[kulcs] = {}
        
        if jelenlegi_szoveg:
            szoveg = ' '.join(jelenlegi_szoveg).strip()
            szoveg = re.sub(r'\s+', ' ', szoveg)
            if szoveg:
                if jelenlegi_bekezdes is not None:
                    torveny_index[kulcs][jelenlegi_bekezdes] = szoveg
                else:
                    torveny_index[kulcs][""] = szoveg
    
    return torveny_index

def torvenyi_hivatkozasok_kinyerese(feldolgozott_szoveg):
    """Kinyeri az összes törvényi hivatkozást a feldolgozott szövegből"""
    hivatkozasok = []
    
    # Minta: "A Polgári Törvénykönyv {konyv} könyvének {paragrafus} paragrafusának {bekezdes} bekezdése"
    # Vagy: "A Polgári Törvénykönyv {konyv} könyvének {paragrafus} paragrafusa"
    # Vagy: "A Polgári Törvénykönyv {konyv} könyvének {paragrafus} paragrafusának {elso}-től {masodik} bekezdései"
    
    # Először a több bekezdéses formátum
    pattern_tobb = r'A Polgári Törvénykönyv\s+(\w+)\s+könyvének\s+(\w+)\s+paragrafusának\s+(\w+)-től\s+(\w+)\s+bekezdései'
    matches = re.finditer(pattern_tobb, feldolgozott_szoveg)
    for match in matches:
        konyv = match.group(1)
        paragrafus = match.group(2)
        elso_bekezdes = match.group(3)
        masodik_bekezdes = match.group(4)
        # Visszakonverzió számmá
        konyv_szam = melleknevi_to_szam(konyv)
        paragrafus_szam = melleknevi_to_szam(paragrafus)
        elso_szam = melleknevi_to_szam(elso_bekezdes)
        masodik_szam = melleknevi_to_szam(masodik_bekezdes)
        if konyv_szam and paragrafus_szam and elso_szam and masodik_szam:
            hivatkozasok.append({
                'konyv': konyv_szam,
                'paragrafus': paragrafus_szam,
                'bekezdes': elso_szam,
                'masodik_bekezdes': masodik_szam,
                'tipus': 'tobb_bekezdes'
            })
    
    # Egy bekezdéses formátum
    pattern_egy = r'A Polgári Törvénykönyv\s+(\w+)\s+könyvének\s+(\w+)\s+paragrafusának\s+(\w+)\s+bekezdése'
    matches = re.finditer(pattern_egy, feldolgozott_szoveg)
    for match in matches:
        konyv = match.group(1)
        paragrafus = match.group(2)
        bekezdes = match.group(3)
        konyv_szam = melleknevi_to_szam(konyv)
        paragrafus_szam = melleknevi_to_szam(paragrafus)
        bekezdes_szam = melleknevi_to_szam(bekezdes)
        if konyv_szam and paragrafus_szam and bekezdes_szam:
            hivatkozasok.append({
                'konyv': konyv_szam,
                'paragrafus': paragrafus_szam,
                'bekezdes': bekezdes_szam,
                'tipus': 'egy_bekezdes'
            })
    
    # Paragrafus formátum (nincs bekezdés)
    pattern_paragrafus = r'A Polgári Törvénykönyv\s+(\w+)\s+könyvének\s+(\w+)\s+paragrafusa'
    matches = re.finditer(pattern_paragrafus, feldolgozott_szoveg)
    for match in matches:
        konyv = match.group(1)
        paragrafus = match.group(2)
        konyv_szam = melleknevi_to_szam(konyv)
        paragrafus_szam = melleknevi_to_szam(paragrafus)
        if konyv_szam and paragrafus_szam:
            hivatkozasok.append({
                'konyv': konyv_szam,
                'paragrafus': paragrafus_szam,
                'tipus': 'paragrafus'
            })
    
    return hivatkozasok

def torvenyi_szoveg_kinyerese(torveny_index, konyv, paragrafus, bekezdes=None, masodik_bekezdes=None):
    """Kinyeri a törvényi szöveget a strukturált indexből"""
    kulcs = f"{konyv}:{paragrafus}"
    
    if kulcs not in torveny_index:
        return None
    
    paragrafus_data = torveny_index[kulcs]
    
    # Ha több bekezdésre hivatkoznak
    if masodik_bekezdes:
        bekezdesek = []
        for i in range(int(bekezdes), int(masodik_bekezdes) + 1):
            bekezdes_str = str(i)
            if bekezdes_str in paragrafus_data:
                bekezdesek.append(paragrafus_data[bekezdes_str])
        if bekezdesek:
            return ' '.join(bekezdesek)
        return None
    
    # Ha egy bekezdésre hivatkoznak
    if bekezdes:
        bekezdes_str = str(bekezdes)
        if bekezdes_str in paragrafus_data:
            return paragrafus_data[bekezdes_str]
        return None
    
    # Ha csak a paragrafusra hivatkoznak (nincs bekezdés)
    if "" in paragrafus_data:
        return paragrafus_data[""]
    
    # Ha nincs üres kulcs, összefűzzük az összes bekezdést
    if paragrafus_data:
        return ' '.join(paragrafus_data.values())
    
    return None

def torvenyi_szoveg_fonetikus_alakitas(torvenyi_szoveg):
    """A törvényi szövegben lévő bekezdés-hivatkozásokat fonetikussá alakítja"""
    from szamok_generalas import general_melleknevi_alakok
    szamok_melleknevi = general_melleknevi_alakok(900)
    
    # Minta: "(1) bekezdés", "az (1) bekezdésben", "a (2) bekezdés szerint", "(1) bekezdés a) pontja"
    # Visszahelyettesítés: melléknévi alak (első, második, stb.)
    
    def helyettesit_bekezdes_hivatkozas(match):
        elotte = match.group(1) or ""  # "az ", "a ", "", stb.
        szam_str = match.group(2)  # a szám
        utana = match.group(3)  # "bekezdés", "bekezdésben", "bekezdés szerint", stb.
        
        melleknevi = szamok_melleknevi.get(szam_str, szam_str)
        # Szóközt beteszünk a melléknév és "bekezdés" közé
        if elotte:
            return f"{elotte}{melleknevi} {utana}"
        else:
            return f"{melleknevi} {utana}"
    
    # Különböző formátumok: "(1) bekezdés", "az (1) bekezdésben", "a (2) bekezdés szerint", "(1) bekezdés a) pontja"
    # Regex: (az|a|Az|A) opcionális, majd (szám zárójelben), majd "bekezdés" + további szöveg (szóközökkel)
    torvenyi_szoveg = re.sub(
        r'(az\s+|a\s+|Az\s+|A\s+)?\((\d+)\)\s+(bekezdés(?:\s+[^\s]+)*?)',
        helyettesit_bekezdes_hivatkozas,
        torvenyi_szoveg
    )
    
    return torvenyi_szoveg

def torvenyi_szoveg_formazasa(konyv_szoveg, paragrafus_szoveg, bekezdes_szoveg, torvenyi_szoveg, tipus):
    """Formázza a törvényi szöveget a kívánt formátumban"""
    # Először a törvényi szövegben lévő bekezdés-hivatkozásokat fonetikussá alakítjuk
    torvenyi_szoveg = torvenyi_szoveg_fonetikus_alakitas(torvenyi_szoveg)
    
    if tipus == 'tobb_bekezdes':
        # A bekezdes_szoveg már előkészített felsorolás: "második és harmadik" vagy "második, harmadik és negyedik"
        return f"A Polgári Törvénykönyv szerint a {konyv_szoveg} könyv {paragrafus_szoveg} paragrafusának {bekezdes_szoveg} bekezdése: {torvenyi_szoveg}"
    elif tipus == 'egy_bekezdes':
        return f"A Polgári Törvénykönyv szerint a {konyv_szoveg} könyv {paragrafus_szoveg} paragrafusának {bekezdes_szoveg} bekezdése: {torvenyi_szoveg}"
    else:  # tipus == 'paragrafus'
        return f"A Polgári Törvénykönyv szerint a {konyv_szoveg} könyv {paragrafus_szoveg} paragrafusa: {torvenyi_szoveg}"

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
    
    # Törvényi fájl beolvasása (egyszer, a fő ciklus előtt)
    script_mappa = os.path.dirname(os.path.abspath(__file__))
    torveny_fajl_utvonal = os.path.join(script_mappa, '..', 'Források', '2013. évi V. törvény a Polgári Törvénykönyvről.txt')
    torveny_fajl_utvonal = os.path.normpath(torveny_fajl_utvonal)
    torveny_index = torveny_fajl_beolvasas(torveny_fajl_utvonal)
    
    if not torveny_index:
        print(f"Figyelem: A törvényi fájl üres vagy nem található. A törvényi szövegek beillesztése kihagyva.")
    
    for i in range(min(50, len(kerdes_tetelek), len(valasz_tetelek), len(magyarazat_tetelek))):
        kerdes = kerdes_tetelek[i].strip() if i < len(kerdes_tetelek) else ''
        valasz = valasz_tetelek[i].strip() if i < len(valasz_tetelek) else ''
        magyarazat = magyarazat_tetelek[i].strip() if i < len(magyarazat_tetelek) else ''
        
        # Kombinálás - intelligens egyesítés: ha a magyarázat tartalmazza a választ, csak a magyarázatot használjuk
        # Különben kombináljuk őket, de először ellenőrizzük, hogy nincs-e nagy átfedés
        if valasz and magyarazat:
            valasz_rovid = valasz.strip()[:100].lower()
            magyarazat_rovid = magyarazat.strip()[:100].lower()
            
            # Ha a válasz nagy része benne van a magyarázatban, csak a magyarázatot használjuk
            if valasz.strip() in magyarazat or valasz_rovid in magyarazat.lower():
                kombinált = magyarazat.strip()
            elif magyarazat_rovid in valasz.lower():
                # Ha fordítva: a magyarázat része a válasznak, akkor csak a választ
                kombinált = valasz.strip()
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
        
        # Teljes mondat duplikációk először - ha egy mondat többször szerepel szó szerint
        egyedi_teljes_mondatok = []
        latott_teljes = set()
        for mondat in mondatok:
            mondat_normalizalt_teljes = mondat.lower().strip()
            mondat_normalizalt_teljes = re.sub(r'\s+', ' ', mondat_normalizalt_teljes)
            # Írásjelek eltávolítása a teljes egyezéshez
            mondat_normalizalt_teljes_irasmely = re.sub(r'[.,;:!?]', '', mondat_normalizalt_teljes)
            
            # Teljes egyezés ellenőrzés (írásjelek nélkül is)
            if mondat_normalizalt_teljes not in latott_teljes and mondat_normalizalt_teljes_irasmely not in latott_teljes:
                if len(mondat_normalizalt_teljes) > 30:
                    latott_teljes.add(mondat_normalizalt_teljes)
                    latott_teljes.add(mondat_normalizalt_teljes_irasmely)
                    egyedi_teljes_mondatok.append(mondat)
        
        mondatok = egyedi_teljes_mondatok
        
        # Duplikációk eltávolítása - javított algoritmus: hasonlóság alapján
        lathatott_mondatok = set()
        egyedi_mondatok = []
        for mondat in mondatok:
            # Normalizálás: kisbetűs, szóközök egységesítése, írásjelek eltávolítása a hasonlóság ellenőrzéshez
            mondat_normalizalt = mondat.lower().strip()
            mondat_normalizalt = re.sub(r'\s+', ' ', mondat_normalizalt)
            mondat_normalizalt = re.sub(r'[.,;:!?]', '', mondat_normalizalt)  # Írásjelek eltávolítása
            
            # Első 100 karakter + kulcsszavak alapján hasonlóság ellenőrzés
            mondat_rovid = mondat_normalizalt[:100] if len(mondat_normalizalt) > 100 else mondat_normalizalt
            
            # Kulcsszavak kinyerése (első 3-4 jelentős szó)
            szavak = mondat_normalizalt.split()
            kulcsszavak = ' '.join(szavak[:4]) if len(szavak) >= 4 else ' '.join(szavak)
            
            # Hasonlóság ellenőrzés: ha a rövid verzió vagy a kulcsszavak megegyeznek egy már látott mondattal, akkor duplikáció
            hasonlo = False
            for latott in lathatott_mondatok:
                # Első 50 karakter egyezés (hosszabb mondatoknál)
                if len(mondat_rovid) > 50 and len(latott) > 50:
                    if mondat_rovid[:50] == latott[:50]:
                        hasonlo = True
                        break
                
                # Tartalmazás ellenőrzés: ha egyik mondat tartalmazza a másikat (vagy fordítva)
                if mondat_rovid in latott or latott in mondat_rovid:
                    if len(mondat_rovid) > 40 and len(latott) > 40:
                        # Különbség max 40% lehet
                        kulonbseg = abs(len(mondat_rovid) - len(latott))
                        if kulonbseg < max(len(mondat_rovid), len(latott)) * 0.4:
                            hasonlo = True
                            break
                
                # Kulcsszavak alapján: ha az első jelentős szavak megegyeznek
                if kulcsszavak and len(kulcsszavak) > 25:
                    kulcs_hossz = min(50, len(kulcsszavak))
                    if kulcsszavak[:kulcs_hossz] in latott or latott.startswith(kulcsszavak[:kulcs_hossz]):
                        hasonlo = True
                        break
                
                # Különleges eset: ha ugyanaz a kezdő rész, csak a végben van különbség
                # Például: "A Ptk. a feldúltsági elvet alkalmazza, ami..." vs "A Ptk. a feldúltsági elvet alkalmazza, amely..."
                if len(mondat_rovid) > 40 and len(latott) > 40:
                    # Az első 40 karakter egyezés + hasonló hosszúság
                    if mondat_rovid[:40] == latott[:40]:
                        kulonbseg = abs(len(mondat_rovid) - len(latott))
                        if kulonbseg < 50:  # Max 50 karakter különbség (tágabb tűrés)
                            # További ellenőrzés: a középső rész is hasonló kell legyen
                            kozep_resz_1 = mondat_rovid[40:min(80, len(mondat_rovid))]
                            kozep_resz_2 = latott[40:min(80, len(latott))]
                            # Ha a középső részek is nagyban egyeznek
                            if len(kozep_resz_1) > 20 and len(kozep_resz_2) > 20:
                                if kozep_resz_1[:20] == kozep_resz_2[:20]:
                                    hasonlo = True
                                    break
            
            if not hasonlo and len(mondat_normalizalt) > 20:  # Minimum hossz
                lathatott_mondatok.add(mondat_rovid)
                lathatott_mondatok.add(kulcsszavak)
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
        
        # Törvényi hivatkozások kinyerése és törvényi szövegek beillesztése
        if torveny_index:
            hivatkozasok = torvenyi_hivatkozasok_kinyerese(feldolgozott_szoveg)
            
            # Duplikáció elkerülése: minden egyedi hivatkozás csak egyszer
            latott_hivatkozasok = set()
            torvenyi_szovegek = []
            
            for hiv in hivatkozasok:
                # Egyedi azonosító létrehozása
                hiv_id = f"{hiv['konyv']}:{hiv['paragrafus']}"
                if hiv['tipus'] in ['egy_bekezdes', 'tobb_bekezdes']:
                    hiv_id += f":{hiv.get('bekezdes', '')}"
                if hiv['tipus'] == 'tobb_bekezdes':
                    hiv_id += f"-{hiv.get('masodik_bekezdes', '')}"
                
                if hiv_id not in latott_hivatkozasok:
                    latott_hivatkozasok.add(hiv_id)
                    
                    # Törvényi szöveg kinyerése
                    torvenyi_szoveg = None
                    if hiv['tipus'] == 'tobb_bekezdes':
                        torvenyi_szoveg = torvenyi_szoveg_kinyerese(
                            torveny_index,
                            hiv['konyv'],
                            hiv['paragrafus'],
                            hiv['bekezdes'],
                            hiv['masodik_bekezdes']
                        )
                    elif hiv['tipus'] == 'egy_bekezdes':
                        torvenyi_szoveg = torvenyi_szoveg_kinyerese(
                            torveny_index,
                            hiv['konyv'],
                            hiv['paragrafus'],
                            hiv['bekezdes']
                        )
                    else:  # paragrafus
                        torvenyi_szoveg = torvenyi_szoveg_kinyerese(
                            torveny_index,
                            hiv['konyv'],
                            hiv['paragrafus']
                        )
                    
                    if torvenyi_szoveg:
                        # Fonetikus konverzió a formázáshoz
                        from szamok_generalas import general_melleknevi_alakok
                        szamok_melleknevi_temp = general_melleknevi_alakok(900)
                        konyv_szoveg = szamok_melleknevi_temp.get(hiv['konyv'], hiv['konyv'])
                        paragrafus_szoveg = szamok_melleknevi_temp.get(hiv['paragrafus'], hiv['paragrafus'])
                        
                        if hiv['tipus'] == 'tobb_bekezdes':
                            # Felsorolás létrehozása: "második és harmadik" vagy "második, harmadik és negyedik"
                            elso_num = int(hiv['bekezdes'])
                            masodik_num = int(hiv['masodik_bekezdes'])
                            
                            # Az összes bekezdés melléknévi alakjának generálása
                            bekezdes_lista = []
                            for num in range(elso_num, masodik_num + 1):
                                bekezdes_szoveg = szamok_melleknevi_temp.get(str(num), str(num))
                                bekezdes_lista.append(bekezdes_szoveg)
                            
                            # Felsorolás formázása
                            if len(bekezdes_lista) == 2:
                                bekezdes_felsorolas = f"{bekezdes_lista[0]} és {bekezdes_lista[1]}"
                            else:
                                # Több mint 2: "második, harmadik és negyedik"
                                bekezdes_felsorolas = ', '.join(bekezdes_lista[:-1]) + ' és ' + bekezdes_lista[-1]
                            
                            formazott = torvenyi_szoveg_formazasa(
                                konyv_szoveg, paragrafus_szoveg, bekezdes_felsorolas,
                                torvenyi_szoveg, 'tobb_bekezdes'
                            )
                        elif hiv['tipus'] == 'egy_bekezdes':
                            bekezdes_szoveg = szamok_melleknevi_temp.get(hiv['bekezdes'], hiv['bekezdes'])
                            formazott = torvenyi_szoveg_formazasa(
                                konyv_szoveg, paragrafus_szoveg, bekezdes_szoveg,
                                torvenyi_szoveg, 'egy_bekezdes'
                            )
                        else:
                            formazott = torvenyi_szoveg_formazasa(
                                konyv_szoveg, paragrafus_szoveg, None,
                                torvenyi_szoveg, 'paragrafus'
                            )
                        
                        torvenyi_szovegek.append(formazott)
            
            # Törvényi szövegek hozzáadása a blokk végén
            if torvenyi_szovegek:
                feldolgozott_szoveg += ' ' + ' '.join(torvenyi_szovegek)
        
        kimenet.append(feldolgozott_szoveg)
    
    # Kimenet írása - SSML break tag a blokkok között
    kimeneti_szoveg = '\n\n<break time="5s"/>\n\n'.join(kimenet)
    
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

