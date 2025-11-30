#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatikus ellenőrző script a generált szövegekhez.
Minden generálás után futtasd ezt a scriptet!
"""

import re
import sys

# TILOS szavak és kifejezések
TILOS_TARGYAK = ['tükör', 'kristály', 'üveg', 'gömb']
TILOS_ABSZTRAKT = ['mechanizmus', 'szerkezet', 'csatlakozóelem', 'komponens', 'elem', 'platform', 'terület', 'zóna']
TILOS_CSELEKMENYEK = [
    r'deszka.*pulzál',
    r'pálca.*pulzál',
    r'pecsét.*pulzál',
    r'tábla.*pulzál',
    r'fémlemezből.*golyó.*gurul',
    r'fémlemezből.*fénysugár',
    r'törött.*fémlemez',
    r'mérleg.*aljáról.*golyó',
]

def ellenoriz_szoveg(szoveg):
    """Ellenőrzi a szöveget a kritikus szabályok szerint."""
    hibak = []
    figyelmeztetesek = []
    
    # Ellenőrzés: TILOS tárgyak
    for targy in TILOS_TARGYAK:
        if targy.lower() in szoveg.lower():
            hibak.append(f"❌ TILOS tárgy található: '{targy}'")
    
    # Ellenőrzés: Absztrakt kifejezések
    for absztrakt in TILOS_ABSZTRAKT:
        if absztrakt.lower() in szoveg.lower():
            figyelmeztetesek.append(f"⚠️ Absztrakt kifejezés: '{absztrakt}' - ellenőrizd, hogy valós tárgyra cserélted-e!")
    
    # Ellenőrzés: Lehetetlen cselekmények
    for minta in TILOS_CSELEKMENYEK:
        if re.search(minta, szoveg, re.IGNORECASE):
            hibak.append(f"❌ Lehetetlen cselekmény: '{minta}'")
    
    # Ellenőrzés: Túl hosszú tárgy leírások (több mint 4 szó)
    mondatok = re.split(r'[.!?]\s+', szoveg)
    for mondat in mondatok:
        # Keresés: "X, Y, Z tárgy" vagy "X Y Z tárgy" minták
        hosszu_leiras = re.search(r'([a-záéíóöőúüű]+(?:\s+[a-záéíóöőúüű]+){3,})\s+(?:tárgy|látható|van)', mondat, re.IGNORECASE)
        if hosszu_leiras:
            figyelmeztetesek.append(f"⚠️ Túl hosszú leírás: '{hosszu_leiras.group(1)}' - maximum 2-3 szó legyen!")
    
    return hibak, figyelmeztetesek

def main():
    if len(sys.argv) < 2:
        print("Használat: python ellenoriz_generalas.py <fájl_útvonal>")
        sys.exit(1)
    
    fajl_utvonal = sys.argv[1]
    
    try:
        with open(fajl_utvonal, 'r', encoding='utf-8') as f:
            szoveg = f.read()
    except FileNotFoundError:
        print(f"❌ Fájl nem található: {fajl_utvonal}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hiba a fájl olvasásakor: {e}")
        sys.exit(1)
    
    hibak, figyelmeztetesek = ellenoriz_szoveg(szoveg)
    
    print("=" * 70)
    print("ELLENŐRZÉS EREDMÉNYE")
    print("=" * 70)
    
    if not hibak and not figyelmeztetesek:
        print("✅ Nincs hiba! A szöveg megfelel a kritikus szabályoknak.")
        return 0
    
    if hibak:
        print("\n❌ KRITIKUS HIBAK (JAVÍTSD KI!):")
        for hiba in hibak:
            print(f"  {hiba}")
    
    if figyelmeztetesek:
        print("\n⚠️ FIGYELMEZTETÉSEK (ELLENŐRIZD!):")
        for figyelmeztetes in figyelmeztetesek:
            print(f"  {figyelmeztetes}")
    
    print("\n" + "=" * 70)
    
    return 1 if hibak else 0

if __name__ == '__main__':
    sys.exit(main())

