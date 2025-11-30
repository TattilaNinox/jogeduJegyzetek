#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Egyszerű wrapper a dialógus generátor futtatásához
"""
import sys
import os

# Hozzáadjuk a script mappát a Python path-hoz
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Importáljuk és futtatjuk a fő szkriptet
from script.dialogus_generator_natural import main

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        print("Használat: python futtat_dialogus.py \"Tételek\\A_témakör_neve\"")
        print("\nPélda: python futtat_dialogus.py \"Tételek\\A_specialis_karfelelossegi_alakzatok\"")
        sys.exit(1)
    
    main(base_path)














