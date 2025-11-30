#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Természetes podcast dialógus generálása - közvetlenül, intelligensen
"""

import re
import os
import random

# Melléknévi alakok szótára (1-900) - paragrafus számokhoz
def load_ordinal_dict():
    """Melléknévi alakok szótárának betöltése"""
    ordinals = {}
    # 1-99 közötti számok
    for i in range(1, 100):
        if i < 20:
            ones = ["", "első", "második", "harmadik", "negyedik", "ötödik", "hatodik", "hetedik", "nyolcadik", "kilencedik",
                   "tizedik", "tizenegyedik", "tizenkettedik", "tizenharmadik", "tizennegyedik", "tizenötödik",
                   "tizenhatodik", "tizenhetedik", "tizennyolcadik", "tizenkilencedik"]
            ordinals[str(i)] = ones[i]
        else:
            tens = ["", "", "huszadik", "harmincadik", "negyvenedik", "ötvenedik", "hatvanedik", "hetvenedik", "nyolcvanedik", "kilencvenedik"]
            ones_ord = ["", "egyedik", "kettedik", "harmadik", "negyedik", "ötödik", "hatodik", "hetedik", "nyolcadik", "kilencedik"]
            t = i // 10
            o = i % 10
            if o == 0:
                ordinals[str(i)] = tens[t]
            else:
                if t == 2:
                    ordinals[str(i)] = "huszon" + ones_ord[o]
                elif t == 3:
                    ordinals[str(i)] = "harminc" + ones_ord[o]
                elif t == 4:
                    ordinals[str(i)] = "negyven" + ones_ord[o]
                elif t == 5:
                    ordinals[str(i)] = "ötven" + ones_ord[o]
                elif t == 6:
                    ordinals[str(i)] = "hatvan" + ones_ord[o]
                elif t == 7:
                    ordinals[str(i)] = "hetven" + ones_ord[o]
                elif t == 8:
                    ordinals[str(i)] = "nyolcvan" + ones_ord[o]
                elif t == 9:
                    ordinals[str(i)] = "kilencven" + ones_ord[o]
    
    # 100-900 közötti számok
    hundreds = ["", "száz", "kétszáz", "háromszáz", "négyszáz", "ötszáz", "hatszáz", "hétszáz", "nyolcszáz", "kilencszáz"]
    for h in range(1, 10):
        for i in range(100):
            num = h * 100 + i
            if num > 900:
                break
            if i == 0:
                ordinals[str(num)] = hundreds[h] + "adik"
            else:
                if str(i) in ordinals:
                    ordinals[str(num)] = hundreds[h] + ordinals[str(i)]
    
    return ordinals

ORDINAL_DICT = load_ordinal_dict()

def number_to_ordinal(num_str):
    """Számot melléknévi alakban ad vissza (pl. 518 -> ötszáztizennyolcadik)"""
    if num_str in ORDINAL_DICT:
        return ORDINAL_DICT[num_str]
    # Ha nincs a szótárban, próbáljuk meg generálni
    try:
        num = int(num_str)
        if num < 1:
            return num_str
        # Nagy számoknál is próbáljuk meg
        if num >= 1000:
            return num_str  # Túl nagy számoknál maradjon számjegy
        # Generáljuk dinamikusan
        if num < 100:
            return number_to_ordinal(str(num))
        # 100-999 közötti számok
        hundreds = num // 100
        remainder = num % 100
        hundreds_map = {1: "száz", 2: "kétszáz", 3: "háromszáz", 4: "négyszáz", 5: "ötszáz",
                       6: "hatszáz", 7: "hétszáz", 8: "nyolcszáz", 9: "kilencszáz"}
        if remainder == 0:
            return hundreds_map.get(hundreds, "") + "adik"
        else:
            remainder_ord = number_to_ordinal(str(remainder))
            return hundreds_map.get(hundreds, "") + remainder_ord
    except:
        return num_str

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
        elif num < 10000:
            thousands_map = {1: "ezer", 2: "kétezer", 3: "háromezer", 4: "négyezer", 5: "ötezer",
                           6: "hatezer", 7: "hétezer", 8: "nyolcezer", 9: "kilencezer"}
            thousand = num // 1000
            remainder = num % 1000
            if remainder == 0:
                return thousands_map.get(thousand, "")
            else:
                return thousands_map.get(thousand, "") + number_to_words(str(remainder))
        else:
            return num_str
    except:
        return num_str

def convert_ptk_reference(text):
    """Ptk. hivatkozásokat alakítja át szöveges formába - rövidebb, érthetőbb formában"""
    pattern = r'Ptk\.\s*(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?'
    
    def replace_ptk(match):
        book = match.group(1)
        para = match.group(2)
        subpara = match.group(3)
        
        # Könyv szám melléknévi alakban
        book_num = int(book)
        book_ordinals = {
            1: "első", 2: "második", 3: "harmadik", 4: "negyedik", 
            5: "ötödik", 6: "hatodik", 7: "hetedik", 8: "nyolcadik", 9: "kilencedik"
        }
        book_word = book_ordinals.get(book_num, number_to_words(book))
        
        # Paragrafus szám MELLÉKNÉVI ALAKBAN (pl. ötszáztizennyolcadik)
        para_word = number_to_ordinal(para)
        result = f"a Polgári Törvénykönyv {book_word} könyvének {para_word} paragrafusa"
        
        if subpara:
            subpara_num = int(subpara)
            subpara_ordinals = {
                1: "első", 2: "második", 3: "harmadik", 4: "negyedik",
                5: "ötödik", 6: "hatodik", 7: "hetedik", 8: "nyolcadik", 9: "kilencedik"
            }
            subpara_word = subpara_ordinals.get(subpara_num, number_to_words(subpara))
            result += f" {subpara_word} bekezdése"
        
        return result
    
    return re.sub(pattern, replace_ptk, text)

def expand_abbreviations(text):
    """Rövidítések kibontása"""
    replacements = {
        r'\bpl\.': 'például',
        r'\bstb\.': 'és így tovább',
        r'\bvagyis': 'vagyis',
        r'\bazaz': 'azaz',
        r'\.\.\.': 'és így tovább',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def convert_latin(text):
    """Latin kifejezések fonetizálása"""
    latin_replacements = {
        r'\bex tunc\b': 'ex tunk',
        r'\bipso iure\b': 'ipszo júre',
        r'\bconditio sine qua non\b': 'kondíció szine kva non',
        r'\brestitutio in integrum\b': 'restitució in integrum',
    }
    
    for pattern, replacement in latin_replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def remove_special_chars(text):
    """Speciális karakterek eltávolítása"""
    text = re.sub(r'\(([^)]+)\)', r'\1', text)
    text = re.sub(r'^[\s]*[-•*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    return text

def tts_transform(text):
    """Teljes TTS transzformáció"""
    text = convert_ptk_reference(text)
    text = remove_special_chars(text)
    text = expand_abbreviations(text)
    text = convert_latin(text)
    
    # Dupla "a" eltávolítása (pl. "a a Polgári" -> "a Polgári")
    text = re.sub(r'\ba\s+a\s+', 'a ', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba\s+a\s+', 'a ', text, flags=re.IGNORECASE)  # Kétszer, ha három "a" van
    
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def parse_source_files(base_path):
    """Forrásfájlok beolvasása"""
    with open(f"{base_path}/kerdesek.txt", "r", encoding="utf-8") as f:
        questions = f.read().strip().split('\n\n')
    
    with open(f"{base_path}/valaszok.txt", "r", encoding="utf-8") as f:
        answers = f.read().strip().split('\n\n')
    
    with open(f"{base_path}/magyarazatok.txt", "r", encoding="utf-8") as f:
        explanations = f.read().strip().split('\n\n')
    
    questions = [re.sub(r'^\d+\.\s+', '', q.strip()) for q in questions if q.strip()]
    answers = [re.sub(r'^\d+\.\s+', '', a.strip()) for a in answers if a.strip()]
    explanations = [re.sub(r'^\d+\.\s+', '', e.strip()) for e in explanations if e.strip()]
    
    return questions, answers, explanations

def create_natural_question(q_text, index, total):
    """Természetes kérdés - változatos, bő szókincs, hangulatkifejezésekkel"""
    q_clean = q_text.strip()
    q_lower = q_clean.lower()
    
    # Ellenőrizzük, hogy a kérdés már tartalmaz-e bizonyos kifejezéseket
    has_kulonbseg = "mi a különbség" in q_lower or "különbség" in q_lower
    has_mi_van = q_lower.startswith("mi van") or q_lower.startswith("mi történik")
    has_mikor = q_lower.startswith("mikor") or q_lower.startswith("milyen")
    has_mi_a = q_lower.startswith("mi a") or q_lower.startswith("mi az")
    has_es_mi = q_lower.startswith("és mi")
    has_mi_a_helyzet = "mi a helyzet" in q_lower
    has_mi_van_akkor = "mi van akkor" in q_lower or "mi történik" in q_lower
    
    # Első kérdés - podcast stílusú, rövid, közvetlen
    if index == 0:
        variants = [
            f"Elsőként tisztázzuk: {q_clean}",
            f"Kezdjük azzal, hogy {q_lower}",
            f"Először is, {q_lower}",
            f"Első kérdés: {q_clean}",
            f"Kezdjük ezzel: {q_clean}",
        ]
        return variants[index % len(variants)]
    
    # Utolsó pár kérdés - podcast stílusú befejezések
    remaining = total - index
    if remaining <= 3:
        variants = [
            f"Végezetül beszéljünk {q_lower.replace('mi a', '').replace('mi az', '').replace('milyen', '').replace('mikor', '').replace('hogyan', '').replace('miért', '').strip(': ,')}",
            f"És végül: {q_clean}",
            f"Végül pedig: {q_clean}",
            f"És még egy fontos pont: {q_clean}",
            f"Zárásként: {q_clean}",
        ]
        if random.random() < 0.4:
            return variants[index % len(variants)]
    
    # Intelligens variánsok választása a kérdés típusa alapján
    variants = []
    
    # Ha már tartalmaz "mi a különbség"-et, ne duplikáljuk
    if has_kulonbseg:
        variants = [
            f"Érdekes! {q_clean}",
            f"Értem. {q_clean}",
            f"Szuper, {q_clean}",
            f"Megértettem, {q_clean}",
            f"Rendben, {q_clean}",
            f"És ezzel kapcsolatban: {q_lower}",
            f"És mondd, {q_lower}",
            f"Tehát {q_lower}",
            f"Oké, {q_lower}",
            f"Jó, {q_lower}",
            f"Szóval {q_lower}",
            f"Értem, {q_lower}",
            f"Köszönöm, {q_clean}",
            q_clean,
            q_clean,
            q_clean,
        ]
    # Ha már "mi van" vagy "mi történik" kezdetű
    elif has_mi_van:
        variants = [
            f"Érdekes! {q_clean}",
            f"Értem. {q_clean}",
            f"Szuper, {q_clean}",
            f"Megértettem, {q_clean}",
            f"És ezzel kapcsolatban: {q_lower}",
            f"És mondd, {q_lower}",
            f"Rendben, {q_lower}",
            f"Oké, {q_lower}",
            q_clean,
            q_clean,
        ]
    # Ha már "mikor" vagy "milyen" kezdetű
    elif has_mikor:
        variants = [
            f"Érdekes! {q_clean}",
            f"Értem. {q_clean}",
            f"Szuper, {q_clean}",
            f"És ezzel kapcsolatban: {q_lower}",
            f"Rendben, {q_lower}",
            q_clean,
            q_clean,
        ]
    # Ha már "és mi" kezdetű, ne adjunk hozzá újabb "és"-t
    elif has_es_mi:
        variants = [
            f"Érdekes! {q_clean}",
            f"Értem. {q_clean}",
            f"Szuper, {q_clean}",
            f"Rendben, {q_clean}",
            q_clean,
            q_clean,
        ]
    # Általános esetek - PODCAST STÍLUSÚ, rövid, közvetlen kérdések
    else:
        variants = [
            # Podcast stílusú átmenetek és kérdések
            f"Rendben. {q_clean}",
            f"Térjünk át {q_lower.replace('mi a', '').replace('mi az', '').replace('milyen', '').replace('mikor', '').replace('hogyan', '').replace('miért', '').strip(': ,')}",
            f"Menjünk tovább {q_lower.replace('mi a', '').replace('mi az', '').replace('milyen', '').replace('mikor', '').replace('hogyan', '').replace('miért', '').strip(': ,')}",
            f"Beszéljünk {q_lower.replace('mi a', '').replace('mi az', '').replace('milyen', '').replace('mikor', '').replace('hogyan', '').replace('miért', '').strip(': ,')}",
            f"Maradjunk {q_lower.replace('mi a', '').replace('mi az', '').replace('milyen', '').replace('mikor', '').replace('hogyan', '').replace('miért', '').strip(': ,')}",
            f"És ezzel kapcsolatban: {q_clean}",
            f"Érdekes pont: {q_clean}",
            f"És mi a helyzet akkor, ha {q_lower.replace('mi a helyzet', '').replace('mi van akkor', '').strip()}",
            f"És {q_lower}",
            f"Érdekes! {q_clean}",
            f"Rendben, {q_clean}",
            f"Oké, {q_clean}",
            f"Jó, {q_clean}",
            f"Szóval {q_lower}",
            f"Tehát {q_lower}",
            
            # Közvetlen kérdések (csak ha nincs benne már "mi a helyzet" vagy "mi van akkor")
            f"És mondd, {q_lower}",
            f"És ezzel kapcsolatban: {q_lower}",
            f"És ez hogy működik? {q_lower}",
            f"És mikor alkalmazható ez? {q_lower}",
            f"És hogyan működik ez? {q_lower}",
            # Csak akkor, ha nincs benne "mi a helyzet" vagy "mi van akkor"
            *([] if (has_mi_a_helyzet or has_mi_van_akkor or has_kulonbseg) else [
                f"És mi a helyzet akkor, ha {q_lower}",
                f"És mi történik, ha {q_lower}",
                f"És mi van akkor, ha {q_lower}",
            ]),
            
            # Kifejezőbb bevezetések
            f"Most beszéljünk kicsit arról, hogy {q_lower}",
            f"Térjünk át egy kicsit másik témára. {q_lower}",
            f"Térjünk vissza a témához. {q_lower}",
            f"Érdekelne, hogy {q_lower}",
            f"El tudnád magyarázni, kérlek, hogy {q_lower}",
            f"Segíts nekem megérteni, kérlek, hogy {q_lower}",
            f"Kérlek, magyarázd el, hogy {q_lower}",
            f"Tudnál segíteni ezzel: {q_lower}",
            f"Kérlek, segíts ezzel: {q_lower}",
            f"Segíts nekem kérlek: {q_lower}",
            
            # További változatosság - önkifejezés
            f"Ezt szeretném megérteni: {q_lower}",
            f"Ezzel kapcsolatban érdekelne: {q_lower}",
            f"Ezt nem értem teljesen: {q_lower}",
            f"Ezt részletesebben is megbeszélhetnénk: {q_lower}",
            f"Ezt még nem világos számomra: {q_lower}",
            f"Ezt szeretném jobban megérteni: {q_lower}",
            f"Ezt nem teljesen értem: {q_lower}",
            f"Ezt szeretném részletesebben megérteni: {q_lower}",
            f"Ezt még nem világos: {q_lower}",
            f"Ezt nem értem: {q_lower}",
            
            # Természetes átmenetek
            f"És akkor {q_lower}",
            f"És még egy dolog: {q_lower}",
            f"És még egy kérdés: {q_lower}",
            f"És még valami: {q_lower}",
            f"És azt is érdekelne: {q_lower}",
            f"És még egy pont: {q_lower}",
            f"És még egy: {q_lower}",
            f"És még valami érdekelne: {q_lower}",
            f"És még egy kérdésem van: {q_lower}",
            
            # Udvarias kérések
            f"Kérlek, segíts nekem ezzel: {q_lower}",
            f"Tudnál segíteni ezzel a kérdéssel: {q_lower}",
            f"Kérlek, magyarázd el részletesen: {q_lower}",
            f"El tudnál részletesebben magyarázni: {q_lower}",
            f"Kérlek, segíts megérteni: {q_lower}",
            f"Tudnál segíteni megérteni: {q_lower}",
            f"Kérlek, magyarázd el: {q_lower}",
            f"El tudnál magyarázni: {q_lower}",
            
            # Köszönés és pozitív visszajelzés
            f"Köszönöm, {q_clean}",
            f"Köszönöm szépen, {q_clean}",
            f"Nagyon köszönöm, {q_clean}",
            f"Köszönöm a segítséget, {q_clean}",
            f"Köszönöm, hogy segítesz, {q_clean}",
            
            # További természetes kifejezések
            f"Na jó, {q_lower}",
            f"Rendben, értem, {q_lower}",
            f"Oké, értem, {q_lower}",
            f"Jó, értem, {q_lower}",
            f"Értem, köszönöm, {q_lower}",
            f"Értem, szuper, {q_lower}",
            f"Értem, nagyszerű, {q_lower}",
            
            # Egyszerű, közvetlen kérdések (több példány a változatosságért)
            q_clean,
            q_clean,
            q_clean,
            q_clean,
            q_clean,
            q_clean,
            q_clean,
        ]
    
    # Választás index és hash kombinációval a változatosságért
    # Hash-t használunk, hogy ugyanaz a kérdés különböző témakörökben más variánst kapjon
    choice_index = (index * 7 + hash(q_text) % 1000) % len(variants)
    return variants[choice_index]

def create_natural_answer(a_text, e_text, is_first=False):
    """Természetes válasz - podcast stílusú, természetes, beszélgetős"""
    a_clean = a_text.strip()
    e_clean = e_text.strip() if e_text else ""
    
    # PODCAST STÍLUSÚ válasz kezdések - természetes, beszélgetős
    if is_first:
        starters = [
            "Szia!",
            "Szia!",
            "Szia!",
        ]
    else:
        starters = [
            # Egyszerű megerősítések (gyakran)
            "Igen,",
            "Úgy van,",
            "Valóban,",
            "Pontosan,",
            "Így van,",
            "Igen, pontosan,",
            "Igen, úgy van,",
            
            # Természetes bevezetések
            "Ez a kettő szorosan összetartozik.",
            "Ez egy fontos pont,",
            "Ez egy érdekes kérdés,",
            "Ez azért van, mert",
            "A lényeg az, hogy",
            "Nézd,",
            "Tehát",
            "Szóval",
            "Rendben,",
            "Oké,",
            
            # További változatosság
            "Ez így van,",
            "Pontosan úgy,",
            "Igen, ez így van,",
            
            # Üres (közvetlen válasz) - gyakran
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    
    # Hash-alapú választás a változatosságért
    starter_index = (hash(a_clean) * 13 + hash(e_clean if e_clean else "") * 7) % len(starters)
    starter = starters[starter_index]
    
    # Ha az első válasz és van "Szia!", akkor ne legyen dupla
    if is_first and starter == "Szia!":
        # Néha marad "Szia!", néha csak közvetlen válasz
        if random.random() < 0.5:
            starter = ""
    
    # Régi kód eltávolítva - csak a podcast stílusú részek maradtak
    # NAGYON BŐVÍTETT válasz kezdések - 80+ variáns
    old_starters = [
        # Pozitív megerősítések
        "Jó kérdés!",
        "Pontosan!",
        "Nagyszerű kérdés!",
        "Kiváló kérdés!",
        "Remek kérdés!",
        "Tökéletes kérdés!",
        "Fantasztikus kérdés!",
        "Szuper kérdés!",
        
        # Egyszerű megerősítések
        "Igen,",
        "Úgy van,",
        "Pontosan úgy,",
        "Igen, pontosan,",
        "Igen, úgy van,",
        "Igen, ez így van,",
        "Igen, pontosan így,",
        
        # Természetes bevezetések (ritkábban "Nos,")
        "Szóval,",
        "Rendben,",
        "Nézd,",
        "Tehát,",
        "Hát,",
        "Na,",
        "Na jó,",
        "Rendben van,",
        "Oké,",
        "Jó,",
        "Értem,",
        "Értem már,",
        "Világos,",
        "Rendben, értem,",
        "Oké, értem,",
        "Jó, értem,",
        
        # Kifejezőbb bevezetések
        "Ez egy nagyon fontos kérdés,",
        "Ez egy összetett kérdés,",
        "Ez egy érdekes kérdés,",
        "Ez egy jó kérdés,",
        "Ez egy fontos kérdés,",
        "Ez egy nagyon jó kérdés,",
        "Ez egy remek kérdés,",
        "Ez egy kiváló kérdés,",
        
        # További változatosság (NEM köszönés a kérdésért, csak pozitív reakció)
        "Rendben, értem a kérdést,",
        "Értem, mit kérdezel,",
        "Világos, mit szeretnél tudni,",
        "Értem a kérdést,",
        "Rendben,",
        
        # Természetes reakciók
        "Érdekes kérdés,",
        "Érdekes pont,",
        "Érdekes megközelítés,",
        "Érdekes szempont,",
        
        # További pozitív kifejezések
        "Nagyszerű,",
        "Kiváló,",
        "Remek,",
        "Tökéletes,",
        "Fantasztikus,",
        "Szuper,",
        "Nagyon jó,",
        "Kiválóan,",
        
        # Megértés kifejezései
        "Megértettem,",
        "Értem már,",
        "Most már értem,",
        "Világos számomra,",
        "Értem, köszönöm,",
        
        # Természetes átmenetek
        "Na jó, szóval,",
        "Rendben, tehát,",
        "Oké, szóval,",
        "Jó, tehát,",
        "Értem, szóval,",
        "Értem, tehát,",
        
        # További változatosság
        "Igen, pontosan,",
        "Igen, úgy van,",
        "Igen, ez így van,",
        "Igen, pontosan így,",
        "Úgy van, pontosan,",
        "Pontosan úgy, ahogy mondod,",
        
        # Ritkábban használt, de természetes
        "Nos,",
        "Hát nézd,",
        "Na nézd,",
        "Hát persze,",
        "Na persze,",
        
        # Üres (közvetlen válasz)
        "",
        "",
        "",
        "",
        "",
    ]
    
    # Hash-alapú választás a változatosságért
    starter_index = (hash(a_clean) * 13 + hash(e_clean if e_clean else "") * 7) % len(starters)
    starter = starters[starter_index]
    
    # Ha van magyarázat, összefésüljük - BŐVÍTETT átmenetekkel
    if e_clean:
        transitions = [
            "Ez azért van, mert",
            "A lényeg az, hogy",
            "Nézd, a jogszabályi háttér szerint",
            "Fontos kiemelni, hogy",
            "Részletesebben",
            "Konkrétabban",
            "Tehát",
            "Pontosabban",
            "És ami még érdekesebb,",
            "És itt jön az érdekes rész,",
            "De!",
            "És ami még fontos,",
            "És ami a legfontosabb,",
            "És még egy fontos dolog,",
            "És még egy érdekes pont,",
            "És még egy szempont,",
            "És még egy fontos szempont,",
            "És még egy érdekes részlet,",
            "És még egy fontos részlet,",
            "És még egy dolog,",
            "És még egy pont,",
            "És még egy fontos pont,",
            "És még egy érdekes rész,",
            "És még egy fontos rész,",
        ]
        transition_index = (hash(e_clean) * 11) % len(transitions)
        transition = transitions[transition_index]
        
        # Ellenőrizzük, hogy ne legyen duplikáció
        # Ha a válasz már tartalmazza az átmenet tartalmát, ne használjuk
        if transition.lower().replace(",", "").strip() in a_clean.lower():
            # Egyszerűen csak összefésüljük vesszővel
            if e_clean[0].islower():
                combined = f"{a_clean}, {e_clean}"
            else:
                combined = f"{a_clean}, {e_clean}"
        else:
            if e_clean[0].islower():
                combined = f"{a_clean} {transition} {e_clean}"
            else:
                combined = f"{a_clean} {transition}, {e_clean}"
    else:
        combined = a_clean
    
    # Válasz összeállítása
    if starter:
        if starter.endswith("!"):
            result = f"{starter} {combined}"
        elif starter.endswith(","):
            result = f"{starter} {combined.lower()}"
        else:
            result = f"{starter} {combined.lower()}"
    else:
        result = combined
    
    return result

def get_topic_name_from_path(base_path):
    """Témakör neve a mappa útvonalból"""
    # Pl: "Tételek/A_deliktualis_karfelelosseg" -> "A_deliktualis_karfelelosseg"
    return os.path.basename(base_path.rstrip('/\\'))

def main(base_path=None):
    """Fő függvény - dialógus generálása"""
    import sys
    
    # Ha nincs megadva útvonal, próbáljuk az első parancssori argumentumot
    if base_path is None:
        if len(sys.argv) > 1:
            base_path = sys.argv[1]
        else:
            # Alapértelmezett: aktuális példa
            base_path = "Tételek/A_deliktualis_karfelelosseg"
    
    # Ellenőrzés: létezik-e a mappa
    if not os.path.exists(base_path):
        print(f"Hiba: A mappa nem létezik: {base_path}")
        sys.exit(1)
    
    # Ellenőrzés: léteznek-e a szükséges fájlok
    required_files = ["kerdesek.txt", "valaszok.txt", "magyarazatok.txt"]
    for file in required_files:
        file_path = os.path.join(base_path, file)
        if not os.path.exists(file_path):
            print(f"Hiba: Hiányzó fájl: {file_path}")
            sys.exit(1)
    
    print(f"Feldolgozás: {base_path}")
    
    questions, answers, explanations = parse_source_files(base_path)
    
    if len(questions) != len(answers) or len(questions) != len(explanations):
        print(f"Figyelmeztetés: A fájlokban eltérő számú tétel van!")
        print(f"  Kérdések: {len(questions)}, Válaszok: {len(answers)}, Magyarázatok: {len(explanations)}")
    
    full_dialog = []
    questions_only = []
    answers_only = []
    
    # Rövid bevezető a dialógushoz
    topic_name = get_topic_name_from_path(base_path)
    topic_display = topic_name.replace("_", " ").replace("A ", "").replace("Az ", "")
    
    intro_variants = [
        f"Szia! Kezdjünk is bele a {topic_display} témakörébe. Ez egy elég nagy falat, szóval haladjunk lépésről lépésre.",
        f"Szia! Beszéljünk ma a {topic_display} témakörről. Haladjunk lépésről lépésre.",
        f"Szia! Kezdjük a {topic_display} témakörrel. Ez egy fontos rész, szóval menjünk át alaposan.",
        f"Szia! Ma a {topic_display} témakörről fogunk beszélgetni. Haladjunk lépésről lépésre.",
        f"Szia! Kezdjünk bele a {topic_display} témakörébe. Menjünk át alaposan a fontosabb pontokon.",
    ]
    
    intro = intro_variants[hash(topic_name) % len(intro_variants)]
    full_dialog.append(intro)
    full_dialog.append('<break time="3s"/>')
    
    # Reakciók a válaszokra (kérdező reakciói) - podcast stílusú, rövidebb
    questioner_reactions = [
        "Köszönöm, ez így tiszta.",
        "Világos.",
        "Értem.",
        "Rendben.",
        "Oké.",
        "Köszönöm.",
        "Értem, köszönöm.",
        "Világos, köszönöm.",
        "",  # Néha nincs reakció
        "",  # Néha nincs reakció
        "",  # Néha nincs reakció
        "",  # Néha nincs reakció
        "",  # Néha nincs reakció
    ]
    
    # Rövid megerősítések/visszakérdezések a válaszolótól - ritkábban podcastban
    answerer_followups = [
        "",  # Ritkábban használjuk podcastban
        "",  # Ritkábban használjuk podcastban
        "",  # Ritkábban használjuk podcastban
        "",  # Ritkábban használjuk podcastban
        "",  # Ritkábban használjuk podcastban
    ]
    
    # Következtetések/összefoglalások a válasz után - ritkábban podcastban
    answerer_conclusions = [
        "",  # Ritkábban használjuk podcastban
        "",  # Ritkábban használjuk podcastban
        "",  # Ritkábban használjuk podcastban
    ]
    
    # Előző mondat tárolása a duplikáció ellenőrzéshez
    previous_text = intro.lower()
    
    for i, (q, a, e) in enumerate(zip(questions, answers, explanations)):
        q_tts = tts_transform(q)
        a_tts = tts_transform(a)
        e_tts = tts_transform(e)
        
        natural_q = create_natural_question(q_tts, i, len(questions))
        natural_a = create_natural_answer(a_tts, e_tts, is_first=(i == 0))
        
        # Duplikáció ellenőrzés és eltávolítás
        # Ha az előző mondatban már szerepel egy szó/mondatrész, ne ismételjük meg
        natural_q_lower = natural_q.lower()
        
        # Közös szavak/mondatrészek ellenőrzése (legalább 3 karakter hosszúak)
        words_prev = set([w for w in previous_text.split() if len(w) >= 3])
        words_q = set([w for w in natural_q_lower.split() if len(w) >= 3])
        
        # Ha túl sok közös szó van, egyszerűsítjük a kérdést
        common_words = words_prev.intersection(words_q)
        if len(common_words) > 2:  # Ha több mint 2 közös szó van
            # Egyszerűsítjük a kérdést - eltávolítjuk a redundáns bevezető részeket
            if natural_q_lower.startswith("kezdjük ezzel a kérdéssel:"):
                natural_q = natural_q[len("Kezdjük ezzel a kérdéssel: "):]
            elif natural_q_lower.startswith("kezdjük az első kérdéssel:"):
                natural_q = natural_q[len("Kezdjük az első kérdéssel: "):]
            elif natural_q_lower.startswith("első kérdésem:"):
                natural_q = natural_q[len("Első kérdésem: "):]
            elif natural_q_lower.startswith("ezzel a kérdéssel szeretnék kezdeni:"):
                natural_q = natural_q[len("Ezzel a kérdéssel szeretnék kezdeni: "):]
        
        # Válaszoló válasza
        full_dialog.append(natural_q)
        full_dialog.append(natural_a)
        
        # Frissítjük az előző szöveget
        previous_text = (natural_q + " " + natural_a).lower()
        
        # Podcast struktúra - ritkábban reakciók, csak néha
        # 20% esély: kérdező rövid reakcióval (podcastban ritkábban)
        if random.random() < 0.2:
            reaction_choice = (hash(natural_a) * 11 + i * 5) % len(questioner_reactions)
            reaction = questioner_reactions[reaction_choice]
            if reaction:
                full_dialog.append(reaction)
        
        full_dialog.append('<break time="5s"/>')
        
        # Kérdések és válaszok külön fájlokhoz
        questions_only.append(natural_q)
        questions_only.append('<break time="5s"/>')
        
        answers_only.append(natural_a)
        # Ha volt followup vagy conclusion, azt is hozzáadjuk a válaszolóhoz
        if random.random() < 0.3:
            followup_choice = (hash(natural_a) * 7 + i * 3) % len(answerer_followups)
            followup = answerer_followups[followup_choice]
            if followup:
                answers_only.append(followup)
        if random.random() < 0.2:
            conclusion_choice = (hash(natural_a) * 13 + i * 7) % len(answerer_conclusions)
            conclusion = answerer_conclusions[conclusion_choice]
            if conclusion:
                answers_only.append(conclusion)
        answers_only.append('<break time="5s"/>')
    
    # Kimeneti mappa létrehozása
    output_dir = os.path.join(base_path, "Dialógus")
    os.makedirs(output_dir, exist_ok=True)
    
    # Témakör neve a fájlnevekhez (már korábban meghatározva)
    
    # Fájlok írása
    output_files = {
        f"{output_dir}/Tanulokartya-Dialogus_{topic_name}.txt": full_dialog,
        f"{output_dir}/Tanulokartya-Dialogus_{topic_name}_kerdezo.txt": questions_only,
        f"{output_dir}/Tanulokartya-Dialogus_{topic_name}_valaszolo.txt": answers_only,
    }
    
    for file_path, content in output_files.items():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('\n\n'.join(content))
        print(f"✓ Létrehozva: {file_path}")
    
    print(f"\nKész! {len(questions)} tétel feldolgozva.")

if __name__ == "__main__":
    main()

