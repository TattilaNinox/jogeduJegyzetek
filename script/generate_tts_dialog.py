#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS-optimalizált dialógus generálása tanulókártyákból
"""

import re
import os
import random

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
            # Nagyobb számoknál visszatérünk a számjegyekre
            return num_str
    except:
        return num_str

def convert_ptk_reference(text):
    """Ptk. hivatkozásokat alakítja át szöveges formába"""
    # Ptk. 6:518. § mintájára
    pattern = r'Ptk\.\s*(\d+):(\d+)\.\s*§(?:\s*\((\d+)\))?'
    
    def replace_ptk(match):
        book = match.group(1)
        para = match.group(2)
        subpara = match.group(3)
        
        book_word = number_to_words(book)
        para_word = number_to_words(para)
        
        result = f"a Polgári Törvénykönyv {book_word} könyvének {para_word} paragrafusa"
        
        if subpara:
            subpara_word = number_to_words(subpara)
            result += f" {subpara_word} bekezdése"
        
        return result
    
    return re.sub(pattern, replace_ptk, text)

def expand_abbreviations(text):
    """Rövidítések kibontása - de ne a már átalakított Ptk hivatkozásokban"""
    # Először a Ptk hivatkozásokat kezeljük külön
    # Aztán a többi rövidítést
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
    """Speciális karakterek eltávolítása és beillesztése a szövegbe"""
    # Zárójelek eltávolítása, tartalom beillesztése
    text = re.sub(r'\(([^)]+)\)', r'\1', text)
    
    # Listajeles pontok eltávolítása
    text = re.sub(r'^[\s]*[-•*]\s+', '', text, flags=re.MULTILINE)
    
    # Markdown formázás eltávolítása
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Számozott listák folyamatos szöveggé alakítása
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    return text

def convert_numbers_in_text(text):
    """Számok átalakítása szöveges formába"""
    # Először a Ptk hivatkozásokat kezeljük külön
    text = convert_ptk_reference(text)
    
    # Egyszerű számok (1-1000 közötti) átalakítása
    def replace_number(match):
        num_str = match.group(0)
        # Ne alakítsuk át, ha már egy hivatkozás része
        if 'könyv' in text[max(0, match.start()-20):match.start()] or \
           'paragrafus' in text[max(0, match.start()-20):match.start()]:
            return num_str
        return number_to_words(num_str)
    
    # Csak azok a számok, amelyek nem részei már átalakított hivatkozásoknak
    text = re.sub(r'\b(\d{1,4})\b', replace_number, text)
    
    return text

def tts_transform(text):
    """Teljes TTS transzformáció"""
    # Először a Ptk hivatkozásokat alakítjuk át (mielőtt a rövidítéseket kibontanánk)
    text = convert_ptk_reference(text)
    
    # Speciális karakterek eltávolítása
    text = remove_special_chars(text)
    
    # Rövidítések kibontása (de már nem lesz benne Ptk.)
    text = expand_abbreviations(text)
    
    # Latin kifejezések
    text = convert_latin(text)
    
    # Szöveg tisztítása
    text = re.sub(r'\s+', ' ', text)  # Többszörös szóközök
    text = text.strip()
    
    return text

def parse_source_files():
    """Forrásfájlok beolvasása és elemzése"""
    base_path = "Tételek/A_deliktualis_karfelelosseg"
    
    with open(f"{base_path}/kerdesek.txt", "r", encoding="utf-8") as f:
        questions = f.read().strip().split('\n\n')
    
    with open(f"{base_path}/valaszok.txt", "r", encoding="utf-8") as f:
        answers = f.read().strip().split('\n\n')
    
    with open(f"{base_path}/magyarazatok.txt", "r", encoding="utf-8") as f:
        explanations = f.read().strip().split('\n\n')
    
    # Számozás eltávolítása
    questions = [re.sub(r'^\d+\.\s+', '', q.strip()) for q in questions if q.strip()]
    answers = [re.sub(r'^\d+\.\s+', '', a.strip()) for a in answers if a.strip()]
    explanations = [re.sub(r'^\d+\.\s+', '', e.strip()) for e in explanations if e.strip()]
    
    return questions, answers, explanations

def create_natural_question(question_text, index, total_count):
    """Természetes podcast stílusú kérdés - egyetemi szintű, változatos, mint a minta"""
    # Széles repertoár - a minta alapján
    question_variants = [
        f"Érdekes! {question_text.lower()}",
        f"Értem. Tehát {question_text.lower()}",
        f"És mi van akkor, ha {question_text.lower()}",
        f"És mondd, {question_text.lower()}",
        f"És mi a helyzet akkor, ha {question_text.lower()}",
        f"Tehát {question_text.lower()}",
        f"És ez hogy működik? {question_text.lower()}",
        f"És mi történik, ha {question_text.lower()}",
        f"És mi a különbség akkor, hogy {question_text.lower()}",
        f"És mikor alkalmazható ez? {question_text.lower()}",
        f"És mi van akkor, ha {question_text.lower()}",
        f"Érdekelne, hogy {question_text.lower()}",
        f"Tudnád elmagyarázni, kérlek, hogy {question_text.lower()}",
        f"Segíts nekem megérteni, kérlek, hogy {question_text.lower()}",
        f"Ezt szeretném megérteni: {question_text.lower()}",
        f"Ezzel kapcsolatban érdekelne: {question_text.lower()}",
        question_text,  # Néha csak simán a kérdés - természetes
        question_text,
        question_text,
    ]
    
    # Első kérdés speciális - udvarias, de természetes
    if index == 0:
        variants_first = [
            f"Szia, segíts nekem kérlek ezzel: {question_text.lower()}",
            f"Szia, kérlek, segíts nekem ezzel: {question_text.lower()}",
            f"Köszönöm, hogy segítesz. {question_text.lower()}",
            f"Szia, tudnál segíteni ezzel: {question_text.lower()}",
        ]
        return random.choice(variants_first)
    
    # Közepén változatos bevezetők - a minta alapján
    if random.random() < 0.4:  # 40% eséllyel változatos bevezető
        mid_intros = [
            f"Érdekes! {question_text.lower()}",
            f"Értem. Tehát {question_text.lower()}",
            f"És mi van akkor, ha {question_text.lower()}",
            f"És mondd, {question_text.lower()}",
            f"És mi a helyzet akkor, ha {question_text.lower()}",
            f"Tehát {question_text.lower()}",
            f"És ez hogy működik? {question_text.lower()}",
            f"És mi történik, ha {question_text.lower()}",
            f"És mi a különbség akkor, hogy {question_text.lower()}",
            f"És mikor alkalmazható ez? {question_text.lower()}",
            f"Most beszéljünk kicsit arról, hogy {question_text.lower()}",
            f"Térjünk át egy kicsit másik témára. {question_text.lower()}",
            f"Térjünk vissza a témához. {question_text.lower()}",
        ]
        return random.choice(mid_intros)
    
    # Utolsó pár kérdésnél lehet rövidebb bevezető
    remaining = total_count - index
    if remaining <= 3:
        if random.random() < 0.3:  # Csak 30% eséllyel
            final_intros = [
                f"És ezzel kapcsolatban: {question_text.lower()}",
                f"Végül pedig, {question_text.lower()}",
                f"És végül, {question_text.lower()}",
            ]
            return random.choice(final_intros)
    
    # Legtöbbször változatos kérdések
    return random.choice(question_variants)

def create_natural_answer(answer_text, explanation_text, index):
    """Természetes podcast stílusú válasz - egyetemi szintű, változatos, mint a minta"""
    # Széles repertoár válasz kezdések - a minta alapján
    answer_starters = [
        "Jó kérdés!",
        "Pontosan!",
        "Igen,",
        "Úgy van,",
        "Igen, úgy van,",
        "Nos,",
        "Szóval,",
        "Rendben,",
        "Nézd,",
        "Tehát,",
        "Ez egy nagyon fontos kérdés,",
        "Ez egy összetett kérdés,",
        "",
        "",
        "",
        "",
    ]
    
    starter = random.choice(answer_starters)
    
    # Ha van magyarázat, természetesen összefésüljük - változatos átkötésekkel
    if explanation_text.strip():
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
        ]
        transition = random.choice(transitions)
        explanation_clean = explanation_text.strip()
        
        if explanation_clean[0].islower():
            combined = f"{answer_text} {transition} {explanation_clean}"
        else:
            combined = f"{answer_text} {transition}, {explanation_clean}"
    else:
        combined = answer_text
    
    # Válasz befejezések (ritkán) - egyetemi szintű
    answer_endings = [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "Ez így világos?",
        "Remélem segített.",
    ]
    
    ending = random.choice(answer_endings)
    
    if starter:
        if starter.endswith("!"):
            result = f"{starter} {combined}"
        else:
            result = f"{starter} {combined.lower()}"
    else:
        result = combined
    
    if ending:
        result += f" {ending}"
    
    return result

def add_natural_reactions():
    """Természetes reakciók a válaszok után - egyetemi szintű"""
    reactions = [
        "Értem, köszönöm.",
        "Köszönöm, értem.",
        "Rendben, köszönöm.",
        "Köszönöm a segítséget.",
        "Értem, köszönöm szépen.",
        "",
        "",
        "",
        "",
        "",
    ]
    return random.choice(reactions)

def generate_dialog(questions, answers, explanations):
    """POTTCAST dialógus generálása - valódi, életszerű beszélgetés"""
    full_dialog = []
    questions_only = []
    answers_only = []
    
    total_count = len(questions)
    
    for i, (q, a, e) in enumerate(zip(questions, answers, explanations)):
        # TTS transzformáció
        q_tts = tts_transform(q)
        a_tts = tts_transform(a)
        e_tts = tts_transform(e)
        
        # Természetes podcast stílusú kérdés és válasz
        natural_question = create_natural_question(q_tts, i, total_count)
        natural_answer = create_natural_answer(a_tts, e_tts, i)
        
        # Természetes reakció (ritkán)
        reaction = ""
        if random.random() < 0.2:  # 20% eséllyel reakció
            reaction = add_natural_reactions()
        
        # Teljes dialógus - NINCS "Kérdező:" vagy "Válaszoló:" címke!
        full_dialog.append(natural_question)
        full_dialog.append(natural_answer)
        if reaction:
            full_dialog.append(reaction)
        full_dialog.append('<break time="5s"/>')
        
        # Csak kérdések - NINCS címke!
        questions_only.append(natural_question)
        questions_only.append('<break time="5s"/>')
        
        # Csak válaszok - NINCS címke!
        answers_only.append(natural_answer)
        if reaction:
            answers_only.append(reaction)
        answers_only.append('<break time="5s"/>')
    
    return '\n\n'.join(full_dialog), '\n\n'.join(questions_only), '\n\n'.join(answers_only)

def main():
    """Főprogram"""
    print("Forrásfájlok beolvasása...")
    questions, answers, explanations = parse_source_files()
    
    print(f"{len(questions)} kérdés-válasz-magyarázat pár feldolgozása...")
    
    print("TTS transzformációk alkalmazása...")
    full_dialog, questions_only, answers_only = generate_dialog(questions, answers, explanations)
    
    # Kimeneti mappa létrehozása
    output_dir = "Tételek/A_deliktualis_karfelelosseg/Dialógus"
    os.makedirs(output_dir, exist_ok=True)
    
    # Fájlok írása
    print("Kimeneti fájlok létrehozása...")
    
    with open(f"{output_dir}/Tanulokartya-Dialogus_A_deliktualis_karfelelosseg.txt", "w", encoding="utf-8") as f:
        f.write(full_dialog)
    
    with open(f"{output_dir}/Tanulokartya-Dialogus_A_deliktualis_karfelelosseg_kerdezo.txt", "w", encoding="utf-8") as f:
        f.write(questions_only)
    
    with open(f"{output_dir}/Tanulokartya-Dialogus_A_deliktualis_karfelelosseg_valaszolo.txt", "w", encoding="utf-8") as f:
        f.write(answers_only)
    
    print("Kész!")

if __name__ == "__main__":
    main()

