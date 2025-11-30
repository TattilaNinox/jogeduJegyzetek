# FFmpeg Telepítési Útmutató

Az `webm_to_mp3.py` script használatához szükséges az FFmpeg telepítése.

## Gyors telepítés (válassz egyet):

### 1. Winget-tel (Windows 10/11 - ajánlott)
```cmd
winget install --id=Gyan.FFmpeg -e
```

### 2. Chocolatey-vel (ha telepítve van)
```cmd
choco install ffmpeg -y
```

### 3. Python scripttel
```cmd
cd script
python install_ffmpeg_python.py
```

### 4. Batch fájllal
```cmd
cd script
install_ffmpeg.bat
```

## Manuális telepítés

Ha az automatikus telepítés nem működik:

1. **Látogasd meg:** https://www.gyan.dev/ffmpeg/builds/
2. **Töltsd le:** `ffmpeg-release-essentials.zip`
3. **Csomagold ki** a ZIP fájlt
4. **Másold** a `bin` mappát valahová (pl. `C:\ffmpeg`)
5. **Add hozzá a PATH-hoz:**
   - Nyisd meg: **Rendszer** → **Speciális rendszerbeállítások** → **Környezeti változók**
   - Szerkeszd a **PATH** változót
   - Add hozzá: `C:\ffmpeg\bin`
6. **Indíts újra a terminált**

## Ellenőrzés

Telepítés után ellenőrizd:
```cmd
ffmpeg -version
```

Ha működik, futtasd a konverter scriptet:
```cmd
cd script
python webm_to_mp3.py
```























