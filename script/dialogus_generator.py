#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS-optimalizált dialógus generátor
Három fájlt hoz létre: teljes dialógus, csak kérdések, csak válaszok
"""

import re
import os

def szam_szavakkal(szam_str):
    """Számokat szavakkal írja ki"""
    szamok = {
        '0': 'nulla', '1': 'egy', '2': 'kettő', '3': 'három', '4': 'négy', '5': 'öt',
        '6': 'hat', '7': 'hét', '8': 'nyolc', '9': 'kilenc', '10': 'tíz',
        '11': 'tizenegy', '12': 'tizenkettő', '13': 'tizenhárom', '14': 'tizennégy', '15': 'tizenöt',
        '16': 'tizenhat', '17': 'tizenhét', '18': 'tizennyolc', '19': 'tizenkilenc', '20': 'húsz',
        '21': 'huszonegy', '22': 'huszonkettő', '23': 'huszonhárom', '24': 'huszonnégy', '25': 'huszonöt',
        '26': 'huszonhat', '27': 'huszonhét', '28': 'huszonnyolc', '29': 'huszonkilenc', '30': 'harminc',
        '50': 'ötven', '100': 'száz'
    }
    
    melleknevi = {
        '1': 'első', '2': 'második', '3': 'harmadik', '4': 'negyedik', '5': 'ötödik',
        '6': 'hatodik', '7': 'hetedik', '8': 'nyolcadik', '9': 'kilencedik', '10': 'tizedik',
        '11': 'tizenegyedik', '12': 'tizenkettedik', '13': 'tizenharmadik', '14': 'tizennegyedik', '15': 'tizenötödik',
        '16': 'tizenhatodik', '17': 'tizenhetedik', '18': 'tizennyolcadik', '19': 'tizenkilencedik', '20': 'huszadik',
        '21': 'huszonelső', '22': 'huszonmásodik', '23': 'huszonharmadik', '24': 'huszonnegyedik', '25': 'huszonötödik',
        '26': 'huszonhatodik', '27': 'huszonhetedik', '28': 'huszonnyolcadik', '29': 'huszonkilencedik', '30': 'harmincadik',
        '31': 'harmincelső', '32': 'harmincmásodik', '33': 'harmincharmadik', '34': 'harmincnegyedik', '35': 'harmincötödik',
        '36': 'harminchatodik', '37': 'harminchetedik', '38': 'harmincnyolcadik', '39': 'harminckilencedik', '40': 'negyvenedik',
        '41': 'negyvenelső', '42': 'negyvenmásodik', '43': 'negyvenharmadik', '44': 'negyvennegyedik', '45': 'negyvenötödik',
        '46': 'negyvenhatodik', '47': 'negyvenhetedik', '48': 'negyvennyolcadik', '49': 'negyvenkilencedik', '50': 'ötvenedik'
    }
    
    if szam_str in melleknevi:
        return melleknevi[szam_str]
    elif szam_str in szamok:
        return szamok[szam_str]
    return szam_str

def ptk_hivatkozas_atalakit(text):
    """Ptk. hivatkozásokat alakítja át"""
    # Ptk. 2:8. § (1) -> a Polgári Törvénykönyv második könyvének nyolcadik paragrafusának első bekezdése
    pattern = r'Ptk\.\s*(\d+):(\d+)\.\s*§\s*(?:\((\d+)\))?'
    
    def replace_func(match):
        konyv = szam_szavakkal(match.group(1))
        paragrafus = szam_szavakkal(match.group(2))
        bekezdes = match.group(3)
        
        if bekezdes:
            bekezdes_szam = szam_szavakkal(bekezdes)
            return f"a Polgári Törvénykönyv {konyv} könyvének {paragrafus} paragrafusának {bekezdes_szam} bekezdése"
        else:
            return f"a Polgári Törvénykönyv {konyv} könyvének {paragrafus} paragrafusa"
    
    return re.sub(pattern, replace_func, text)

def roviditesek_kibontasa(text):
    """Rövidítések kibontása"""
    roviditesek = {
        r'\bPtk\.': 'Polgári Törvénykönyv',
        r'\bpl\.': 'például',
        r'\bstb\.': 'és így tovább',
        r'\bvagy\.': 'vagyis',
        r'\bld\.': 'lásd',
        r'\bö\.': 'ön',
        r'\bdr\.': 'doktor',
        r'\bprof\.': 'professzor',
        r'\bstb': 'és így tovább',
    }
    
    for pattern, replacement in roviditesek.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def zarojel_eltavolitas(text):
    """Zárójelek eltávolítása, tartalom megtartása"""
    # (1) -> első, (2) -> második, stb.
    def replace_bekezdes(match):
        szam = match.group(1)
        return szam_szavakkal(szam)
    
    # Számozott zárójelek
    text = re.sub(r'\((\d+)\)', replace_bekezdes, text)
    
    # Egyéb zárójelek tartalmának megtartása
    text = re.sub(r'\(([^)]+)\)', r'\1', text)
    
    return text

def lista_folyo_szovegge(text):
    """Listákat folyó szöveggé alakítja"""
    # Számozott listák eltávolítása
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    
    # Betűvel számozott listák
    text = re.sub(r'^[a-z]\)\s*', '', text, flags=re.MULTILINE)
    
    # Listajeles pontok
    text = re.sub(r'^[-•*]\s*', '', text, flags=re.MULTILINE)
    
    return text

def markdown_eltavolitas(text):
    """Markdown formázás eltávolítása"""
    # Félkövér
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    # Dőlt
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Címsorok
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Kód blokkok
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    return text

def szamok_szavakkal(text):
    """Önálló számokat szavakkal írja ki"""
    def replace_szam(match):
        szam = match.group(0)
        if szam.isdigit():
            return szam_szavakkal(szam)
        return szam
    
    # Csak akkor cseréljük le, ha nem része egy hivatkozásnak vagy más speciális formátumnak
    text = re.sub(r'\b(\d+)\b', replace_szam, text)
    
    return text

def tts_optimalizalas(text):
    """TTS-optimalizálás teljes folyamata"""
    # 1. Markdown eltávolítása
    text = markdown_eltavolitas(text)
    
    # 2. Ptk. hivatkozások átalakítása (ez előbb kell, mert tartalmaz számokat)
    text = ptk_hivatkozas_atalakit(text)
    
    # 3. Rövidítések kibontása
    text = roviditesek_kibontasa(text)
    
    # 4. Zárójelek eltávolítása
    text = zarojel_eltavolitas(text)
    
    # 5. Listák folyó szöveggé alakítása
    text = lista_folyo_szovegge(text)
    
    # 6. Önálló számok szavakkal (de csak ha nem része már átalakított hivatkozásnak)
    # Ez utoljára, hogy ne rontsa el a már átalakított hivatkozásokat
    
    # Tisztítás: többszörös szóközök
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    return text.strip()

def fajl_beolvasas(fajlnev):
    """Fájl beolvasása"""
    with open(fajlnev, 'r', encoding='utf-8') as f:
        return f.read()

def fajl_mentes(tartalom, fajlnev):
    """Fájl mentése"""
    mappa = os.path.dirname(fajlnev)
    if mappa and not os.path.exists(mappa):
        os.makedirs(mappa, exist_ok=True)
    
    with open(fajlnev, 'w', encoding='utf-8') as f:
        f.write(tartalom)

def main():
    # Fájlok elérési útjai
    kerdesek_fajl = 'Tételek/A_cselekvokepesseg/kerdesek.txt'
    valaszok_fajl = 'Tételek/A_cselekvokepesseg/valaszok.txt'
    magyarazatok_fajl = 'Tételek/A_cselekvokepesseg/magyarazatok.txt'
    
    kimenet_mappa = 'Promtok/Tanulókártyák dialógus/Dialógus'
    
    # Fájlok beolvasása
    kerdesek = fajl_beolvasas(kerdesek_fajl)
    valaszok = fajl_beolvasas(valaszok_fajl)
    magyarazatok = fajl_beolvasas(magyarazatok_fajl)
    
    # Sorok feldolgozása
    kerdes_sorok = [s.strip() for s in kerdesek.split('\n') if s.strip() and not s.strip().isdigit()]
    valasz_sorok = [s.strip() for s in valaszok.split('\n') if s.strip() and not s.strip().isdigit()]
    magyarazat_sorok = [s.strip() for s in magyarazatok.split('\n') if s.strip() and not s.strip().isdigit()]
    
    # Dialógus építése
    teljes_dialogus = []
    csak_kerdesek = []
    csak_valaszok = []
    
    for i in range(min(len(kerdes_sorok), len(valasz_sorok), len(magyarazat_sorok))):
        kerdes = kerdes_sorok[i]
        valasz = valasz_sorok[i]
        magyarazat = magyarazat_sorok[i]
        
        # TTS-optimalizálás
        kerdes_opt = tts_optimalizalas(kerdes)
        valasz_opt = tts_optimalizalas(valasz)
        magyarazat_opt = tts_optimalizalas(magyarazat)
        
        # Válasz és magyarázat összefűzése természetes átkötéssel
        valasz_teljes = f"{valasz_opt} Ez azért van, mert {magyarazat_opt}"
        
        # Teljes dialógus
        teljes_dialogus.append(f"Kérdező: {kerdes_opt}")
        teljes_dialogus.append(f"Válaszoló: {valasz_teljes}")
        teljes_dialogus.append("")
        
        # Csak kérdések (címke nélkül)
        csak_kerdesek.append(kerdes_opt)
        csak_kerdesek.append("")
        
        # Csak válaszok (címke nélkül)
        csak_valaszok.append(valasz_teljes)
        csak_valaszok.append("")
    
    # Fájlok mentése
    fajl_mentes('\n'.join(teljes_dialogus), 
                f'{kimenet_mappa}/Tanulokartya-Dialogus_A_cselekvokepesseg.txt')
    fajl_mentes('\n'.join(csak_kerdesek), 
                f'{kimenet_mappa}/Tanulokartya-Kerdesek_A_cselekvokepesseg.txt')
    fajl_mentes('\n'.join(csak_valaszok), 
                f'{kimenet_mappa}/Tanulokartya-Valaszok_A_cselekvokepesseg.txt')
    
    print(f"Fájlok sikeresen létrehozva a '{kimenet_mappa}' mappában!")

if __name__ == '__main__':
    main()

