#!/usr/bin/env python3
"""
Jogeset Generátor REST API - JSON Adatbázis Alapú
Flutter webalkalmazáshoz REST API, amely JSON fájlokból választ véletlenszerűen.
Nincs szükséglet szükséges!
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import sys

# Hozzáadjuk a szülő mappát a path-hoz
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from jogeset_db import JogesetDatabase

app = Flask(__name__)
CORS(app)  # CORS engedélyezése Flutter webapp számára

# Adatbázis inicializálása
DB_PATH = script_dir / "jogesetek_db"
db = JogesetDatabase(DB_PATH)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Jogeset Generátor API (JSON alapú) működik",
        "database_path": str(DB_PATH)
    })


@app.route('/api/generate-jogeset', methods=['POST'])
def generate_jogeset():
    """
    Jogeset generálása API endpoint
    Véletlenszerűen választ egy jogesetet a JSON adatbázisból
    """
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
        
        komplexitas = data.get('komplexitas')  # Opcionális
        
        # Véletlenszerű jogeset választása
        jogeset = db.get_random_jogeset(paragrafus, komplexitas)
        
        if not jogeset:
            return jsonify({
                "success": False,
                "error": f"Nem található jogeset a paragrafushoz: {paragrafus}"
            }), 404
        
        # Response JSON formátumban
        return jsonify({
            "success": True,
            "jogeset": jogeset
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Váratlan hiba: {str(e)}"
        }), 500


@app.route('/api/jogesetek/<paragrafus>', methods=['GET'])
def get_all_jogesetek(paragrafus):
    """
    Visszaadja az összes jogesetet egy paragrafushoz
    Flutter app közvetlen használathoz
    """
    try:
        komplexitas = request.args.get('komplexitas')  # Opcionális query paraméter
        
        jogesetek = db.get_all_jogesetek(paragrafus)
        
        if jogesetek is None:
            return jsonify({
                "success": False,
                "error": f"Nem található adatbázis fájl a paragrafushoz: {paragrafus}"
            }), 404
        
        # Szűrés komplexitás szerint, ha meg van adva
        if komplexitas:
            jogesetek = [j for j in jogesetek if j.get('komplexitas') == komplexitas]
        
        return jsonify({
            "success": True,
            "paragrafus": paragrafus,
            "count": len(jogesetek),
            "jogesetek": jogesetek
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/paragrafusok', methods=['GET'])
def list_paragrafusok():
    """Visszaadja az összes elérhető paragrafus számot"""
    try:
        paragrafusok = db.list_paragrafusok()
        return jsonify({
            "success": True,
            "count": len(paragrafusok),
            "paragrafusok": paragrafusok
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/database/<path:filename>', methods=['GET'])
def get_database_file(filename):
    """
    Közvetlenül letölti a JSON fájlt
    Flutter app közvetlen használathoz
    """
    try:
        return send_from_directory(str(DB_PATH), filename, mimetype='application/json')
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404


if __name__ == '__main__':
    import os
    
    # Port és host beállítása
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Jogeset Generátor API (JSON alapú) indítása...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"📁 Adatbázis mappa: {DB_PATH}")
    print(f"📋 Endpoints:")
    print(f"   - GET  /api/health")
    print(f"   - POST /api/generate-jogeset")
    print(f"   - GET  /api/jogesetek/<paragrafus>")
    print(f"   - GET  /api/paragrafusok")
    print(f"   - GET  /api/database/<filename>")
    print(f"\n✅ Nincs szükség API kulcsokra vagy tokenekre!")
    print(f"   Az adatbázis JSON fájlokban van tárolva.")
    
    app.run(host=host, port=port, debug=True)

