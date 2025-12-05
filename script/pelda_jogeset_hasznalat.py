#!/usr/bin/env python3
"""
Példa használat a jogeset generátorhoz

Ez a szkript bemutatja, hogyan lehet programozottan használni
a jogeset generátort Python kódból.
"""

from jogeset_generator import JogszabalyElemzo, LLMGenerator, Jogeset
from pathlib import Path


def pelda_1_egyszeru_hasznalat():
    """Egyszerű példa: közvetlen jogszabály szövegből"""
    print("="*70)
    print("PÉLDA 1: Egyszerű használat")
    print("="*70)
    
    jogszabaly_szoveg = """
    Ptk. 6:519. § [A kártérítési kötelezettség]
    
    (1) A károkozó köteles megtéríteni a kárt, ha nem bizonyítja, 
    hogy a kár nem az ő hibájából következett be.
    """
    
    # Jogszabály elemzése
    elemzo = JogszabalyElemzo(jogszabaly_szoveg)
    struktura = elemzo.strukturalt_leiras()
    
    print(f"\nElemzett jogszabály:")
    print(f"  Paragrafus: {struktura['paragrafus']}")
    print(f"  Kulcsszavak: {', '.join(struktura['kulcsszavak'])}")
    print(f"  Joghatások: {', '.join(struktura['joghatasok'])}")
    
    # Jogeset generálása (template mód - LLM nélkül)
    print("\nJogeset generálása...")
    generator = LLMGenerator(provider="template")
    jogeset = generator.generate_jogeset(elemzo, komplexitas="közepes", kategoria="kártérítés")
    
    print(f"\nGenerált jogeset:")
    print(f"  Cím: {jogeset.cim}")
    print(f"  Tényállás: {jogeset.tenyek[:200]}...")
    print(f"  Kategória: {jogeset.kategoria}")


def pelda_2_fajlbol_olvasas():
    """Példa: fájlból olvasás"""
    print("\n" + "="*70)
    print("PÉLDA 2: Fájlból olvasás")
    print("="*70)
    
    # Keressük meg a jogszabály fájlt
    projekt_root = Path(__file__).parent.parent
    jogszabaly_fajl = projekt_root / "forrasok" / "2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt"
    
    if not jogszabaly_fajl.exists():
        print(f"\nA fájl nem található: {jogszabaly_fajl}")
        print("Ez egy példa, ami bemutatja, hogyan lehet fájlból olvasni.")
        return
    
    # Olvassuk be a fájlt
    jogszabaly_szoveg = jogszabaly_fajl.read_text(encoding='utf-8')
    
    # Keressük meg egy konkrét paragrafust (pl. 6:519)
    import re
    pattern = r'6:519\.?\s*§.*?(?=\d+:\d+\.?\s*§|$)'
    match = re.search(pattern, jogszabaly_szoveg, re.DOTALL | re.IGNORECASE)
    
    if match:
        paragrafus_szoveg = match.group(0)
        print(f"\nTalált paragrafus (első 200 karakter):")
        print(paragrafus_szoveg[:200] + "...")
        
        # Elemzés és generálás
        elemzo = JogszabalyElemzo(paragrafus_szoveg)
        generator = LLMGenerator(provider="template")
        jogeset = generator.generate_jogeset(elemzo, komplexitas="komplex", kategoria="kártérítés")
        
        print(f"\nGenerált jogeset címe: {jogeset.cim}")
    else:
        print("\nA paragrafus nem található a fájlban.")


def pelda_3_tobb_jogeset():
    """Példa: több jogeset generálása"""
    print("\n" + "="*70)
    print("PÉLDA 3: Több jogeset generálása")
    print("="*70)
    
    jogszabalyok = [
        {
            "szoveg": "Ptk. 6:1. § A szerződés a felek megállapodása.",
            "komplexitas": "egyszerű",
            "kategoria": "szerződés"
        },
        {
            "szoveg": "Ptk. 2:1. § (1) Minden ember jogképes: jogai és kötelezettségei lehetnek.",
            "komplexitas": "közepes",
            "kategoria": "jogképesség"
        },
        {
            "szoveg": "Ptk. 5:38. § Az ingatlan tulajdonjogának átruházásánál az ingatlan-nyilvántartási bejegyzés konstitutív hatályú.",
            "komplexitas": "komplex",
            "kategoria": "tulajdonjog"
        }
    ]
    
    generator = LLMGenerator(provider="template")
    
    for i, js in enumerate(jogszabalyok, 1):
        print(f"\n{i}. Jogszabály: {js['kategoria']}")
        elemzo = JogszabalyElemzo(js['szoveg'])
        jogeset = generator.generate_jogeset(
            elemzo, 
            komplexitas=js['komplexitas'],
            kategoria=js['kategoria']
        )
        print(f"   Generált cím: {jogeset.cim}")


def pelda_4_json_export():
    """Példa: JSON exportálás"""
    print("\n" + "="*70)
    print("PÉLDA 4: JSON exportálás")
    print("="*70)
    
    import json
    from dataclasses import asdict
    
    jogszabaly_szoveg = "Ptk. 6:519. § A károkozó köteles megtéríteni a kárt."
    
    elemzo = JogszabalyElemzo(jogszabaly_szoveg)
    generator = LLMGenerator(provider="template")
    jogeset = generator.generate_jogeset(elemzo, komplexitas="közepes", kategoria="kártérítés")
    
    # JSON formátumba konvertálás
    jogeset_dict = asdict(jogeset)
    
    # Exportálás
    kimenet_fajl = Path(__file__).parent / "pelda_jogeset_output.json"
    with open(kimenet_fajl, 'w', encoding='utf-8') as f:
        json.dump(jogeset_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Jogeset exportálva: {kimenet_fajl}")
    print(f"\nJSON tartalom (első 500 karakter):")
    json_str = json.dumps(jogeset_dict, ensure_ascii=False, indent=2)
    print(json_str[:500] + "...")


def main():
    """Fő függvény - futtatja az összes példát"""
    print("\n" + "="*70)
    print("JOGESET GENERÁTOR - PÉLDA HASZNÁLAT")
    print("="*70)
    
    try:
        pelda_1_egyszeru_hasznalat()
        pelda_2_fajlbol_olvasas()
        pelda_3_tobb_jogeset()
        pelda_4_json_export()
        
        print("\n" + "="*70)
        print("MINDEN PÉLDA SIKERESEN LE FUTOTT")
        print("="*70)
        print("\nTovábbi információkért lásd: script/README_JOGESET_GENERATOR.md")
        
    except Exception as e:
        print(f"\nHiba történt: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

