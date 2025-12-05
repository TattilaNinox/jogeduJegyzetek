#!/bin/bash
# Jogeset Generátor API indítása Linux/Mac-en

echo "========================================"
echo "JOGESET GENERATOR API INDITASA"
echo "========================================"
echo ""

# Virtual environment aktiválása (ha van)
if [ -f "../../.venv/bin/activate" ]; then
    echo "Virtual environment aktiválása..."
    source ../../.venv/bin/activate
fi

# Függőségek telepítése
echo ""
echo "Függőségek ellenőrzése..."
pip install -q -r requirements.txt

# API indítása
echo ""
echo "API indítása..."
echo ""
python jogeset_api.py

