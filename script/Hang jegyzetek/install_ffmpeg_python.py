#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg telepítő Python script
Megpróbálja telepíteni az FFmpeg-et különböző módszerekkel
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, shell=False):
    """Futtat egy parancsot és visszaadja az eredményt"""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        else:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_ffmpeg():
    """Ellenőrzi, hogy az ffmpeg telepítve van-e"""
    success, _, _ = run_command(['ffmpeg', '-version'])
    return success

def install_with_winget():
    """Telepíti az ffmpeg-et winget-tel"""
    print("[1/3] Próbálkozás winget-tel...")
    success, _, _ = run_command(['winget', '--version'])
    if not success:
        print("   Winget nem található.")
        return False
    
    print("   Winget található, telepítés...")
    success, stdout, stderr = run_command([
        'winget', 'install', '--id=Gyan.FFmpeg', '-e',
        '--accept-source-agreements', '--accept-package-agreements'
    ])
    
    if success:
        print("   ✓ FFmpeg sikeresen telepítve winget-tel!")
        return True
    else:
        print(f"   ✗ Hiba: {stderr}")
        return False

def install_with_choco():
    """Telepíti az ffmpeg-et Chocolatey-vel"""
    print("[2/3] Próbálkozás Chocolatey-vel...")
    success, _, _ = run_command(['choco', '--version'])
    if not success:
        print("   Chocolatey nem található.")
        return False
    
    print("   Chocolatey található, telepítés...")
    success, stdout, stderr = run_command(['choco', 'install', 'ffmpeg', '-y'])
    
    if success:
        print("   ✓ FFmpeg sikeresen telepítve Chocolatey-vel!")
        return True
    else:
        print(f"   ✗ Hiba: {stderr}")
        return False

def main():
    """Fő függvény"""
    print("="*60)
    print("FFmpeg telepítési script")
    print("="*60)
    print()
    
    # Ellenőrizzük, hogy már telepítve van-e
    if check_ffmpeg():
        print("✓ Az FFmpeg már telepítve van!")
        return 0
    
    # Próbáljuk meg winget-tel
    if install_with_winget():
        print("\n✓ Telepítés sikeres! Indíts újra a terminált, majd futtasd:")
        print("  python webm_to_mp3.py")
        return 0
    
    # Próbáljuk meg Chocolatey-vel
    if install_with_choco():
        print("\n✓ Telepítés sikeres! Indíts újra a terminált, majd futtasd:")
        print("  python webm_to_mp3.py")
        return 0
    
    # Ha egyik sem sikerült
    print("\n" + "="*60)
    print("MANUÁLIS TELEPÍTÉSI ÚTMUTATÓ")
    print("="*60)
    print("\nAz automatikus telepítés nem sikerült.")
    print("\nKérlek, telepítsd manuálisan:")
    print("\n1. Látogasd meg: https://www.gyan.dev/ffmpeg/builds/")
    print("2. Töltsd le a 'ffmpeg-release-essentials.zip' fájlt")
    print("3. Csomagold ki a ZIP fájlt")
    print("4. Másold a 'bin' mappát valahová (pl. C:\\ffmpeg)")
    print("5. Add hozzá a PATH környezeti változóhoz:")
    print("   - Nyisd meg: Rendszer -> Speciális rendszerbeállítások -> Környezeti változók")
    print("   - Szerkeszd a PATH változót és add hozzá: C:\\ffmpeg\\bin")
    print("6. Indíts újra a terminált")
    print("\nVagy próbáld meg manuálisan:")
    print("   winget install --id=Gyan.FFmpeg -e")
    print("   vagy")
    print("   choco install ffmpeg -y")
    print("="*60)
    
    return 1

if __name__ == '__main__':
    sys.exit(main())




