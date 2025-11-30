#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Általános script dialógus fájlok szétválasztására kérdésekre és válaszokra.

Használat:
    python split_dialogus.py [fájl_elérési_út]
    
    Ha nincs megadva argumentum, akkor interaktívan kéri be a fájl elérési útját.
    Windows-on drag & drop-tel is használható (húzd rá a fájlt a scriptre).
"""

import os
import re
import sys
from pathlib import Path


def split_dialogus(source_file_path):
    """
    Szétválasztja a dialógus fájlt kérdésekre és válaszokra.
    
    Args:
        source_file_path: A forrás dialógus fájl elérési útja (str vagy Path)
    
    Returns:
        bool: True ha sikeres, False ha hiba történt
    """
    try:
        # Fájl elérési útjának ellenőrzése
        source_path = Path(source_file_path)
        
        if not source_path.exists():
            print(f"❌ Hiba: A fájl nem található: {source_file_path}")
            return False
        
        if not source_path.is_file():
            print(f"❌ Hiba: Ez nem egy fájl: {source_file_path}")
            return False
        
        # Forrás fájl nevének kinyerése (kiterjesztés nélkül)
        source_name = source_path.stem
        
        # Cél mappa meghatározása
        # A forrás fájl mappájában kell létrehozni a Dialogus mappát
        source_dir = source_path.parent
        dialogus_dir = source_dir / "Dialogus"
        
        # Dialogus mappa létrehozása, ha nem létezik
        dialogus_dir.mkdir(exist_ok=True)
        print(f"📁 Dialogus mappa: {dialogus_dir}")
        
        # Fájlok beolvasása
        print(f"📖 Fájl beolvasása: {source_path.name}")
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Kérdések és válaszok gyűjtése
        kerdesek = []
        valaszok = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Kérdező sorok kezelése (ezek valójában válaszok a fájlban)
            if line.startswith("Kérdező:"):
                # Eltávolítjuk a "Kérdező: " előtagot
                content = line.replace("Kérdező:", "").strip()
                # Eltávolítjuk a meglévő break tageket
                content = re.sub(r'<break\s+time="[^"]*"\s*/>', '', content).strip()
                if content:
                    valaszok.append(content)
            
            # Válaszoló sorok kezelése (ezek valójában kérdések a fájlban)
            elif line.startswith("Válaszoló:"):
                # Eltávolítjuk a "Válaszoló: " előtagot
                content = line.replace("Válaszoló:", "").strip()
                # Eltávolítjuk a meglévő break tageket
                content = re.sub(r'<break\s+time="[^"]*"\s*/>', '', content).strip()
                if content:
                    kerdesek.append(content)
        
        if not kerdesek and not valaszok:
            print("⚠️  Figyelmeztetés: Nem található 'Kérdező:' vagy 'Válaszoló:' címke a fájlban!")
            return False
        
        # Fájlok elnevezése a forrás fájl nevével
        kerdesek_file = dialogus_dir / f"{source_name}_kerdesek.txt"
        valaszok_file = dialogus_dir / f"{source_name}_valaszok.txt"
        
        # Kérdések fájl írása
        if kerdesek:
            with open(kerdesek_file, 'w', encoding='utf-8') as f:
                for kerdes in kerdesek:
                    f.write(f"{kerdes}\n")
                    f.write('<break time="5s"/>\n\n')
            print(f"✓ Kérdések fájl létrehozva: {kerdesek_file.name}")
            print(f"  - {len(kerdesek)} kérdés")
        
        # Válaszok fájl írása
        if valaszok:
            with open(valaszok_file, 'w', encoding='utf-8') as f:
                for valasz in valaszok:
                    f.write(f"{valasz}\n")
                    f.write('<break time="5s"/>\n\n')
            print(f"✓ Válaszok fájl létrehozva: {valaszok_file.name}")
            print(f"  - {len(valaszok)} válasz")
        
        # Forrás fájl áthelyezése a Dialogus mappába
        target_source_file = dialogus_dir / source_path.name
        if source_path != target_source_file:
            source_path.rename(target_source_file)
            print(f"✓ Forrás fájl áthelyezve: {target_source_file.name}")
        else:
            print(f"ℹ A forrás fájl már a cél mappában van")
        
        return True
        
    except Exception as e:
        print(f"❌ Hiba történt: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Főprogram"""
    print("=" * 60)
    print("Dialógus fájl szétválasztása")
    print("=" * 60)
    print()
    
    # Parancssori argumentumok ellenőrzése
    if len(sys.argv) > 1:
        # Fájl elérési útja megadva argumentumként
        source_file = sys.argv[1]
        # Windows drag & drop esetén idézőjelek eltávolítása
        source_file = source_file.strip('"')
    else:
        # Interaktív bevitel
        print("Kérlek add meg a dialógus fájl elérési útját:")
        print("(vagy húzd rá a fájlt a scriptre Windows-on)")
        print()
        source_file = input("Fájl elérési útja: ").strip().strip('"')
    
    if not source_file:
        print("❌ Hiba: Nincs megadva fájl elérési út!")
        print()
        print("Használat:")
        print("  python split_dialogus.py [fájl_elérési_út]")
        print()
        print("Vagy húzd rá a fájlt a scriptre Windows-on.")
        sys.exit(1)
    
    print(f"📄 Forrás fájl: {source_file}")
    print()
    
    # Dialógus feldolgozása
    success = split_dialogus(source_file)
    
    print()
    print("=" * 60)
    if success:
        print("✅ Kész!")
    else:
        print("❌ A feldolgozás sikertelen volt!")
        sys.exit(1)


if __name__ == "__main__":
    main()

