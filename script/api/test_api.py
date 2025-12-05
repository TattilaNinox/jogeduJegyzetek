#!/usr/bin/env python3
"""
Teszt script az API-hoz
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Health check teszt"""
    print("🔍 Health check tesztelése...")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_paragrafus_info():
    """Paragrafus info teszt"""
    print("🔍 Paragrafus info tesztelése...")
    response = requests.get(f"{API_URL}/api/paragrafus-info/6:519")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_generate_jogeset():
    """Jogeset generálás teszt"""
    print("🔍 Jogeset generálás tesztelése...")
    
    data = {
        "paragrafus": "6:519",
        "kategoria": "kártérítés",
        "komplexitas": "közepes",
        "provider": "openai"  # vagy "anthropic", "gemini"
    }
    
    print(f"Request: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("\n⏳ Generálás folyamatban... (ez eltarthat egy ideig)")
    
    response = requests.post(
        f"{API_URL}/api/generate-jogeset",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            jogeset = result["jogeset"]
            print("\n✅ Sikeres generálás!")
            print(f"\nCím: {jogeset['cim']}")
            print(f"\nTényállás (első 200 karakter):")
            print(jogeset['tenyek'][:200] + "...")
            print(f"\nKategória: {jogeset['kategoria']}")
            print(f"Komplexitás: {jogeset['komplexitas']}")
        else:
            print(f"❌ Hiba: {result.get('error')}")
    else:
        print(f"❌ HTTP hiba: {response.status_code}")
        print(f"Response: {response.text}")
    print()

def test_multiple_generations():
    """Többszöri generálás tesztelése (változatosság ellenőrzése)"""
    print("🔍 Többszöri generálás tesztelése (változatosság ellenőrzése)...")
    
    data = {
        "paragrafus": "6:519",
        "kategoria": "kártérítés",
        "komplexitas": "közepes",
        "provider": "openai"
    }
    
    print("⏳ 3 jogeset generálása ugyanarra a paragrafusra...\n")
    
    for i in range(3):
        print(f"--- Generálás {i+1}/3 ---")
        response = requests.post(
            f"{API_URL}/api/generate-jogeset",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                jogeset = result["jogeset"]
                print(f"Cím: {jogeset['cim']}")
                print(f"Tényállás kezdete: {jogeset['tenyek'][:100]}...")
            else:
                print(f"Hiba: {result.get('error')}")
        else:
            print(f"HTTP hiba: {response.status_code}")
        print()

if __name__ == "__main__":
    print("="*60)
    print("JOGESET GENERÁTOR API TESZTELÉS")
    print("="*60)
    print()
    
    try:
        # Health check
        test_health()
        
        # Paragrafus info
        test_paragrafus_info()
        
        # Jogeset generálás (csak akkor, ha van API kulcs)
        import os
        if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY"):
            test_generate_jogeset()
            
            # Többszöri generálás teszt
            user_input = input("Szeretnél több generálást tesztelni? (i/n): ")
            if user_input.lower() == 'i':
                test_multiple_generations()
        else:
            print("⚠️  Nincs API kulcs beállítva, ezért a generálás teszt kihagyva.")
            print("   Állítsd be az OPENAI_API_KEY, ANTHROPIC_API_KEY vagy GEMINI_API_KEY környezeti változót.")
        
        print("="*60)
        print("TESZTELÉS BEFEJEZVE")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Hiba: Nem lehet csatlakozni az API-hoz!")
        print("   Győződj meg róla, hogy az API fut: python script/api/jogeset_api.py")
    except Exception as e:
        print(f"❌ Váratlan hiba: {e}")
        import traceback
        traceback.print_exc()

