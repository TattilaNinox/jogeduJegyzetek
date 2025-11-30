#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS-optimalizált dialógus generálása tanulókártyákból
"""

import re
import os

def number_to_words(num_str):
    """Számokat szavakkal írja ki"""
    num_map = {
        '1': 'első', '2': 'második', '3': 'harmadik', '4': 'negyedik', '5': 'ötödik',
        '6': 'hatodik', '7': 'hetedik', '8': 'nyolcadik', '9': 'kilencedik', '10': 'tizedik',
        '11': 'tizenegyedik', '12': 'tizenkettedik', '13': 'tizenharmadik', '14': 'tizennegyedik',
        '15': 'tizenötödik', '16': 'tizenhatodik', '17': 'tizenhetedik', '18': 'tizennyolcadik',
        '19': 'tizenkilencedik', '20': 'huszadik', '21': 'huszonegyedik', '22': 'huszonkettedik',
        '23': 'huszonharmadik', '24': 'huszonnegyedik', '25': 'huszonötödik',
        '26': 'huszonhatodik', '27': 'huszonhetedik', '28': 'huszonnyolcadik',
        '29': 'huszonkilencedik', '30': 'harmincadik', '31': 'harmincegyedik',
        '32': 'harminckettedik', '33': 'harmincharmadik', '34': 'harmincnegyedik',
        '35': 'harmincötödik', '36': 'harminchatodik', '37': 'harminchetedik',
        '38': 'harmincnyolcadik', '39': 'harminckilencedik', '40': 'negyvenedik',
        '41': 'negyvenegyedik', '42': 'negyvenkettedik', '43': 'negyvenharmadik',
        '44': 'negyvennegyedik', '45': 'negyvenötödik', '46': 'negyvenhatodik',
        '47': 'negyvenhetedik', '48': 'negyvennyolcadik', '49': 'negyvenkilencedik',
        '50': 'ötvenedik'
    }
    
    # Egyszerű számok
    if num_str in num_map:
        return num_map[num_str]
    
    # Összetett számok (pl. "18" -> "tizennyolc")
    if len(num_str) == 2:
        tens = {'1': 'tizen', '2': 'huszon', '3': 'harminc', '4': 'negyven', '5': 'ötven'}
        ones = {'0': '', '1': 'egy', '2': 'kettő', '3': 'három', '4': 'négy', '5': 'öt',
                '6': 'hat', '7': 'hét', '8': 'nyolc', '9': 'kilenc'}
        if num_str[0] in tens and num_str[1] in ones:
            return tens[num_str[0]] + ones[num_str[1]]
    
    return num_str

def expand_abbreviations(text):
    """Rövidítések kibontása"""
    abbrev_map = {
        r'\bPtk\.': 'Polgári Törvénykönyv',
        r'\bpl\.': 'például',
        r'\bstb\.': 'és így tovább',
        r'\b§': 'paragrafus',
        r'\b\((\d+)\)': lambda m: f'{number_to_words(m.group(1))} bekezdés',
    }
    
    for pattern, replacement in abbrev_map.items():
        if callable(replacement):
            text = re.sub(pattern, replacement, text)
        else:
            text = re.sub(pattern, replacement, text)
    
    return text

def process_legal_references(text):
    """Törvényi hivatkozások feldolgozása"""
    # Ptk. 6:518. § -> Polgári Törvénykönyv hatodik könyvének ötszáztizennyolcadik paragrafusa
    def replace_ptk_ref(match):
        book = number_to_words(match.group(1))
        para = match.group(2)
        # Egyszerűsített: csak a számot írjuk ki
        para_words = number_to_words(para) if para.isdigit() else para
        return f'Polgári Törvénykönyv {book} könyvének {para_words} paragrafusa'
    
    text = re.sub(r'Ptk\.\s*(\d+):(\d+)\.\s*§', replace_ptk_ref, text)
    
    # § (1) -> paragrafus első bekezdése
    text = re.sub(r'§\s*\((\d+)\)', lambda m: f'paragrafus {number_to_words(m.group(1))} bekezdése', text)
    
    # (1) bekezdés -> első bekezdés
    text = re.sub(r'\((\d+)\)\s*bekezdés', lambda m: f'{number_to_words(m.group(1))} bekezdés', text)
    
    return text

def remove_formatting(text):
    """Formázás eltávolítása"""
    # Markdown formázás
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic*
    text = re.sub(r'`([^`]+)`', r'\1', text)  # `code`
    
    # Lista jelek
    text = re.sub(r'^[\s]*[-•*]\s+', '', text, flags=re.MULTILINE)
    
    # Zárójelek tartalmának beillesztése
    text = re.sub(r'\(([^)]+)\)', r', \1', text)
    
    # Felsorolások folyamatos mondatokká alakítása
    text = re.sub(r'([a-záéíóöőúüű])\s*\n\s*([a-záéíóöőúüű])', r'\1, \2', text)
    
    return text

def process_numbers(text):
    """Számok feldolgozása"""
    # Törvényi hivatkozásokban lévő számok már feldolgozva vannak
    # Egyéb számok (pl. "5 év" -> "öt év")
    def replace_number(match):
        num = match.group(1)
        if num.isdigit() and 1 <= int(num) <= 50:
            return number_to_words(num)
        return num
    
    # Csak akkor cseréljük le, ha nem törvényi hivatkozás része
    text = re.sub(r'\b(\d+)\s+(év|évig|éven|éves)', lambda m: f'{number_to_words(m.group(1))} {m.group(2)}', text)
    
    return text

def process_latin(text):
    """Latin kifejezések fonetikusan"""
    latin_map = {
        'ex tunc': 'ex tunk',
        'ipso iure': 'ipszo júre',
        'conditio sine qua non': 'kondíció szine kva non',
        'restitutio in integrum': 'restitució in integrum',
    }
    
    for latin, phonetic in latin_map.items():
        text = text.replace(latin, phonetic)
    
    return text

def clean_text(text):
    """Teljes szöveg tisztítása"""
    # Többszörös szóközök
    text = re.sub(r'\s+', ' ', text)
    
    # Többszörös pontok
    text = re.sub(r'\.{2,}', '.', text)
    
    # Szóközök írásjelek előtt/után
    text = re.sub(r'\s+([,\.;:!?])', r'\1', text)
    text = re.sub(r'([,\.;:!?])\s*([a-záéíóöőúüű])', r'\1 \2', text, flags=re.IGNORECASE)
    
    return text.strip()

def tts_optimize(text):
    """TTS optimalizálás teljes folyamata"""
    text = expand_abbreviations(text)
    text = process_legal_references(text)
    text = process_numbers(text)
    text = process_latin(text)
    text = remove_formatting(text)
    text = clean_text(text)
    return text

def create_dialogues():
    """Dialógusok létrehozása"""
    base_path = "Tételek/A_deliktualis_karfelelosseg"
    output_path = os.path.join(base_path, "Dialógus")
    
    # Mappa létrehozása
    os.makedirs(output_path, exist_ok=True)
    
    # Fájlok beolvasása
    with open(os.path.join(base_path, "kerdesek.txt"), "r", encoding="utf-8") as f:
        questions = f.read().strip().split('\n\n')
    
    with open(os.path.join(base_path, "valaszok.txt"), "r", encoding="utf-8") as f:
        answers = f.read().strip().split('\n\n')
    
    with open(os.path.join(base_path, "magyarazatok.txt"), "r", encoding="utf-8") as f:
        explanations = f.read().strip().split('\n\n')
    
    # Számozás eltávolítása és tisztítás
    def clean_item(item):
        # Eltávolítjuk a számozást (pl. "1. ", "2. ")
        item = re.sub(r'^\d+\.\s*', '', item.strip())
        return item
    
    questions = [clean_item(q) for q in questions if q.strip()]
    answers = [clean_item(a) for a in answers if a.strip()]
    explanations = [clean_item(e) for e in explanations if e.strip()]
    
    # Dialógusok generálása
    full_dialog = []
    question_only = []
    answer_only = []
    
    transitions = [
        "Ez azért van, mert",
        "A jogszabályi háttér szerint",
        "Fontos kiemelni, hogy",
        "Részletesebben",
        "Konkrétabban",
        "A törvényi szabályozás szerint",
        "Ez azt jelenti, hogy",
        "Ebből következik, hogy",
    ]
    
    for i, (q, a, e) in enumerate(zip(questions, answers, explanations)):
        # TTS optimalizálás
        q_opt = tts_optimize(q)
        a_opt = tts_optimize(a)
        e_opt = tts_optimize(e)
        
        # Átkötés választás
        transition = transitions[i % len(transitions)]
        
        # Válasz és magyarázat összefűzése
        combined_answer = f"{a_opt}. {transition} {e_opt}"
        
        # Teljes dialógus
        full_dialog.append(f"Kérdező: {q_opt}")
        full_dialog.append(f"Válaszoló: {combined_answer}")
        full_dialog.append("<break time=\"5s\"/>")
        
        # Külön fájlok
        question_only.append(q_opt)
        question_only.append("<break time=\"5s\"/>")
        
        answer_only.append(combined_answer)
        answer_only.append("<break time=\"5s\"/>")
    
    # Fájlok írása
    output_file_full = os.path.join(output_path, "Tanulokartya-Dialogus_A_deliktualis_karfelelosseg.txt")
    output_file_questions = os.path.join(output_path, "Tanulokartya-Dialogus_A_deliktualis_karfelelosseg_kerdezo.txt")
    output_file_answers = os.path.join(output_path, "Tanulokartya-Dialogus_A_deliktualis_karfelelosseg_valaszolo.txt")
    
    with open(output_file_full, "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_dialog))
    
    with open(output_file_questions, "w", encoding="utf-8") as f:
        f.write("\n\n".join(question_only))
    
    with open(output_file_answers, "w", encoding="utf-8") as f:
        f.write("\n\n".join(answer_only))
    
    print(f"Fájlok létrehozva:")
    print(f"  - {output_file_full}")
    print(f"  - {output_file_questions}")
    print(f"  - {output_file_answers}")

if __name__ == "__main__":
    create_dialogues()


















