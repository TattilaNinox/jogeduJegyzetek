================================================================================
MP4 TO MP3 CONVERTER SCRIPT - RÉSZLETES DOKUMENTÁCIÓ
================================================================================

INDÍTÁSI PARANCS
================================================================================

Windows PowerShell-ben:
    python process_mp4_to_mp3.py

Vagy közvetlenül a Python interpreterrel:
    python.exe process_mp4_to_mp3.py

================================================================================
ÁTTEKINTÉS
================================================================================

Ez a Python script automatikusan feldolgozza az MP3 mappában található összes 
MP4 fájlt, és MP3 formátumú audiófájlokat készít belőlük. A script fő funkciói:

1. MP4 fájlok MP3-vá konvertálása
2. 2 másodpercnél hosszabb szünetek automatikus törlése
3. 16 kbps fix bitrate-tel való kódolás
4. Fájlméret ellenőrzése és tájékoztatás

================================================================================
ELŐFELTÉTELEK
================================================================================

1. Python 3.x telepítve
   - A script Python 3.x verzióval működik
   - Ellenőrzés: python --version

2. FFmpeg telepítve és PATH-ban
   - FFmpeg szükséges az audio feldolgozáshoz
   - Letöltés: https://ffmpeg.org/download.html
   - Windows: https://www.gyan.dev/ffmpeg/builds/
   - Telepítés után ellenőrizze: ffmpeg -version

3. MP3 mappa létrehozása
   - A projekt gyökerében hozzon létre egy "MP3" nevű mappát
   - Ide helyezze az MP4 fájlokat, amelyeket feldolgozni szeretne

================================================================================
HASZNÁLAT
================================================================================

1. Készítse elő az MP4 fájlokat:
   - Helyezze az MP4 fájlokat a projekt gyökerében lévő "MP3" mappába

2. Futtassa a scriptet:
   - Nyissa meg a PowerShell-t vagy parancssort
   - Navigáljon a projekt mappájába
   - Futtassa: python process_mp4_to_mp3.py

3. A script működése:
   - Automatikusan megkeresi az MP3 mappában lévő összes MP4 fájlt
   - Ha már létezik MP3 fájl ugyanazzal a névvel, kérdez, hogy felülírja-e
   - Feldolgozza az összes fájlt sorban
   - Minden fájlhoz létrehoz egy MP3 fájlt ugyanazzal a névvel

================================================================================
FUNKCIÓK RÉSZLETES LEÍRÁSA
================================================================================

1. detect_silences_ffmpeg()
   -------------------------
   Feladat: Észleli a szüneteket az audio fájlban
   
   Paraméterek:
   - input_file: Bemeneti audio fájl útvonala
   - min_silence_len: Minimum szünet hossz milliszekundumban (alapértelmezett: 2000 ms = 2 mp)
   - silence_thresh: Szünet küszöbérték dB-ben (alapértelmezett: -50 dB)
   
   Működés:
   - FFmpeg silencedetect filtert használ
   - Kinyeri a szünetek kezdetét és végét
   - Visszaadja a nem szünetes tartományokat listaként [(start_ms, end_ms), ...]
   
   Visszatérési érték:
   - Lista a nem szünetes tartományokról milliszekundumban
   - Ha nincs szünet, az egész fájlt adja vissza
   - Hiba esetén None-t ad vissza

2. remove_long_silences_ffmpeg()
   -------------------------------
   Feladat: Törli a hosszú szüneteket és MP3-vá konvertál
   
   Paraméterek:
   - input_file: Bemeneti fájl útvonala
   - output_file: Kimeneti MP3 fájl útvonala
   - min_silence_len: Minimum szünet hossz ms-ben (alapértelmezett: 2000)
   - silence_thresh: Szünet küszöbérték dB-ben (alapértelmezett: -50)
   - bitrate: Bitrate kbps-ben (alapértelmezett: 16)
   
   Működés:
   a) Szünetek észlelése a detect_silences_ffmpeg() függvénnyel
   b) Ha nincs hang, egy rövid csendet hoz létre
   c) Ha csak egy tartomány van (az egész fájl), egyszerűen konvertál
   d) Ha több rész van:
      - Minden részt külön kivág WAV formátumban
      - Összefűzi a részeket WAV formátumban
      - MP3-vá konvertálja 16 kbps bitrate-tel
   e) Temp fájlok automatikus törlése

3. process_mp4_to_mp3()
   ----------------------
   Feladat: Fő feldolgozási függvény egy MP4 fájlhoz
   
   Paraméterek:
   - input_file: Bemeneti MP4 fájl útvonala
   - output_file: Kimeneti MP3 fájl útvonala
   - target_bitrate: Cél bitrate kbps-ben (alapértelmezett: 16)
   - max_size_mb: Maximális fájlméret MB-ban (alapértelmezett: 7, csak tájékoztató)
   
   Működés:
   a) Megállapítja az eredeti fájl hosszát
   b) Meghívja a remove_long_silences_ffmpeg() függvényt
   c) Ellenőrzi a kimeneti fájl méretét
   d) Kiírja a feldolgozott fájl hosszát
   e) Tájékoztat, ha a fájl mérete meghaladja a 7 MB-ot

4. check_ffmpeg()
   ---------------
   Feladat: Ellenőrzi, hogy FFmpeg telepítve van-e
   
   Visszatérési érték:
   - True: FFmpeg elérhető
   - False: FFmpeg nincs telepítve vagy nem elérhető

5. main()
   -------
   Feladat: Főprogram, amely kezeli a fájlok feldolgozását
   
   Működés:
   a) Ellenőrzi az FFmpeg telepítését
   b) Ellenőrzi az MP3 mappa létezését
   c) Megkeresi az összes MP4 fájlt az MP3 mappában
   d) Minden fájlhoz:
      - Ellenőrzi, hogy már létezik-e MP3 fájl
      - Ha igen, kérdez, hogy felülírja-e
      - Meghívja a process_mp4_to_mp3() függvényt
      - Hibakezelés és folytatás a következő fájllal

================================================================================
TECHNIKAI RÉSZLETEK
================================================================================

1. Szünetek észlelése:
   - FFmpeg silencedetect filter használata
   - Küszöbérték: -50 dB (alapértelmezett)
   - Minimum szünet hossz: 2000 ms (2 másodperc)

2. Audio feldolgozás:
   - Köztes formátum: WAV (PCM 16-bit, little-endian)
   - Végleges formátum: MP3 (libmp3lame codec)
   - Bitrate: 16 kbps (fix)

3. Fájlok összefűzése:
   - FFmpeg concat demuxer használata
   - Temp fájlok a rendszer temp könyvtárában
   - Automatikus törlés feldolgozás után

4. Hibakezelés:
   - Részletes hibaüzenetek kiírása
   - Temp fájlok automatikus törlése hiba esetén
   - Folytatás a következő fájllal hiba esetén

================================================================================
KIMENETI INFORMÁCIÓK
================================================================================

A script a következő információkat jeleníti meg minden fájlhoz:

- Feldolgozás: [fájlnév]
  - Eredeti hossz: [másodperc] másodperc
  - Szünetek törlése (2 mp-nél hosszabb)...
  - Bitrate: 16 kbps
  - Fájlméret: [MB] MB (OK) vagy (FIGYELEM: meghaladja a 7 MB-ot)
  - Feldolgozott hossz: [másodperc] másodperc
  - Kész: [fájlnév].mp3

================================================================================
PÉLDA HASZNÁLAT
================================================================================

1. Előkészítés:
   C:\PROJEKTEK\POLGÁRI JOG\MP3\
      - 2025-11-26 13-25-28.mp4
      - eloadas.mp4

2. Script futtatása:
   C:\PROJEKTEK\POLGÁRI JOG> python process_mp4_to_mp3.py

3. Kimenet:
   2 MP4 fájl található.
   ------------------------------------------------------------
   Feldolgozás: 2025-11-26 13-25-28.mp4
     - Eredeti hossz: 1957.73 másodperc
     - Szünetek törlése (2 mp-nél hosszabb)...
     - Bitrate: 16 kbps
     - Fájlméret: 3.45 MB (OK)
     - Feldolgozott hossz: 1823.12 másodperc
     - Kész: 2025-11-26 13-25-28.mp3

   Feldolgozás: eloadas.mp4
     - Eredeti hossz: 1234.56 másodperc
     - Szünetek törlése (2 mp-nél hosszabb)...
     - Bitrate: 16 kbps
     - Fájlméret: 2.18 MB (OK)
     - Feldolgozott hossz: 1156.78 másodperc
     - Kész: eloadas.mp3

   ------------------------------------------------------------
   Feldolgozás befejezve!

================================================================================
HIBAKEZELÉS
================================================================================

1. FFmpeg nincs telepítve:
   HIBA: FFmpeg nincs telepítve vagy nem elérhető!
   Megoldás: Telepítse az FFmpeg-et és győződjön meg róla, hogy a PATH-ban van.

2. MP3 mappa nem található:
   HIBA: A 'MP3' mappa nem található!
   Megoldás: Hozzon létre egy "MP3" nevű mappát a projekt gyökerében.

3. Nincs MP4 fájl:
   Nincs MP4 fájl a 'MP3' mappában.
   Megoldás: Helyezzen MP4 fájlokat az MP3 mappába.

4. Konverziós hiba:
   A script részletes hibaüzenetet ír ki, amely tartalmazza:
   - Az FFmpeg parancsot
   - A teljes hibaüzenetet
   - További debug információkat

================================================================================
BEÁLLÍTÁSOK MÓDOSÍTÁSA
================================================================================

Ha módosítani szeretné a beállításokat, szerkessze a process_mp4_to_mp3.py fájlt:

1. Bitrate módosítása:
   - Sor 128: bitrate=16 → bitrate=[kívánt érték]
   - Sor 379: target_bitrate=16 → target_bitrate=[kívánt érték]
   - Sor 526: target_bitrate=16 → target_bitrate=[kívánt érték]

2. Szünet küszöbérték módosítása:
   - Sor 15: silence_thresh=-50 → silence_thresh=[kívánt érték dB]
   - Sor 128: silence_thresh=-50 → silence_thresh=[kívánt érték dB]
   - Sor 422: silence_thresh=-50 → silence_thresh=[kívánt érték dB]

3. Minimum szünet hossz módosítása:
   - Sor 15: min_silence_len=2000 → min_silence_len=[ms]
   - Sor 128: min_silence_len=2000 → min_silence_len=[ms]
   - Sor 421: min_silence_len=2000 → min_silence_len=[ms]

4. Maximális fájlméret módosítása:
   - Sor 379: max_size_mb=7 → max_size_mb=[MB]
   - Sor 526: max_size_mb=7 → max_size_mb=[MB]

================================================================================
FÜGGŐSÉGEK
================================================================================

A script a következő Python modulokat használja (beépített modulok):
- os: Fájlrendszer műveletek
- glob: Fájlkeresés
- subprocess: FFmpeg parancsok futtatása
- tempfile: Ideiglenes fájlok kezelése
- json: (jelenleg nem használt, de importálva van)
- shutil: Fájlmásolás műveletek

Külső függőségek:
- FFmpeg: Külső program, nem Python modul

================================================================================
LIMITÁCIÓK ÉS MEGJEGYZÉSEK
================================================================================

1. Bitrate: A script fix 16 kbps bitrate-tel dolgozik. Ez alacsony minőségű,
   de kisebb fájlméretet eredményez. Beszédhez általában elég.

2. Szünetek: Csak a 2 másodpercnél hosszabb szüneteket törli. Rövid szünetek
   megmaradnak.

3. Fájlméret: A script csak tájékoztat, ha a fájl mérete meghaladja a 7 MB-ot,
   de nem akadályozza meg a feldolgozást.

4. Platform: A script Windows-on tesztelve, de működnie kell Linux és macOS
   rendszereken is (FFmpeg elérhetőségétől függően).

5. Temp fájlok: A script ideiglenes fájlokat hoz létre a rendszer temp
   könyvtárában. Ezeket automatikusan törli, de ha a script megszakad,
   manuálisan törölhetők.

================================================================================
VERZIÓ INFORMÁCIÓK
================================================================================

Script neve: process_mp4_to_mp3.py
Verzió: 1.0
Utolsó módosítás: 2025
Python verzió: 3.x
FFmpeg követelmény: Bármely modern verzió

================================================================================
TÁMOGATÁS ÉS KAPCSOLAT
================================================================================

Ha problémába ütközik a script használatakor:
1. Ellenőrizze az FFmpeg telepítését: ffmpeg -version
2. Ellenőrizze a Python verziót: python --version
3. Ellenőrizze, hogy az MP3 mappa létezik-e és tartalmaz-e MP4 fájlokat
4. Nézze meg a részletes hibaüzeneteket a konzolon

================================================================================
VÉGE A DOKUMENTÁCIÓNAK
================================================================================

