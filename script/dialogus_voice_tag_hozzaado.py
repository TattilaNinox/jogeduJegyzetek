#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialógus fájl átalakító script
A MENTOR és TANULÓ címkéket voice tag-ek közé helyezi
"""

import os
import sys

# ============================================================================
# BEÁLLÍTÁSOK - ITT MÓDOSÍTSD A VOICE TAG-EKET
# ============================================================================

# Mentor voice tag-ek
MENTOR_VOICE_START = '<voice voice-id="3af57f25-0c84-4202-9381-47f013458d29" speaker-id="c5680bed-a453-402e-a95b-ebef56707136" language="hu" seed="f07dddb4-6af4-4132-8379-50ee5e1c80a7">'
MENTOR_VOICE_END = '</voice>'

# Tanuló voice tag-ek
TANULO_VOICE_START = '<voice voice-id="f99a416d-6943-4541-90c6-8ea0b282e39a" speaker-id="8a67d393-1ff8-41eb-a7d6-e7641c8cf9b3" language="hu" seed="8023d092-d0b2-4b00-8034-5102eec293d9">'
TANULO_VOICE_END = '</voice>'

# ============================================================================
# FŐPROGRAM
# ============================================================================

def atalakit_dialogus_fajl(bemeneti_fajl, kimeneti_fajl=None):
    """
    Átalakítja a dialógus fájlt: eltávolítja a MENTOR: és TANULÓ: címkéket,
    és a megfelelő voice tag-ek közé helyezi a szövegeket.
    
    Args:
        bemeneti_fajl: A bemeneti fájl elérési útja
        kimeneti_fajl: A kimeneti fájl elérési útja (opcionális, ha None, akkor felülírja a bemeneti fájlt)
    """
    
    # Ha nincs kimeneti fájl megadva, akkor felülírjuk a bemeneti fájlt
    if kimeneti_fajl is None:
        kimeneti_fajl = bemeneti_fajl
    
    # Ellenőrizzük, hogy létezik-e a bemeneti fájl
    if not os.path.exists(bemeneti_fajl):
        print(f"Hiba: A fájl nem található: {bemeneti_fajl}")
        return False
    
    try:
        # Beolvassuk a fájlt
        with open(bemeneti_fajl, 'r', encoding='utf-8') as f:
            sorok = f.readlines()
        
        # Feldolgozzuk a sorokat
        uj_sorok = []
        
        for sor in sorok:
            sor = sor.rstrip('\n\r')  # Eltávolítjuk a sorvégeket
            
            if sor.startswith('MENTOR: '):
                # Eltávolítjuk a "MENTOR: " részt
                szoveg = sor[8:]  # "MENTOR: " hossza 8 karakter
                uj_sorok.append(MENTOR_VOICE_START)
                uj_sorok.append(szoveg)
                uj_sorok.append(MENTOR_VOICE_END)
            elif sor.startswith('TANULÓ: '):
                # Eltávolítjuk a "TANULÓ: " részt
                szoveg = sor[8:]  # "TANULÓ: " hossza 8 karakter
                uj_sorok.append(TANULO_VOICE_START)
                uj_sorok.append(szoveg)
                uj_sorok.append(TANULO_VOICE_END)
            else:
                # Üres sorok és egyéb sorok megtartása
                uj_sorok.append(sor)
        
        # Kiírjuk az új fájlt
        with open(kimeneti_fajl, 'w', encoding='utf-8') as f:
            f.write('\n'.join(uj_sorok))
        
        print(f"✓ Sikeresen átalakítva: {bemeneti_fajl}")
        if kimeneti_fajl != bemeneti_fajl:
            print(f"✓ Kimeneti fájl: {kimeneti_fajl}")
        return True
        
    except Exception as e:
        print(f"Hiba történt: {e}")
        return False


def main():
    """Főprogram"""
    
    print("=" * 60)
    print("Dialógus fájl átalakító")
    print("=" * 60)
    print()
    
    # Ellenőrizzük a parancssori argumentumokat
    if len(sys.argv) < 2:
        print("Használat:")
        print(f"  python {sys.argv[0]} <bemeneti_fajl> [kimeneti_fajl]")
        print()
        print("Példa:")
        print(f"  python {sys.argv[0]} dialogus.txt")
        print(f"  python {sys.argv[0]} dialogus.txt dialogus_atalakított.txt")
        print()
        print("Megjegyzés: Ha nem adsz meg kimeneti fájlt, akkor a bemeneti fájl")
        print("            felül lesz írva az átalakított verzióval.")
        sys.exit(1)
    
    bemeneti_fajl = sys.argv[1]
    kimeneti_fajl = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Átalakítjuk a fájlt
    sikeres = atalakit_dialogus_fajl(bemeneti_fajl, kimeneti_fajl)
    
    if sikeres:
        print()
        print("Kész!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()


