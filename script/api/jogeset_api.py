#!/usr/bin/env python3
"""
Jogeset Generátor REST API
Flutter webalkalmazáshoz REST API, amely LLM-mel generál egyedi jogeseteket.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import os
import random
from datetime import datetime

# Hozzáadjuk a szülő mappát a path-hoz, hogy importálni tudjuk a jogeset_generator modult
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from jogeset_generator import JogszabalyElemzo, LLMGenerator, Jogeset

app = Flask(__name__)
CORS(app)  # CORS engedélyezése Flutter webapp számára

# Projekt root elérési út
PROJECT_ROOT = Path(__file__).parent.parent.parent
JOGSZABALY_FAJL = PROJECT_ROOT / "forrasok" / "2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt"


def load_jogszabaly_fajl() -> str:
    """Betölti a jogszabály fájlt"""
    if not JOGSZABALY_FAJL.exists():
        raise FileNotFoundError(f"A jogszabály fájl nem található: {JOGSZABALY_FAJL}")
    return JOGSZABALY_FAJL.read_text(encoding='utf-8')


def get_paragrafus_szoveg(paragrafus_szam: str, teljes_fajl: str) -> str:
    """Kinyeri a paragrafus szövegét a fájlból"""
    paragrafus_szoveg = JogszabalyElemzo.kinyer_paragrafus_fajlbol(teljes_fajl, paragrafus_szam)
    if not paragrafus_szoveg:
        raise ValueError(f"A paragrafus ({paragrafus_szam}) nem található a fájlban")
    return paragrafus_szoveg


def add_variation_to_prompt(base_prompt: str) -> str:
    """Változatosságot ad a promptnak, hogy minden alkalommal más jogeset generálódjon"""
    variations = [
        "\n\nFONTOS: Készíts egy teljesen ÚJ, egyedi jogesetet, amely eltér az előzőektől. Használj más személyeket, dátumokat, helyszíneket és körülményeket.",
        "\n\nFONTOS: Ez egy új generálás. Készíts egy teljesen más szituációt, más szereplőkkel és más tényekkel.",
        "\n\nFONTOS: Generálj egy egyedi jogesetet, amely kreatív és eltér a korábbi példáktól.",
    ]
    
    # Véletlenszerű variáció hozzáadása
    variation = random.choice(variations)
    
    # Timestamp alapú variáció is
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    variation += f"\n\nGenerálási időpont: {timestamp}"
    
    return base_prompt + variation


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Jogeset Generátor API működik"
    })


@app.route('/api/generate-jogeset', methods=['POST'])
def generate_jogeset():
    """Jogeset generálása API endpoint"""
    try:
        # Request adatok ellenőrzése
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Nincs JSON adat a kérésben"
            }), 400
        
        paragrafus = data.get('paragrafus')
        if not paragrafus:
            return jsonify({
                "success": False,
                "error": "A 'paragrafus' mező kötelező"
            }), 400
        
        kategoria = data.get('kategoria')
        komplexitas = data.get('komplexitas', 'közepes')
        provider = data.get('provider', 'openai')
        
        # Jogszabály fájl betöltése
        try:
            teljes_fajl = load_jogszabaly_fajl()
        except FileNotFoundError as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
        
        # Paragrafus kinyerése
        try:
            paragrafus_szoveg = get_paragrafus_szoveg(paragrafus, teljes_fajl)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
        
        # Jogszabály elemzése
        elemzo = JogszabalyElemzo(paragrafus_szoveg)
        
        # LLM generátor inicializálása
        try:
            generator = LLMGenerator(provider=provider)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"LLM provider hiba: {str(e)}"
            }), 400
        
        # Prompt variáció hozzáadása a változatossághoz
        original_create_prompt = generator._create_prompt
        def create_prompt_with_variation(elemzo, komplexitas, kategoria):
            base_prompt = original_create_prompt(elemzo, komplexitas, kategoria)
            return add_variation_to_prompt(base_prompt)
        
        generator._create_prompt = create_prompt_with_variation
        
        # Jogeset generálása
        jogeset = generator.generate_jogeset(elemzo, komplexitas, kategoria)
        
        # Response JSON formátumban
        return jsonify({
            "success": True,
            "jogeset": {
                "cim": jogeset.cim,
                "tenyek": jogeset.tenyek,
                "kerdes": jogeset.kerdes,
                "alkalmazando_jogszabaly": jogeset.alkalmazando_jogszabaly,
                "megoldas": jogeset.megoldas,
                "komplexitas": jogeset.komplexitas,
                "kategoria": jogeset.kategoria
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Váratlan hiba: {str(e)}"
        }), 500


@app.route('/api/paragrafus-info/<paragrafus>', methods=['GET'])
def get_paragrafus_info(paragrafus):
    """Paragrafus információk lekérése"""
    try:
        teljes_fajl = load_jogszabaly_fajl()
        paragrafus_szoveg = get_paragrafus_szoveg(paragrafus, teljes_fajl)
        
        elemzo = JogszabalyElemzo(paragrafus_szoveg)
        struktura = elemzo.strukturalt_leiras()
        
        return jsonify({
            "success": True,
            "paragrafus": struktura['paragrafus'],
            "kulcsszavak": struktura['kulcsszavak'],
            "joghatasok": struktura['joghatasok'],
            "elso_500_karakter": struktura['teljes_szoveg']
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


if __name__ == '__main__':
    # Port és host beállítása
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Jogeset Generátor API indítása...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"📋 Endpoints:")
    print(f"   - GET  /api/health")
    print(f"   - POST /api/generate-jogeset")
    print(f"   - GET  /api/paragrafus-info/<paragrafus>")
    print(f"\n⚠️  FONTOS: Állítsd be az API kulcsokat környezeti változóként!")
    print(f"   - OPENAI_API_KEY")
    print(f"   - ANTHROPIC_API_KEY")
    print(f"   - GEMINI_API_KEY")
    
    app.run(host=host, port=port, debug=True)

