#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanulókártya-generátor script LLM API-val
Használat: python3 kartya_generator.py --konyv 2 --tol 8 --ig 15 [opcionális paraméterek]
"""

import re
import os
import sys
import json
import argparse
from typing import List, Dict, Optional

# Meglévő függvények importálása
from feldolgozas import torveny_fajl_beolvasas, torvenyi_szoveg_kinyerese


def parse_arguments():
    """Parancssori argumentumok feldolgozása"""
    parser = argparse.ArgumentParser(
        description='Tanulókártya-generátor törvényi szövegből LLM API-val',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Példa használat:
  python3 kartya_generator.py --konyv 2 --tol 8 --ig 15
  python3 kartya_generator.py --konyv 4 --tol 21 --ig 25 --kartyak 3 --api openai --model gpt-4
  python3 kartya_generator.py --konyv 2 --tol 8 --ig 15 --output-dir "./kimenet"
        """
    )
    
    # Kötelező paraméterek
    parser.add_argument('--konyv', type=int, required=True,
                        help='Könyv száma (pl. 2, 4)')
    parser.add_argument('--tol', type=int, required=True,
                        help='Kezdő paragrafus száma (pl. 8)')
    parser.add_argument('--ig', type=int, required=True,
                        help='Végző paragrafus száma (pl. 15)')
    
    # Opcionális paraméterek
    parser.add_argument('--kartyak', type=int, default=2,
                        choices=range(1, 6),
                        help='Kártyák száma paragrafusonként (1-5, alapértelmezett: 2)')
    parser.add_argument('--api', type=str, default='openai',
                        choices=['openai', 'anthropic'],
                        help='API provider (alapértelmezett: openai)')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo',
                        help='Model neve (alapértelmezett: gpt-3.5-turbo)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Kimeneti mappa (alapértelmezett: aktuális mappa)')
    
    return parser.parse_args()


def validate_arguments(args):
    """Argumentumok validálása"""
    if args.tol > args.ig:
        print(f"Hiba: A kezdő paragrafus ({args.tol}) nem lehet nagyobb, mint a végző ({args.ig})")
        sys.exit(1)
    
    if args.konyv < 1 or args.tol < 1 or args.ig < 1:
        print(f"Hiba: A könyv és paragrafus számoknak pozitív egész számoknak kell lenniük")
        sys.exit(1)


def check_api_key(api_provider: str) -> bool:
    """API kulcs ellenőrzése"""
    if api_provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Hiba: OPENAI_API_KEY environment változó nincs beállítva!")
            print("Használat: export OPENAI_API_KEY='sk-...'")
            return False
        return True
    elif api_provider == 'anthropic':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Hiba: ANTHROPIC_API_KEY environment változó nincs beállítva!")
            print("Használat: export ANTHROPIC_API_KEY='sk-ant-...'")
            return False
        return True
    return False


def create_prompt(paragrafus_szoveg: str, kartyak_szama: int) -> str:
    """Prompt létrehozása LLM számára"""
    prompt = f"""Egyetemi jogász professzori hozzáértéssel készíts {kartyak_szama} db egyetemi szintű tanulókártyát a következő törvényi szövegrészlet alapján:

{paragrafus_szoveg}

Minden kártyához:
1. Egyetemi szintű, részletes kérdés (professzori minőségű, dogmatikailag pontos)
2. Professzori minőségű részletes válasz (tartalmas, jogszabály-hivatkozásokkal)
3. Kiegészítő magyarázat/jogdogmatikai háttér (további kontextus, jogelméleti összefüggések)

Válaszolj CSAK JSON formátumban, az alábbi struktúrában:
{{
  "kartyak": [
    {{
      "kerdes": "Teljes kérdés szövege",
      "valasz": "Teljes válasz szövege",
      "magyarazat": "Teljes magyarázat szövege"
    }},
    ...
  ]
}}

Fontos követelmények:
- Minden kérdés egyetemi szintű legyen, ne csak egyszerű definíció
- A válaszok részletesek, professzori minőségűek legyenek
- A magyarázatok jogdogmatikai hátteret, jogelméleti összefüggéseket tartalmazzanak
- Ne használj rövidítéseket (pl. Ptk. → Polgári Törvénykönyv)
- Ne használj speciális karaktereket (zárójelek, nyilak)
- A válasz csak JSON formátum legyen, semmi más szöveg"""

    return prompt


def call_openai_api(prompt: str, model: str, max_retries: int = 3) -> Optional[Dict]:
    """OpenAI API hívás retry logikával"""
    import time
    
    try:
        import openai
    except ImportError:
        print("Hiba: Az 'openai' package nincs telepítve!")
        print("Telepítés: pip install openai")
        return None
    
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Te egy egyetemi jogász professzor vagy, aki egyetemi szintű tanulókártyákat készít. Válaszolj CSAK JSON formátumban."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            return json.loads(response_text)
            
        except openai.RateLimitError:
            wait_time = (attempt + 1) * 2
            print(f"  Rate limit, várakozás {wait_time} másodperc...")
            time.sleep(wait_time)
        except json.JSONDecodeError as e:
            print(f"  JSON dekódolási hiba: {e}")
            if attempt < max_retries - 1:
                continue
            return None
        except Exception as e:
            print(f"  Hiba az OpenAI API híváskor: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    
    return None


def call_anthropic_api(prompt: str, model: str, max_retries: int = 3) -> Optional[Dict]:
    """Anthropic API hívás retry logikával"""
    import time
    
    try:
        import anthropic
    except ImportError:
        print("Hiba: Az 'anthropic' package nincs telepítve!")
        print("Telepítés: pip install anthropic")
        return None
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=4000,
                system="Te egy egyetemi jogász professzor vagy, aki egyetemi szintű tanulókártyákat készít. Válaszolj CSAK JSON formátumban.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # JSON kinyerése a válaszból (ha van körülötte szöveg)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response_text)
                
        except anthropic.RateLimitError:
            wait_time = (attempt + 1) * 2
            print(f"  Rate limit, várakozás {wait_time} másodperc...")
            time.sleep(wait_time)
        except json.JSONDecodeError as e:
            print(f"  JSON dekódolási hiba: {e}")
            if attempt < max_retries - 1:
                continue
            return None
        except Exception as e:
            print(f"  Hiba az Anthropic API híváskor: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    
    return None


def generate_cards_for_paragraph(paragrafus_szoveg: str, kartyak_szama: int, 
                                  api_provider: str, model: str) -> List[Dict]:
    """Kártyák generálása egy paragrafushoz"""
    if not paragrafus_szoveg or not paragrafus_szoveg.strip():
        return []
    
    prompt = create_prompt(paragrafus_szoveg, kartyak_szama)
    
    # API hívás
    if api_provider == 'openai':
        response = call_openai_api(prompt, model)
    elif api_provider == 'anthropic':
        response = call_anthropic_api(prompt, model)
    else:
        print(f"Unknown API provider: {api_provider}")
        return []
    
    if not response or 'kartyak' not in response:
        print("Figyelem: Az API nem adott vissza érvényes választ")
        return []
    
    return response.get('kartyak', [])


def save_output(kerdesek: List[str], valaszok: List[str], magyarazatok: List[str], 
                output_dir: str):
    """Kimenet mentése fájlokba"""
    os.makedirs(output_dir, exist_ok=True)
    
    # kerdesek.txt
    with open(os.path.join(output_dir, 'kerdesek.txt'), 'w', encoding='utf-8') as f:
        f.write("Professzori minőségemben összeállítottam az egyetemi szintű, {} tételből álló tanulókártya-csomagot a kért témakörökből. Az alábbiakban a kártyák előlapjai, a kérdések találhatók.\n\n".format(len(kerdesek)))
        for i, kerdes in enumerate(kerdesek, 1):
            f.write(f"{i}. {kerdes}\n")
    
    # valaszok.txt
    with open(os.path.join(output_dir, 'valaszok.txt'), 'w', encoding='utf-8') as f:
        for i, valasz in enumerate(valaszok, 1):
            f.write(f"{i}. {valasz}\n")
    
    # magyarazatok.txt
    with open(os.path.join(output_dir, 'magyarazatok.txt'), 'w', encoding='utf-8') as f:
        for i, magyarazat in enumerate(magyarazatok, 1):
            f.write(f"{i}. {magyarazat}\n")
    
    print(f"\nKimenet mentve a '{output_dir}' mappába:")
    print(f"  - kerdesek.txt ({len(kerdesek)} db)")
    print(f"  - valaszok.txt ({len(valaszok)} db)")
    print(f"  - magyarazatok.txt ({len(magyarazatok)} db)")


def main():
    """Fő függvény"""
    args = parse_arguments()
    validate_arguments(args)
    
    if not check_api_key(args.api):
        sys.exit(1)
    
    print(f"Tanulókártya-generátor indítása...")
    print(f"Könyv: {args.konyv}, Paragrafusok: {args.tol}-{args.ig}")
    print(f"Kártyák paragrafusonként: {args.kartyak}")
    print(f"API: {args.api}, Model: {args.model}")
    print()
    
    # Törvényi fájl beolvasása
    script_mappa = os.path.dirname(os.path.abspath(__file__))
    torveny_fajl_utvonal = os.path.join(script_mappa, '..', 'Források', '2013. évi V. törvény a Polgári Törvénykönyvről.txt')
    torveny_fajl_utvonal = os.path.normpath(torveny_fajl_utvonal)
    
    print(f"Törvényi fájl beolvasása: {torveny_fajl_utvonal}")
    torveny_index = torveny_fajl_beolvasas(torveny_fajl_utvonal)
    
    if not torveny_index:
        print("Hiba: Nem sikerült beolvasni a törvényi fájlt!")
        sys.exit(1)
    
    # Kártyák generálása
    kerdesek = []
    valaszok = []
    magyarazatok = []
    
    print(f"\nKártyák generálása {args.konyv}. könyv {args.tol}-{args.ig}. paragrafusaihoz...")
    
    for paragrafus_num in range(args.tol, args.ig + 1):
        kulcs = f"{args.konyv}:{paragrafus_num}"
        
        if kulcs not in torveny_index:
            print(f"Figyelem: {kulcs}. § nem található a törvényi fájlban, kihagyva")
            continue
        
        # Paragrafus szöveg kinyerése (összes bekezdés)
        paragrafus_data = torveny_index[kulcs]
        paragrafus_szoveg = ' '.join(paragrafus_data.values()).strip()
        
        if not paragrafus_szoveg:
            print(f"Figyelem: {kulcs}. § üres, kihagyva")
            continue
        
        print(f"  {kulcs}. § feldolgozása...", end=' ', flush=True)
        
        # Kártyák generálása
        kartyak = generate_cards_for_paragraph(
            paragrafus_szoveg, 
            args.kartyak, 
            args.api, 
            args.model
        )
        
        if not kartyak:
            print("(nem sikerült kártyákat generálni)")
            continue
        
        # Kártyák hozzáadása
        for kartya in kartyak:
            if 'kerdes' in kartya:
                kerdesek.append(kartya['kerdes'])
            if 'valasz' in kartya:
                valaszok.append(kartya['valasz'])
            if 'magyarazat' in kartya:
                magyarazatok.append(kartya['magyarazat'])
        
        print(f"✓ ({len(kartyak)} db kártya)")
    
    # Kimenet mentése
    if kerdesek:
        save_output(kerdesek, valaszok, magyarazatok, args.output_dir)
        print(f"\nÖsszesen {len(kerdesek)} db tanulókártya generálva!")
    else:
        print("\nHiba: Nem sikerült kártyákat generálni!")


if __name__ == '__main__':
    main()

