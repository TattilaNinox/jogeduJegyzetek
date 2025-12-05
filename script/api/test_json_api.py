#!/usr/bin/env python3
"""
Teszt script a JSON alapú API-hoz
"""

import requests
import json
from jogeset_db import JogesetDatabase
from pathlib import Path

API_URL = "http://localhost:5000"
script_dir = Path(__file__).parent
DB_PATH = script_dir / "jogesetek_db"

def test_database_direct():
    """Közvetlen adatbázis tesztelése (API nélkül)"""
    print("="*60)
    print("KÖZVETLEN ADATBÁZIS TESZTELÉS")
    print("="*60)
    print()
    
    db = JogesetDatabase(DB_PATH)
    
    # Paragrafusok listázása
    print("1. Elérhető paragrafusok:")
    paragrafusok = db.list_paragrafusok()
    if paragrafusok:
        for p in paragrafusok:
            print(f"   - {p}")
    else:
        print("   ⚠ Nincs még paragrafus az adatbázisban!")
        print("   Futtasd le először: python script/api/init_database.py")
        return
    print()
    
    # Véletlenszerű jogeset választása
    print("2. Véletlenszerű jogeset választása (6:519):")
    for i in range(3):
        jogeset = db.get_random_jogeset("6:519")
        if jogeset:
            print(f"\n   Variáció {i+1}:")
            print(f"   Cím: {jogeset['cim']}")
            print(f"   Tényállás (első 100 karakter): {jogeset['tenyek'][:100]}...")
        else:
            print(f"   ⚠ Nincs jogeset a 6:519 paragrafushoz")
    print()
    
    # Összes jogeset lekérése
    print("3. Összes jogeset lekérése (6:519):")
    all_jogesetek = db.get_all_jogesetek("6:519")
    if all_jogesetek:
        print(f"   Összesen {len(all_jogesetek)} jogeset:")
        for j in all_jogesetek:
            print(f"   - [{j['id']}] {j['cim']} ({j.get('komplexitas', 'ismeretlen')})")
    else:
        print("   ⚠ Nincs jogeset")
    print()


def test_api():
    """API tesztelése"""
    print("="*60)
    print("API TESZTELÉS")
    print("="*60)
    print()
    
    try:
        # Health check
        print("1. Health check:")
        response = requests.get(f"{API_URL}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print()
        
        # Paragrafusok listázása
        print("2. Paragrafusok listázása:")
        response = requests.get(f"{API_URL}/api/paragrafusok")
        if response.status_code == 200:
            data = response.json()
            print(f"   Összesen {data['count']} paragrafus:")
            for p in data['paragrafusok']:
                print(f"   - {p}")
        print()
        
        # Jogeset generálás (többször, hogy lássuk a változatosságot)
        print("3. Jogeset generálás (3x ugyanarra a paragrafusra):")
        for i in range(3):
            print(f"\n   Generálás {i+1}/3:")
            response = requests.post(
                f"{API_URL}/api/generate-jogeset",
                json={
                    "paragrafus": "6:519",
                    "komplexitas": "közepes"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    jogeset = data["jogeset"]
                    print(f"   ✓ Cím: {jogeset['cim']}")
                    print(f"   Tényállás kezdete: {jogeset['tenyek'][:80]}...")
                else:
                    print(f"   ❌ Hiba: {data.get('error')}")
            else:
                print(f"   ❌ HTTP hiba: {response.status_code}")
                print(f"   Response: {response.text}")
        print()
        
        # Összes jogeset lekérése
        print("4. Összes jogeset lekérése (6:519):")
        response = requests.get(f"{API_URL}/api/jogesetek/6:519")
        if response.status_code == 200:
            data = response.json()
            print(f"   Összesen {data['count']} jogeset:")
            for j in data['jogesetek']:
                print(f"   - [{j['id']}] {j['cim']} ({j.get('komplexitas', 'ismeretlen')})")
        print()
        
    except requests.exceptions.ConnectionError:
        print("❌ Hiba: Nem lehet csatlakozni az API-hoz!")
        print("   Győződj meg róla, hogy az API fut: python script/api/jogeset_api_json.py")
    except Exception as e:
        print(f"❌ Váratlan hiba: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_workflow():
    """Bemutatja a munkafolyamatot"""
    print("="*60)
    print("MŰKÖDÉS BEMUTATÁSA")
    print("="*60)
    print()
    
    print("1. ADATBÁZIS STRUKTÚRA:")
    print("   script/api/jogesetek_db/")
    print("   ├── 6_519.json  (6:519. § jogesetek)")
    print("   ├── 4_15.json   (4:15. § jogesetek)")
    print("   └── ...")
    print()
    
    print("2. MŰKÖDÉS:")
    print("   Flutter App → POST /api/generate-jogeset")
    print("   ↓")
    print("   Flask API → jogeset_db.py")
    print("   ↓")
    print("   JSON fájl betöltése (pl. 6_519.json)")
    print("   ↓")
    print("   Véletlenszerű választás a jogesetek közül")
    print("   ↓")
    print("   JSON válasz → Flutter App")
    print()
    
    print("3. VÁLTOZATOSSÁG:")
    print("   - Minden kérésnél véletlenszerűen választ")
    print("   - Ugyanarra a paragrafusra több különböző jogeset")
    print("   - Komplexitás szerint szűrhető")
    print()
    
    print("4. ELŐNYÖK:")
    print("   ✅ Nincs szükség API kulcsokra")
    print("   ✅ Gyors válaszidő (nincs LLM hívás)")
    print("   ✅ Költségmentes")
    print("   ✅ Flutter app közvetlenül is használhatja a JSON fájlokat")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("JSON ALAPÚ JOGESET API TESZTELÉS")
    print("="*60)
    print()
    
    # Működés bemutatása
    demonstrate_workflow()
    
    # Közvetlen adatbázis teszt
    test_database_direct()
    
    # API teszt (ha fut)
    user_input = input("Szeretnéd tesztelni az API-t is? (i/n): ")
    if user_input.lower() == 'i':
        test_api()
    
    print("="*60)
    print("TESZTELÉS BEFEJEZVE")
    print("="*60)

