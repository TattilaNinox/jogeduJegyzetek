# Dialógus Feldolgozó Telepítési Útmutató

Ez az útmutató segít telepíteni a `webm_dialogus_osszeallito.py` script futtatásához szükséges összes függőséget.

## Követelmények

- Python 3.7 vagy újabb
- FFmpeg (WEBM/MP3 konverzióhoz)
- Python könyvtárak: pydub, numpy

## 1. FFmpeg Telepítése

### Windows - Gyors telepítés (válassz egyet):

#### Winget-tel (ajánlott Windows 10/11-en)
```cmd
winget install --id=Gyan.FFmpeg -e
```

#### Chocolatey-vel
```cmd
choco install ffmpeg -y
```

#### Python scripttel
```cmd
cd script/Hang jegyzetek
python install_ffmpeg_python.py
```

### Ellenőrzés
```cmd
ffmpeg -version
```

Részletes FFmpeg telepítési útmutató: `FFMPEG_TELEPITES.md`

## 2. Python Könyvtárak Telepítése

### Automatikus telepítés (ajánlott)

A projekt gyökérkönyvtárából:
```cmd
pip install -r script/requirements.txt
```

VAGY a Hang jegyzetek mappából:
```cmd
cd "script/Hang jegyzetek"
pip install pydub numpy
```

### Manuális telepítés

Ha a fenti nem működik, egyenként:
```cmd
pip install pydub
pip install numpy
```

## 3. Telepítés Ellenőrzése

Futtasd ezt a Python parancsot:
```python
python -c "from pydub import AudioSegment; import numpy; print('✓ Minden rendben!')"
```

Ha nem ad hibaüzenetet, akkor minden telepítve van!

## 4. Script Tesztelése

```cmd
cd "script/Hang jegyzetek"
python webm_dialogus_osszeallito.py --help
```

## Hibaelhárítás

### "FFmpeg not found" hiba
- Ellenőrizd, hogy az FFmpeg a PATH-ban van: `ffmpeg -version`
- Indítsd újra a terminált a telepítés után
- Windows-on próbáld meg újraindítani a gépet

### "No module named 'pydub'" hiba
- Futtasd újra: `pip install pydub`
- Ellenőrizd a Python verziót: `python --version`
- Próbáld: `python -m pip install pydub`

### "Permission denied" hiba
- Futtasd adminisztrátorként a terminált
- VAGY használd: `pip install --user pydub numpy`

### Import hiba numpy-nál
```cmd
pip install --upgrade numpy
```

## További segítség

Ha továbbra is problémáid vannak, nézd meg a fő projekt dokumentációját:
- `script/HASZNALAT.md`
- `script/README.md`

