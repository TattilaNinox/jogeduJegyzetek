#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teljes tétel fájl feldolgozása felolvasóbarát (TTS) formába
Egyetlen .txt fájlt alakít át TTS-optimalizált formába az irányelvek szerint.
"""

import re
import os
import sys
from pathlib import Path

# ============================================================================
# KONFIGURÁCIÓ
# ============================================================================

# Rövidítések és kibontásaik
ROVIDITESEK = {
    'pl.': 'például',
    'Ptk.': 'Polgári Törvénykönyv',
    'stb.': 'és így tovább',
    'ld.': 'lásd',
    'vm.': 'valamely',
    'INY': 'ingatlan-nyilvántartás',
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
    'ipso iure': 'ipszo júre',
    'ex tunc': 'ex tunk',
    'conditio sine qua non': 'kondíció szine kva non',
    'restitutio in integrum': 'restitució in integrum',
}

# Számok fonetikus formája (1-100)
SZAMOK = {
    '1': 'egy', '2': 'kettő', '3': 'három', '4': 'négy', '5': 'öt',
    '6': 'hat', '7': 'hét', '8': 'nyolc', '9': 'kilenc', '10': 'tíz',
    '11': 'tizenegy', '12': 'tizenkettő', '13': 'tizenhárom', '14': 'tizennégy', '15': 'tizenöt',
    '16': 'tizenhat', '17': 'tizenhét', '18': 'tizennyolc', '19': 'tizenkilenc', '20': 'húsz',
    '21': 'huszonegy', '22': 'huszonkettő', '23': 'huszonhárom', '24': 'huszonnégy', '25': 'huszonöt',
    '26': 'huszonhat', '27': 'huszonhét', '28': 'huszonnyolc', '29': 'huszonkilenc', '30': 'harminc',
    '40': 'negyven', '50': 'ötven', '60': 'hatvan', '70': 'hetven', '80': 'nyolcvan', '90': 'kilencven', '100': 'száz'
}

# Melléknévi alakok betöltése a szamok_dict.txt fájlból
MELLEKNEMI_ALAKOK = {}
try:
    script_dir = Path(__file__).parent
    szamok_dict_path = script_dir / 'szamok_dict.txt'
    if szamok_dict_path.exists():
        with open(szamok_dict_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # A fájl Python dictionary formátumban van, exec-áljuk biztonságosan
            # Csak a szamok_melleknevi változót töltjük be
            local_vars = {}
            exec(content, {}, local_vars)
            if 'szamok_melleknevi' in local_vars:
                MELLEKNEMI_ALAKOK = local_vars['szamok_melleknevi']
    # Ha nem sikerült betölteni, használjuk az alapértelmezettet
    if not MELLEKNEMI_ALAKOK:
        MELLEKNEMI_ALAKOK = {
            '1': 'első', '2': 'második', '3': 'harmadik', '4': 'negyedik', '5': 'ötödik',
            '6': 'hatodik', '7': 'hetedik', '8': 'nyolcadik', '9': 'kilencedik', '10': 'tizedik',
            '11': 'tizenegyedik', '12': 'tizenkettedik', '13': 'tizenharmadik', '14': 'tizennegyedik', '15': 'tizenötödik',
            '16': 'tizenhatodik', '17': 'tizenhetedik', '18': 'tizennyolcadik', '19': 'tizenkilencedik', '20': 'huszadik',
            '21': 'huszonegyedik', '22': 'huszonkettedik', '23': 'huszonharmadik', '24': 'huszonnegyedik', '25': 'huszonötödik',
            '26': 'huszonhatodik', '27': 'huszonhetedik', '28': 'huszonnyolcadik', '29': 'huszonkilencedik', '30': 'harmincadik',
            '40': 'negyvenedik', '50': 'ötvenedik', '60': 'hatvanedik', '70': 'hetvenedik', '80': 'nyolcvanedik', '90': 'kilencvenedik', '100': 'századik'
        }
except Exception as e:
    # Ha hiba van, használjuk az alapértelmezettet
    MELLEKNEMI_ALAKOK = {
        '1': 'első', '2': 'második', '3': 'harmadik', '4': 'negyedik', '5': 'ötödik',
        '6': 'hatodik', '7': 'hetedik', '8': 'nyolcadik', '9': 'kilencedik', '10': 'tizedik',
        '11': 'tizenegyedik', '12': 'tizenkettedik', '13': 'tizenharmadik', '14': 'tizennegyedik', '15': 'tizenötödik',
        '16': 'tizenhatodik', '17': 'tizenhetedik', '18': 'tizennyolcadik', '19': 'tizenkilencedik', '20': 'huszadik',
        '21': 'huszonegyedik', '22': 'huszonkettedik', '23': 'huszonharmadik', '24': 'huszonnegyedik', '25': 'huszonötödik',
        '26': 'huszonhatodik', '27': 'huszonhetedik', '28': 'huszonnyolcadik', '29': 'huszonkilencedik', '30': 'harmincadik',
        '40': 'negyvenedik', '50': 'ötvenedik', '60': 'hatvanedik', '70': 'hetvenedik', '80': 'nyolcvanedik', '90': 'kilencvenedik', '100': 'századik'
    }

# Római számok átalakítása
ROMAN_TO_NUMBER = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15, 'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
}

def roman_to_words(roman_str):
    """Római számot szavakkal ír ki"""
    roman_clean = roman_str.upper().rstrip('.')
    if roman_clean in ROMAN_TO_NUMBER:
        num = ROMAN_TO_NUMBER[roman_clean]
        return number_to_ordinal(str(num))
    return roman_str

def year_to_words(year_str):
    """Évet szavakkal ír ki (pl. 2013 -> kettőezer tizenhárom)"""
    try:
        year = int(year_str)
        if year < 1000:
            return number_to_words(year_str)
        elif year < 2000:
            # 1000-1999: ezer + szám
            remainder = year % 1000
            if remainder == 0:
                return "ezer"
            else:
                return "ezer " + number_to_words(str(remainder))
        elif year < 10000:
            # 2000-9999: szám + ezer + szám
            thousands = year // 1000
            remainder = year % 1000
            thousands_word = number_to_words(str(thousands))
            if remainder == 0:
                return thousands_word + "ezer"
            else:
                return thousands_word + "ezer " + number_to_words(str(remainder))
        else:
            return year_str
    except:
        return year_str

# ============================================================================
# SEGÉDFÜGGVÉNYEK
# ============================================================================

def number_to_words(num_str):
    """Számot szavakkal ír ki"""
    try:
        num = int(num_str)
        if num == 0:
            return "nulla"
        elif num < 20:
            ones = ["", "egy", "kettő", "három", "négy", "öt", "hat", "hét", "nyolc", "kilenc", 
                   "tíz", "tizenegy", "tizenkettő", "tizenhárom", "tizennégy", "tizenöt", 
                   "tizenhat", "tizenhét", "tizennyolc", "tizenkilenc"]
            return ones[num]
        elif num < 100:
            tens = ["", "", "húsz", "harminc", "negyven", "ötven", "hatvan", "hetven", "nyolcvan", "kilencven"]
            ones = ["", "egy", "kettő", "három", "négy", "öt", "hat", "hét", "nyolc", "kilenc"]
            if num % 10 == 0:
                return tens[num // 10]
            elif num < 30:
                return tens[num // 10] + ones[num % 10]
            else:
                return tens[num // 10] + "en" + ones[num % 10]
        elif num < 1000:
            hundreds_map = {1: "száz", 2: "kétszáz", 3: "háromszáz", 4: "négyszáz", 5: "ötszáz",
                           6: "hatszáz", 7: "hétszáz", 8: "nyolcszáz", 9: "kilencszáz"}
            hundred = num // 100
            remainder = num % 100
            if remainder == 0:
                return hundreds_map.get(hundred, "")
            else:
                return hundreds_map.get(hundred, "") + number_to_words(str(remainder))
        else:
            return num_str
    except:
        return num_str

def number_to_ordinal(num_str):
    """Számot melléknévi alakban ad vissza"""
    if num_str in MELLEKNEMI_ALAKOK:
        return MELLEKNEMI_ALAKOK[num_str]
    try:
        num = int(num_str)
        if num < 1:
            return num_str
        if num < 20:
            ones_ord = ["", "első", "második", "harmadik", "negyedik", "ötödik", "hatodik", "hetedik", "nyolcadik", "kilencedik",
                       "tizedik", "tizenegyedik", "tizenkettedik", "tizenharmadik", "tizennegyedik", "tizenötödik",
                       "tizenhatodik", "tizenhetedik", "tizennyolcadik", "tizenkilencedik"]
            return ones_ord[num]
        elif num < 100:
            tens_ord = ["", "", "huszadik", "harmincadik", "negyvenedik", "ötvenedik", "hatvanedik", "hetvenedik", "nyolcvanedik", "kilencvenedik"]
            ones_ord = ["", "egyedik", "kettedik", "harmadik", "negyedik", "ötödik", "hatodik", "hetedik", "nyolcadik", "kilencedik"]
            t = num // 10
            o = num % 10
            if o == 0:
                return tens_ord[t]
            else:
                if t == 2:
                    return "huszon" + ones_ord[o]
                elif t == 3:
                    return "harminc" + ones_ord[o]
                elif t == 4:
                    return "negyven" + ones_ord[o]
                elif t == 5:
                    return "ötven" + ones_ord[o]
                elif t == 6:
                    return "hatvan" + ones_ord[o]
                elif t == 7:
                    return "hetven" + ones_ord[o]
                elif t == 8:
                    return "nyolcvan" + ones_ord[o]
                elif t == 9:
                    return "kilencven" + ones_ord[o]
        else:
            return num_str
    except:
        return num_str

def convert_ptk_reference(text):
    """Ptk. hivatkozásokat alakítja át szöveges formába"""
    # Először kezeljük azokat az eseteket, amikor már van "2013. évi V. törvény a Polgári Törvénykönyvről" előtte
    # "2013. évi V. törvény a Polgári Törvénykönyvről 5:14. §" -> "kettőezer tizenhárom évi ötödik törvény, a Polgári Törvénykönyv ötödik könyvének tizennegyedik paragrafusa"
    pattern1a = r'(\d{4})\.\s*évi\s+([IVX]+)\.\s*törvény\s*a\s*Polgári\s*Törvénykönyvről\s*(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?([-a-záéíóöőúüű]*)?'
    
    def replace_with_torveny_rol(match):
        year = match.group(1)
        torveny_num = match.group(2)
        book = match.group(3)
        para = match.group(4)
        subpara = match.group(5)
        rag = match.group(6) if match.group(6) else ""
        
        # Év fonetikusan
        year_word = year_to_words(year)
        
        # Törvény szám melléknévi alakban
        torveny_ordinal = roman_to_words(torveny_num)
        
        # Könyv szám melléknévi alakban
        book_ordinal = number_to_ordinal(book)
        
        # Paragrafus szám melléknévi alakban
        para_ordinal = number_to_ordinal(para)
        
        result = f"{year_word} évi {torveny_ordinal} törvény, a Polgári Törvénykönyv {book_ordinal} könyvének {para_ordinal} paragrafusa"
        
        if subpara:
            subpara_ordinal = number_to_ordinal(subpara)
            result += f" {subpara_ordinal} bekezdése"
        
        return result
    
    text = re.sub(pattern1a, replace_with_torveny_rol, text, flags=re.IGNORECASE)
    
    # Aztán kezeljük azokat az eseteket, amikor már van "2013. évi V. törvény (Ptk.)" előtte
    # "2013. évi V. törvény (Ptk.) 2:8. §-a" -> "kettőezer tizenhárom évi ötödik törvény, a Polgári Törvénykönyv második könyvének nyolcadik paragrafusa"
    pattern1b = r'(\d{4})\.\s*évi\s+([IVX]+)\.\s*törvény\s*\(Ptk\.\)\s*(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?([-a-záéíóöőúüű]*)?'
    
    def replace_with_torveny(match):
        year = match.group(1)
        torveny_num = match.group(2)
        book = match.group(3)
        para = match.group(4)
        subpara = match.group(5)
        rag = match.group(6) if match.group(6) else ""
        
        # Év fonetikusan
        year_word = year_to_words(year)
        
        # Törvény szám melléknévi alakban
        torveny_ordinal = roman_to_words(torveny_num)
        
        # Könyv szám melléknévi alakban
        book_ordinal = number_to_ordinal(book)
        
        # Paragrafus szám melléknévi alakban
        para_ordinal = number_to_ordinal(para)
        
        result = f"{year_word} évi {torveny_ordinal} törvény, a Polgári Törvénykönyv {book_ordinal} könyvének {para_ordinal} paragrafusa"
        
        if subpara:
            subpara_ordinal = number_to_ordinal(subpara)
            result += f" {subpara_ordinal} bekezdése"
        
        return result
    
    # Először az összetett hivatkozásokat alakítjuk át
    text = re.sub(pattern1b, replace_with_torveny, text, flags=re.IGNORECASE)
    
    # Kezeljük azokat az eseteket, amikor "2013. évi V. törvény Polgári Törvénykönyv" (nincs "a" és nincs "ről")
    pattern1c = r'(\d{4})\.\s*évi\s+([IVX]+)\.\s*törvény\s+Polgári\s*Törvénykönyv\s+(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?([-a-záéíóöőúüű]*)?'
    
    def replace_with_torveny_no_a(match):
        year = match.group(1)
        torveny_num = match.group(2)
        book = match.group(3)
        para = match.group(4)
        subpara = match.group(5)
        rag = match.group(6) if match.group(6) else ""
        
        # Év fonetikusan
        year_word = year_to_words(year)
        
        # Törvény szám melléknévi alakban
        torveny_ordinal = roman_to_words(torveny_num)
        
        # Könyv szám melléknévi alakban
        book_ordinal = number_to_ordinal(book)
        
        # Paragrafus szám melléknévi alakban
        para_ordinal = number_to_ordinal(para)
        
        result = f"{year_word} évi {torveny_ordinal} törvény, a Polgári Törvénykönyv {book_ordinal} könyvének {para_ordinal} paragrafusa"
        
        if subpara:
            subpara_ordinal = number_to_ordinal(subpara)
            result += f" {subpara_ordinal} bekezdése"
        
        return result
    
    text = re.sub(pattern1c, replace_with_torveny_no_a, text, flags=re.IGNORECASE)
    
    # Kezeljük a "Ptk. szám: szám" formátumot (pl. "Ptk. hat: kétszázhetvenenkettő")
    # Ez egy speciális formátum, ahol a számok már átalakítva vannak
    pattern_ptk_words = r'\bPtk\.\s*([a-záéíóöőúüű]+):\s*([a-záéíóöőúüű\s]+)\.\s*§'
    
    def replace_ptk_words(match):
        book_word = match.group(1)
        para_text = match.group(2).strip()
        # A számokat már átalakítottuk, csak a "Ptk."-t kell átalakítani
        return f"A Polgári Törvénykönyv {book_word}: {para_text}. paragrafusa"
    
    text = re.sub(pattern_ptk_words, replace_ptk_words, text, flags=re.IGNORECASE)
    
    # Aztán az egyszerű "Ptk. 2:8. §" hivatkozásokat (amikor már nincs "2013. évi V. törvény" előtte)
    # De vigyázzunk: "Ptk. hat: hat" formátumot ne alakítsuk át rosszul
    pattern2 = r'\bPtk\.\s*(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?([-a-záéíóöőúüű]*)?'
    
    def replace_simple_ptk(match):
        book = match.group(1)
        para = match.group(2)
        subpara = match.group(3)
        rag = match.group(4) if match.group(4) else ""
        
        # Könyv szám melléknévi alakban
        book_ordinal = number_to_ordinal(book)
        
        # Paragrafus szám melléknévi alakban
        para_ordinal = number_to_ordinal(para)
        
        result = f"A Polgári Törvénykönyv {book_ordinal} könyvének {para_ordinal} paragrafusa"
        
        if subpara:
            subpara_ordinal = number_to_ordinal(subpara)
            result += f" {subpara_ordinal} bekezdése"
        
        return result
    
    # Csak azokat a "Ptk." hivatkozásokat alakítjuk át, amelyeket még nem alakítottunk át
    text = re.sub(pattern2, replace_simple_ptk, text, flags=re.IGNORECASE)
    
    # Kezeljük azokat az eseteket, amikor csak "5:73. §" van (nincs előtte "Ptk." vagy "2013. évi V. törvény")
    # De csak akkor, ha még nem alakítottuk át
    pattern3 = r'\b(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?([-a-záéíóöőúüű]*)?'
    
    def replace_standalone_ptk(match):
        book = match.group(1)
        para = match.group(2)
        subpara = match.group(3)
        rag = match.group(4) if match.group(4) else ""
        
        # Ellenőrizzük, hogy már átalakítva van-e
        context_before = text[max(0, match.start()-50):match.start()]
        context_after = text[match.end():match.end()+50]
        
        # Ha már van "könyv" vagy "paragrafus" a környezetben, ne alakítsuk át
        if 'könyv' in context_before[-30:] or 'paragrafus' in context_before[-30:]:
            return match.group(0)
        
        # Könyv szám melléknévi alakban
        book_ordinal = number_to_ordinal(book)
        
        # Paragrafus szám melléknévi alakban
        para_ordinal = number_to_ordinal(para)
        
        result = f"A Polgári Törvénykönyv {book_ordinal} könyvének {para_ordinal} paragrafusa"
        
        if subpara:
            subpara_ordinal = number_to_ordinal(subpara)
            result += f" {subpara_ordinal} bekezdése"
        
        return result
    
    text = re.sub(pattern3, replace_standalone_ptk, text, flags=re.IGNORECASE)
    
    # Kezeljük azokat az eseteket, amikor csak "V. törvény" van (nincs utána paragrafus hivatkozás)
    pattern4 = r'(\d{4})\.\s*évi\s+([IVX]+)\.\s*törvény\s+(?:Polgári\s*Törvénykönyv|Ptk\.)?(?!\s*\d+:\d+\.\s*§)'
    
    def replace_torveny_only(match):
        year = match.group(1)
        torveny_num = match.group(2)
        
        # Év fonetikusan
        year_word = year_to_words(year)
        
        # Törvény szám melléknévi alakban
        torveny_ordinal = roman_to_words(torveny_num)
        
        return f"{year_word} évi {torveny_ordinal} törvény, a Polgári Törvénykönyv"
    
    text = re.sub(pattern4, replace_torveny_only, text, flags=re.IGNORECASE)
    
    return text

def expand_abbreviations(text):
    """Rövidítések kibontása"""
    # Először alakítsuk át az összes maradék "Ptk."-t, amelyet még nem alakítottunk át
    # (pl. "Ptk. Negyedik Könyv" vagy "Ptk. Harmadik Könyve")
    pattern_ptk_remaining = r'\bPtk\.\s+([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű\s]+)'
    
    def replace_ptk_remaining(match):
        rest = match.group(1)
        return f"Polgári Törvénykönyv {rest}"
    
    text = re.sub(pattern_ptk_remaining, replace_ptk_remaining, text, flags=re.IGNORECASE)
    
    # Aztán a többi rövidítést bontjuk ki
    for rovidites, kibontott in ROVIDITESEK.items():
        if rovidites == 'Ptk.':  # Ezt már kezeltük
            continue
        # Speciális kezelés ponttal végződő rövidítéseknél
        if rovidites.endswith('.'):
            # Ponttal végződő rövidítéseknél a pontot is escape-eljük
            pattern = r'\b' + re.escape(rovidites) + r'(?=\s|$|[^\w])'
        else:
            pattern = r'\b' + re.escape(rovidites) + r'\b'
        text = re.sub(pattern, kibontott, text, flags=re.IGNORECASE)
    
    return text

def convert_latin(text):
    """Latin kifejezések fonetizálása"""
    for latin, fonetikus in LATIN_KIFEJEZESEK.items():
        pattern = r'\b' + re.escape(latin) + r'\b'
        text = re.sub(pattern, fonetikus, text, flags=re.IGNORECASE)
    
    return text

def remove_special_chars(text):
    """Speciális karakterek eltávolítása"""
    # Táblázatokban lévő "|" karakterek eltávolítása
    text = re.sub(r'\s*\|\s*', ' ', text)
    
    # Többszörös kötőjelek eltávolítása (táblázatok szegélyei)
    text = re.sub(r'-{3,}', '', text)
    
    # Zárójelek eltávolítása, tartalom megtartása
    # De vigyázzunk: (1) bekezdés esetén át kell alakítani
    text = re.sub(r'\(([^)]+)\)', r'\1', text)
    
    # Nyilak szöveggé alakítása
    text = text.replace('->', 'akkor következik')
    text = text.replace('→', 'akkor következik')
    
    return text

def remove_formatting(text):
    """Markdown és formázás eltávolítása"""
    # Címsorok eltávolítása (#, ##, ###)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # Félkövér formázás (**text** vagy __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # Dőlt formázás (*text* vagy _text_)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Code formázás (`text`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    return text

def convert_lists_to_text(text):
    """Felsorolások és listák folyó szöveggé alakítása"""
    # Listajeles pontok eltávolítása és folyó szöveggé alakítás
    text = re.sub(r'^\s*[-•*]\s+', '', text, flags=re.MULTILINE)
    
    # Számozott listák (1., 2., stb.)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Betűvel számozott listák (a), b), c)) -> "a pont, b pont, c pont"
    # De csak akkor, ha még nincs "pont" utána
    def replace_letter_list(match):
        letter = match.group(1)
        # Ellenőrizzük, hogy már nincs-e "pont" utána
        after_match = text[match.end():match.end()+10]
        if 'pont' in after_match.lower():
            return match.group(0)  # Ne alakítsuk át
        return f' {letter} pont, '
    
    text = re.sub(r'\s*([a-z])\)\s+', replace_letter_list, text, flags=re.IGNORECASE)
    
    # Kötőjeles számok (pl. "14-18" -> "tizennégy és tizennyolc közötti")
    # De ne alakítsuk át, ha már egy hivatkozás része
    pattern_range = r'\b(\d{1,3})\s*-\s*(\d{1,3})\b'
    
    def replace_range(match):
        num1 = match.group(1)
        num2 = match.group(2)
        # Ne alakítsuk át, ha már egy hivatkozás része
        context = text[max(0, match.start()-50):match.end()+50]
        if ('könyv' in context or 'paragrafus' in context or 'bekezdés' in context or 
            'Polgári Törvénykönyv' in context or 'Ptk.' in context):
            return match.group(0)
        word1 = number_to_words(num1)
        word2 = number_to_words(num2)
        return f"{word1} és {word2} közötti"
    
    text = re.sub(pattern_range, replace_range, text)
    
    # "közötti közötti" duplikációk eltávolítása
    text = re.sub(r'\b(közötti)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # "pont, pont" duplikációk eltávolítása
    text = re.sub(r'\b(pont),\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # Ne kössük össze a sorokat automatikusan - tartsuk meg a bekezdéseket
    # Csak akkor kössük össze, ha egyértelműen felsorolás része
    # (pl. ha egy sor végén nincs írásjel és a következő sor "-" vagy számozott lista elemmel kezdődik)
    
    return text

def remove_roman_from_headers(text):
    """Római számok eltávolítása a címekből"""
    # Címekben lévő római számokat töröljük (pl. "III. A Kiskorúak" -> "A Kiskorúak")
    # Ha egy sor elején van római szám ponttal, majd nagybetűvel kezdődő szöveg, akkor cím
    pattern = r'^([IVX]+)\.\s+([A-ZÁÉÍÓÖŐÚÜŰ])'
    
    def remove_roman(match):
        # Csak a római számot és pontot töröljük, a szöveget megtartjuk
        return match.group(2)
    
    text = re.sub(pattern, remove_roman, text, flags=re.MULTILINE)
    
    return text

def convert_roman_numbers(text):
    """Római számok átalakítása fonetikusan"""
    # Római számok ponttal (I., II., III., IV., V., stb.)
    # NE alakítsuk át a címekben lévő római számokat (pl. "III. A Kiskorúak")
    pattern = r'\b([IVX]+)\.\b'
    
    def replace_roman(match):
        roman = match.group(1)
        # Ne alakítsuk át, ha már egy átalakított hivatkozás része
        context_before = text[max(0, match.start()-100):match.start()]
        context_after = text[match.end():match.end()+100]
        
        # Ne alakítsuk át, ha címben van (pl. "III. A Kiskorúak")
        # Ha a római szám után nagybetűvel kezdődő szöveg van, akkor cím
        if re.match(r'^\s+[A-ZÁÉÍÓÖŐÚÜŰ]', context_after):
            return match.group(0)
        
        # Ne alakítsuk át, ha már része egy átalakított hivatkozásnak
        # (pl. "ötödik törvény" vagy "második könyv" után)
        if ('könyv' in context_before[-30:] or 'paragrafus' in context_before[-30:] or 
            'bekezdés' in context_before[-30:] or 'törvény' in context_before[-30:].lower()):
            return match.group(0)
        
        # Alakítsuk át minden más esetben
        return roman_to_words(roman) + "."
    
    text = re.sub(pattern, replace_roman, text, flags=re.IGNORECASE)
    
    return text

def convert_years(text):
    """Évek átalakítása fonetikusan"""
    # Először az "évi" szóval együtt lévő éveket (pl. "2013. évi")
    pattern1 = r'\b(\d{4})\.\s*évi\b'
    
    def replace_year_with_evi(match):
        year = match.group(1)
        return year_to_words(year) + ". évi"
    
    text = re.sub(pattern1, replace_year_with_evi, text)
    
    # Aztán az általános éveket (pl. "2013." vagy "2013-ben")
    # De csak akkor, ha még nem alakítottuk át (nem része egy már átalakított hivatkozásnak)
    pattern2 = r'\b(\d{4})(\.|ben|ban|ból|ből|ra|re|ig|től|től)\b'
    
    def replace_year_general(match):
        year = match.group(1)
        suffix = match.group(2)
        # Ne alakítsuk át, ha már egy hivatkozás része
        context = text[max(0, match.start()-30):match.end()+30]
        if 'könyv' in context or 'paragrafus' in context or 'bekezdés' in context:
            return match.group(0)
        return year_to_words(year) + suffix
    
    text = re.sub(pattern2, replace_year_general, text)
    
    return text

def convert_numbers_in_text(text):
    """Számok átalakítása szöveges formába"""
    # Először a zárójelben lévő számokat (bekezdések számait)
    # De csak akkor, ha nem része egy már átalakított hivatkozásnak
    pattern_bekezdes = r'\((\d+)\)(?:\s*bekezdés[eé]?)?'
    
    def replace_bekezdes(match):
        num = match.group(1)
        # Ne alakítsuk át, ha már egy hivatkozás része
        context = text[max(0, match.start()-50):match.end()+50]
        if 'könyv' in context or 'paragrafus' in context:
            return match.group(0)
        return "(" + number_to_ordinal(num) + " bekezdés)"
    
    text = re.sub(pattern_bekezdes, replace_bekezdes, text, flags=re.IGNORECASE)
    
    # NE alakítsuk át az idézetekben lévő számokat (pl. "1 Cselekvőképtelen" maradjon "1 Cselekvőképtelen")
    # Az idézetekben lévő számokat megtartjuk eredeti formájukban
    
    # Számok szavakkal az idézetekben (pl. "kettő Aki" -> "második Aki")
    # Csak akkor, ha egy idézetben van és szóval kezdődik
    pattern_quote_number = r'["""](kettő|három|négy|öt|hat|hét|nyolc|kilenc|tíz|tizenegy|tizenkettő|tizenhárom|tizennégy|tizenöt|tizenhat|tizenhét|tizennyolc|tizenkilenc|húsz|huszonegy|huszonkettő|huszonhárom|huszonnégy|huszonöt|huszonhat|huszonhét|huszonnyolc|huszonkilenc|harminc|negyven|ötven|hatvan|hetven|nyolcvan|kilencven|száz)\s+([A-ZÁÉÍÓÖŐÚÜŰ])'
    
    def replace_quote_number_word(match):
        num_word = match.group(1)
        next_char = match.group(2)
        # Szám szóról számra, majd melléknévi alakba
        num_dict = {
            'kettő': '2', 'három': '3', 'négy': '4', 'öt': '5', 'hat': '6',
            'hét': '7', 'nyolc': '8', 'kilenc': '9', 'tíz': '10',
            'tizenegy': '11', 'tizenkettő': '12', 'tizenhárom': '13',
            'tizennégy': '14', 'tizenöt': '15', 'tizenhat': '16',
            'tizenhét': '17', 'tizennyolc': '18', 'tizenkilenc': '19',
            'húsz': '20', 'huszonegy': '21', 'huszonkettő': '22',
            'huszonhárom': '23', 'huszonnégy': '24', 'huszonöt': '25',
            'huszonhat': '26', 'huszonhét': '27', 'huszonnyolc': '28',
            'huszonkilenc': '29', 'harminc': '30', 'negyven': '40',
            'ötven': '50', 'hatvan': '60', 'hetven': '70',
            'nyolcvan': '80', 'kilencven': '90', 'száz': '100'
        }
        if num_word in num_dict:
            ordinal = number_to_ordinal(num_dict[num_word])
            return '"' + ordinal + " " + next_char
        return match.group(0)
    
    text = re.sub(pattern_quote_number, replace_quote_number_word, text)
    
    # "A 3 bekezdés" vagy "1 bekezdése" -> "(harmadik bekezdés)" vagy "(első bekezdés)"
    pattern_bekezdes_ref = r'\bA\s+(\d+)\s+bekezdés'
    
    def replace_bekezdes_ref(match):
        num = match.group(1)
        return "A (" + number_to_ordinal(num) + " bekezdés)"
    
    text = re.sub(pattern_bekezdes_ref, replace_bekezdes_ref, text, flags=re.IGNORECASE)
    
    # "5:73. § 1 bekezdése" vagy "A Polgári Törvénykönyv negyedik könyvének ötödik paragrafusa első bekezdése" formátumok
    # De csak akkor, ha még nem alakítottuk át
    pattern_ptk_with_bekezdes = r'(\d+):(\d+)\.\s*§\s*(\d+)\s+bekezdés[eé]?'
    
    def replace_ptk_with_bekezdes(match):
        book = match.group(1)
        para = match.group(2)
        bekezdes = match.group(3)
        # Ellenőrizzük, hogy már átalakítva van-e
        context = text[max(0, match.start()-50):match.end()+50]
        if 'könyv' in context or 'paragrafus' in context:
            return match.group(0)
        book_ordinal = number_to_ordinal(book)
        para_ordinal = number_to_ordinal(para)
        bekezdes_ordinal = number_to_ordinal(bekezdes)
        return f"{book_ordinal} könyvének {para_ordinal} paragrafusa ({bekezdes_ordinal} bekezdés)"
    
    text = re.sub(pattern_ptk_with_bekezdes, replace_ptk_with_bekezdes, text, flags=re.IGNORECASE)
    
    # "A Polgári Törvénykönyv negyedik könyvének ötödik paragrafusa első bekezdése" -> "A Polgári Törvénykönyv negyedik könyvének ötödik paragrafusa (első bekezdés)"
    pattern_bekezdes_after_paragrafus = r'(A Polgári Törvénykönyv [a-záéíóöőúüű\s]+ paragrafusa)\s+([a-záéíóöőúüű]+)\s+bekezdés[eé]?'
    
    def replace_bekezdes_after_paragrafus(match):
        paragrafus_text = match.group(1)
        bekezdes_word = match.group(2)
        # Szám szóról számra, majd melléknévi alakba
        num_dict = {
            'első': '1', 'második': '2', 'harmadik': '3', 'negyedik': '4', 'ötödik': '5',
            'hatodik': '6', 'hetedik': '7', 'nyolcadik': '8', 'kilencedik': '9', 'tizedik': '10'
        }
        if bekezdes_word in num_dict:
            bekezdes_ordinal = number_to_ordinal(num_dict[bekezdes_word])
            return f"{paragrafus_text} ({bekezdes_ordinal} bekezdés)"
        return match.group(0)
    
    text = re.sub(pattern_bekezdes_after_paragrafus, replace_bekezdes_after_paragrafus, text, flags=re.IGNORECASE)
    
    # "1 bekezdése" -> "(első bekezdés)" (ha még nem alakítottuk át)
    pattern_bekezdes_standalone = r'\b(\d+)\s+bekezdés[eé]?'
    
    def replace_bekezdes_standalone(match):
        num = match.group(1)
        # Ellenőrizzük, hogy már átalakítva van-e
        context_before = text[max(0, match.start()-30):match.start()]
        context_after = text[match.end():match.end()+30]
        context = context_before + context_after
        if 'könyv' in context or 'paragrafus' in context or '(' in context_before[-10:]:
            return match.group(0)
        return f"({number_to_ordinal(num)} bekezdés)"
    
    text = re.sub(pattern_bekezdes_standalone, replace_bekezdes_standalone, text, flags=re.IGNORECASE)
    
    # Aztán az általános számokat
    def replace_number(match):
        num_str = match.group(0)
        # Ne alakítsuk át, ha már egy hivatkozás része
        context = text[max(0, match.start()-50):match.end()+50]
        if ('könyv' in context or 'paragrafus' in context or 'bekezdés' in context or 
            'évi' in context or 'Polgári Törvénykönyv' in context or 'Ptk.' in context):
            return num_str
        
        # Ne alakítsuk át, ha idézetben van (pl. "1 Cselekvőképtelen")
        # Ha a szám előtt vagy után idézőjel van
        if '"' in context or '"' in context or '"' in context:
            return num_str
        
        # Ne alakítsuk át, ha tartományban van (pl. "0-14 év")
        # Ha a szám előtt vagy után kötőjel van
        if re.search(r'\d+\s*-\s*\d+', context) or re.search(r'\d+\s*–\s*\d+', context):
            return num_str
        
        return number_to_words(num_str)
    
    # Csak azok a számok, amelyek nem részei már átalakított hivatkozásoknak vagy éveknek
    text = re.sub(r'\b(\d{1,3})\b', replace_number, text)
    
    # Javítás: "hat: hat" vagy "egy: egy" formátumok javítása hivatkozásokban
    # "Polgári Törvénykönyv hat: hat" -> "Polgári Törvénykönyv hatodik könyvének hatodik paragrafusa"
    pattern_fix_ptk_words = r'(Polgári Törvénykönyv|Ptk\.)\s+([a-záéíóöőúüű]+):\s*([a-záéíóöőúüű]+)\s+és\s+\3\s+közötti'
    
    def fix_ptk_words_range(match):
        ptk = match.group(1)
        book_word = match.group(2)
        para_word = match.group(3)
        # Szám szóról számra, majd melléknévi alakba
        num_dict = {
            'egy': '1', 'kettő': '2', 'három': '3', 'négy': '4', 'öt': '5', 'hat': '6',
            'hét': '7', 'nyolc': '8', 'kilenc': '9', 'tíz': '10'
        }
        if book_word in num_dict and para_word in num_dict:
            book_ordinal = number_to_ordinal(num_dict[book_word])
            para_ordinal = number_to_ordinal(num_dict[para_word])
            return f"A Polgári Törvénykönyv {book_ordinal} könyvének {para_ordinal} paragrafusa"
        return match.group(0)
    
    text = re.sub(pattern_fix_ptk_words, fix_ptk_words_range, text, flags=re.IGNORECASE)
    
    return text

def ensure_colon_after_headers(text):
    """Biztosítja, hogy a bekezdés címek után kettőspont legyen"""
    # Címek után kettőspont (pl. "I. Bevezetés:" vagy "1. Fogalom:")
    text = re.sub(r'^([IVX]+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ][^:]+?)(\s|$)', r'\1:\2', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ][^:]+?)(\s|$)', r'\1:\2', text, flags=re.MULTILINE)
    
    return text

def clean_whitespace(text):
    """Szóközök és sortörések tisztítása, bekezdések megőrzése"""
    # Speciális duplikációk eltávolítása először
    # "pont, pont" -> "pont"
    text = re.sub(r'\b(pont),\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # "közötti közötti" -> "közötti"
    text = re.sub(r'\b(közötti)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # "bekezdés bekezdés" vagy "bekezdése bekezdése" -> "bekezdés" vagy "bekezdése"
    text = re.sub(r'\b(bekezdés[eé]?)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # "bekezdésében bekezdésében" -> "bekezdésében"
    text = re.sub(r'\b(bekezdésében)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # Duplikációk eltávolítása (pl. "bekezdése bekezdése" -> "bekezdése")
    # Többször is futtatjuk, hogy az összes duplikációt eltávolítsuk
    for _ in range(5):  # Maximum 5 iteráció, hogy ne legyen végtelen ciklus
        new_text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        if new_text == text:
            break
        text = new_text
    
    # Többszavas duplikációk (pl. "első bekezdése első bekezdése" -> "első bekezdése")
    for _ in range(3):
        new_text = re.sub(r'\b(\w+\s+\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        if new_text == text:
            break
        text = new_text
    
    # Dupla "A A" -> "A"
    text = re.sub(r'\bA\s+A\s+', 'A ', text)
    
    # Többszörös szóközök egyetlen szóközre (de ne érintsük a sortöréseket)
    # Csak a sorokon belüli szóközöket cseréljük le
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Csak a soron belüli szóközöket cseréljük le
        cleaned_line = re.sub(r'[ \t]+', ' ', line)
        cleaned_lines.append(cleaned_line)
    text = '\n'.join(cleaned_lines)
    
    # Szóközök írásjelek előtt eltávolítása
    text = re.sub(r'[ \t]+([,\.;:!?])', r'\1', text)
    
    # Szóköz írásjel után (ha nincs)
    text = re.sub(r'([,\.;:!?])([A-ZÁÉÍÓÖŐÚÜŰa-záéíóöőúüű])', r'\1 \2', text)
    
    # Biztosítjuk, hogy a címek után legyen sortörés
    text = re.sub(r'([IVX]+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ][^:\n]+:)\s*', r'\1\n\n', text)
    text = re.sub(r'(\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ][^:\n]+:)\s*', r'\1\n\n', text)
    
    # Mondatok után bekezdés (ha egy mondat ponttal vagy kérdőjellel végződik és nagybetűvel kezdődik a következő)
    text = re.sub(r'([\.!?])\s+([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű])', r'\1\n\n\2', text)
    
    # Többszörös sortörések (max 2 üres sor)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Üres sorok eltávolítása a szöveg elejéről és végéről
    text = text.strip()
    
    return text

# ============================================================================
# FŐ FELDOLGOZÁSI FÜGGVÉNY
# ============================================================================

def feldolgoz_teljes_tetel(szoveg):
    """Teljes tétel feldolgozása felolvasóbarát formába"""
    # 1. Markdown formázás eltávolítása (először, hogy ne zavarja a hivatkozások felismerését)
    szoveg = remove_formatting(szoveg)
    
    # 1.5. Római számok eltávolítása a címekből (pl. "III. A Kiskorúak" -> "A Kiskorúak")
    szoveg = remove_roman_from_headers(szoveg)
    
    # 2. Ptk. hivatkozások átalakítása (a markdown eltávolítása után)
    szoveg = convert_ptk_reference(szoveg)
    
    # 3. Évek átalakítása fonetikusan (pl. "2013. évi" -> "kettőezer tizenhárom évi")
    szoveg = convert_years(szoveg)
    
    # 4. Római számok NEM alakítjuk át - megtartjuk eredeti formájukban
    # (A hivatkozásokban lévő római számokat a convert_ptk_reference már kezeli)
    # szoveg = convert_roman_numbers(szoveg)  # KIKAPCSOLVA - egyáltalán nem alakítjuk át
    
    # 5. Rövidítések kibontása (a "(Ptk.)" már átalakítva, csak a többi rövidítést kezeli)
    szoveg = expand_abbreviations(szoveg)
    
    # 6. Latin kifejezések fonetizálása
    szoveg = convert_latin(szoveg)
    
    # 7. Speciális karakterek eltávolítása
    szoveg = remove_special_chars(szoveg)
    
    # 8. Felsorolások folyó szöveggé alakítása
    szoveg = convert_lists_to_text(szoveg)
    
    # 9. Számok átalakítása (UTOLSÓ, hogy ne alakítsa át a hivatkozásokban lévő számokat)
    # A hivatkozásokban lévő számok már átalakítva vannak a convert_ptk_reference-ben
    szoveg = convert_numbers_in_text(szoveg)
    
    # 10. Bekezdés címek után kettőspont biztosítása
    szoveg = ensure_colon_after_headers(szoveg)
    
    # 11. Szóközök és sortörések tisztítása
    szoveg = clean_whitespace(szoveg)
    
    return szoveg

# ============================================================================
# FÁJLKEZELÉS
# ============================================================================

def feldolgoz_fajl(bemenet_utvonal, kimenet_utvonal=None):
    """Egyetlen fájl feldolgozása"""
    try:
        with open(bemenet_utvonal, 'r', encoding='utf-8') as f:
            szoveg = f.read()
    except FileNotFoundError:
        print(f"✗ Hiba: A fájl nem található: {bemenet_utvonal}")
        return False
    except Exception as e:
        print(f"✗ Hiba a fájl olvasása során: {e}")
        return False
    
    # Feldolgozás
    feldolgozott_szoveg = feldolgoz_teljes_tetel(szoveg)
    
    # Kimenet meghatározása
    if kimenet_utvonal is None:
        bemenet_path = Path(bemenet_utvonal)
        # Kimenet mappa: ugyanabban a mappában, feldolgozott_tetelek almappába
        kimenet_mappa = bemenet_path.parent / "feldolgozott_tetelek"
        kimenet_mappa.mkdir(parents=True, exist_ok=True)
        kimenet_utvonal = kimenet_mappa / f"{bemenet_path.stem}_feldolgozott{bemenet_path.suffix}"
    
    # Kimenet írása
    try:
        kimenet_path = Path(kimenet_utvonal)
        kimenet_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(kimenet_utvonal, 'w', encoding='utf-8') as f:
            f.write(feldolgozott_szoveg)
        
        print(f"✓ Feldolgozva: {bemenet_utvonal} -> {kimenet_utvonal}")
        return True
    except Exception as e:
        print(f"✗ Hiba a fájl írása során: {e}")
        return False

def feldolgoz_mappa(mappa_utvonal):
    """Egy mappa közvetlenül lévő .txt fájljainak feldolgozása (nem az almappákban)"""
    mappa_path = Path(mappa_utvonal)
    
    if not mappa_path.is_dir():
        print(f"✗ Hiba: A mappa nem létezik: {mappa_utvonal}")
        return
    
    # Csak a mappában közvetlenül lévő .txt fájlokat keressük (nem az almappákban)
    # Kizárjuk a feldolgozott fájlokat is
    txt_fajlok = [f for f in mappa_path.iterdir() 
                  if f.is_file() 
                  and f.suffix.lower() == '.txt'
                  and "feldolgozott" not in f.name.lower()]
    
    if not txt_fajlok:
        print(f"ℹ Figyelem: Nem található .txt fájl a mappában: {mappa_utvonal}")
        return
    
    print(f"Feldolgozás indítása: {len(txt_fajlok)} fájl...\n")
    
    sikeres = 0
    for txt_fajl in txt_fajlok:
        if feldolgoz_fajl(txt_fajl):
            sikeres += 1
    
    print(f"\n✓ Feldolgozás kész: {sikeres}/{len(txt_fajlok)} fájl sikeresen feldolgozva")

# ============================================================================
# FŐPROGRAM
# ============================================================================

def main():
    """Fő függvény"""
    if len(sys.argv) < 2:
        print("Teljes tétel fájl feldolgozása felolvasóbarát (TTS) formába")
        print("\nHasználat:")
        print("  python script/feldolgoz_teljes_tetel.py <bemenet_fájl>")
        print("  python script/feldolgoz_teljes_tetel.py <mappa_utvonal>")
        print("\nPéldák:")
        print("  python script/feldolgoz_teljes_tetel.py Tételek/A_cselekvokepesseg/A_cselekvokepesseg.txt")
        print("  python script/feldolgoz_teljes_tetel.py Tételek/A_cselekvokepesseg/")
        print("\nMegjegyzés:")
        print("  Ha mappát adsz meg, a script a mappában közvetlenül lévő összes .txt fájlt")
        print("  feldolgozza (nem az almappákban lévőket).")
        print("\nA feldolgozott fájlok a 'feldolgozott_tetelek' almappába kerülnek.")
        sys.exit(1)
    
    bemenet = sys.argv[1]
    bemenet_path = Path(bemenet)
    
    # Ha fájl
    if bemenet_path.is_file():
        feldolgoz_fajl(bemenet)
    # Ha mappa
    elif bemenet_path.is_dir():
        feldolgoz_mappa(bemenet)
    else:
        print(f"✗ Hiba: A megadott útvonal nem létezik: {bemenet}")
        sys.exit(1)

if __name__ == '__main__':
    main()

