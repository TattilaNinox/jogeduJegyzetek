# Python Scriptek Tájékoztatója

Ez a dokumentum tartalmazza a projektben található Python scriptek rövid leírását és használati útmutatóját.

---

## 📚 TANANYAG FELDOLGOZÁS ÉS GENERÁLÁS

### `feldolgozas_altalanos.py`

**Feladat:** Általánosított feldolgozó script tananyag-generáláshoz. Feldolgozza a kérdéseket, válaszokat és magyarázatokat, rövidítéseket kibontja, latin kifejezéseket fonetizálja, számokat szóra alakítja.

**Használat:** A scriptet közvetlenül módosítani kell a konfiguráció részben (konyvtar, fájl útvonalak).

```python
# A script belsejében módosítandó:
konyvtar = '/path/to/konyvtar'
feldolgoz_fajlokat(
    kerdesek_utvonal='kerdesek.txt',
    valaszok_utvonal='valaszok.txt',
    magyarazatok_utvonal='magyarazatok.txt',
    kimenet_utvonal='feldolgozott_tananyag/tananyag.txt',
    tetel_szama=50,
    konyvtar=konyvtar
)
```

---

### `kartya_generator.py`

**Feladat:** Tanulókártya-generátor script LLM API-val. Törvényi szövegből generál tanulókártyákat a megadott könyv és paragrafus tartomány alapján.

**Parancs:**

```bash
python script/kartya_generator.py --konyv 2 --tol 8 --ig 15
```

**Opcionális paraméterek:**

```bash
python script/kartya_generator.py --konyv 4 --tol 21 --ig 25 --kartyak 3 --api openai --model gpt-4 --output-dir "./kimenet"
```

**Paraméterek:**
- `--konyv` - Kötelező: Könyv száma (pl. 2, 4)
- `--tol` - Kötelező: Kezdő paragrafus száma
- `--ig` - Kötelező: Végző paragrafus száma
- `--kartyak` - Opcionális: Kártyák száma paragrafusonként (1-5, alapértelmezett: 2)
- `--api` - Opcionális: API provider (openai vagy anthropic, alapértelmezett: openai)
- `--model` - Opcionális: Model neve (alapértelmezett: gpt-3.5-turbo)
- `--output-dir` - Opcionális: Kimeneti mappa (alapértelmezett: aktuális mappa)

---

### `szamok_generalas.py`

**Feladat:** Segédszkript a számok melléknévi alakjának generálásához. Generálja az 1-től 900-ig a melléknévi alakokat szótár formátumban.

**Parancs:**

```bash
python script/szamok_generalas.py
```

**Kimenet:** A konzolra írja ki a szótárat, amelyet másolni lehet más scriptekbe.

---

## 🔄 HTML/TXT KONVERZIÓ

### `tetelek_html_generator.py`

**Feladat:** HTML generáló szkript a Tételek mappában lévő kidolgozott tételek HTML formátumba konvertálásához. Szép formázással, CSS stílusokkal generál HTML fájlokat.

**Parancs:**

```bash
python script/tetelek_html_generator.py "Tételek"
```

**Vagy egy konkrét fájlhoz:**

```bash
python script/tetelek_html_generator.py "Tételek/A_cselekvokepesseg.txt"
```

**Megjegyzés:** Ha nincs megadva argumentum, akkor alapértelmezettként a `Tételek` mappát dolgozza fel.

**Kimenet:** A `html_tetelek` mappába menti az HTML fájlokat.

---

### `html_to_txt_converter.py`

**Feladat:** HTML to TXT Converter. Konvertálja a HTML tételeket vissza .txt fájlokká Markdown formátumban.

**Parancs:**

```bash
python script/html_to_txt_converter.py
```

**Megjegyzés:** A script automatikusan keresi a HTML fájlokat és konvertálja őket TXT formátumba.

---

## 🔧 HIBAJAVÍTÁS

### `tetelek_hibajavitas.py`

**Feladat:** TTS feldolgozott szövegek hibajavító szkripte. Automatikusan javítja a valódi hibákat (duplikációk, formázási hibák), miközben megtartja a jogászi kifejezésmódokat és hosszú hivatkozásokat.

**Parancs egy fájlhoz:**

```bash
python script/tetelek_hibajavitas.py input.txt output.txt
```

**Parancs egy mappához:**

```bash
python script/tetelek_hibajavitas.py Tételek/
```

**Megjegyzés:** Ha mappa van megadva, akkor az összes .txt fájlt feldolgozza és egy `hibajavitas` almappába menti.

---

## 🎵 HANG FELDOLGOZÁS

### `webm_dialogus_osszeallito.py`

**Feladat:** TTS Dialógus Összeállító Script. WEBM hangfájlokat (kérdések és válaszok) dolgoz fel: csend alapján szegmentálja őket, párosítja a kérdéseket és válaszokat, létrehozza az egyedi MP3 fájlokat minden kérdés-válasz párhoz, és létrehozza a teljes dialógus MP3-at.

**Alap parancs:**

```bash
python script/Hang jegyzetek/webm_dialogus_osszeallito.py --kerdesek kerdesek.webm --valaszok valaszok.webm --kimenet Audio/
```

**Paraméter finomhangolással:**

```bash
python script/Hang jegyzetek/webm_dialogus_osszeallito.py --kerdesek kerdesek.webm --valaszok valaszok.webm --kimenet Audio/ --csend-hossz 5000 --csend-kuszob -35 --tetel "Hazassagkotes"
```

**Paraméterek:**
- `--kerdesek` - Kötelező: Kérdések WEBM fájlja
- `--valaszok` - Kötelező: Válaszok WEBM fájlja
- `--kimenet` - Kötelező: Kimeneti mappa az MP3 fájloknak
- `--tetel` - Opcionális: Tétel neve a fájlnevek generálásához (alapértelmezett: tetel)
- `--csend-hossz` - Opcionális: Minimális csend hossza ms-ben (alapértelmezett: 4000)
- `--csend-kuszob` - Opcionális: Csend küszöbérték dB-ben (alapértelmezett: -40)
- `--no-egyeni` - Opcionális: Ne hozza létre az egyedi fájlokat, csak a teljes dialógust
- `--no-teljes` - Opcionális: Ne hozza létre a teljes dialógust, csak az egyedi fájlokat

**Követelmények:**
- pydub (`pip install pydub`)
- numpy (`pip install numpy`)
- FFmpeg (telepítve és PATH-ban)

---

### `webm_to_mp3.py`

**Feladat:** WebM to MP3 Converter. Konvertálja a WebM fájlokat MP3 formátumra, maximum 5 MB mérettel.

**Parancs:**

```bash
python script/Hang jegyzetek/webm_to_mp3.py
```

**Megjegyzés:** A script automatikusan keresi a `MP3` mappában lévő összes `.webm` fájlt és konvertálja őket `.mp3` formátumba. Ha az MP3 fájl mérete meghaladja az 5 MB-ot, akkor automatikusan csökkenti a bitrátát.

**Követelmények:**
- FFmpeg (telepítve és PATH-ban)

---

### `install_ffmpeg_python.py`

**Feladat:** FFmpeg telepítő Python script. Megpróbálja telepíteni az FFmpeg-et különböző módszerekkel (winget, chocolatey, manuális letöltés).

**Parancs:**

```bash
python script/Hang jegyzetek/install_ffmpeg_python.py
```

**Megjegyzés:** A script automatikusan próbálja a különböző telepítési módszereket és jelzi, ha sikeres volt a telepítés.

---

## 📂 DIALÓGUS FELDOLGOZÁS

### `split_dialogus.py` (projekt gyökér)

**Feladat:** Általános script dialógus fájlok szétválasztására kérdésekre és válaszokra. Beolvassa a dialógus fájlt, különválasztja a "Kérdező:" és "Válaszoló:" sorokat, minden után beszúrja a `<break time="5s"/>` taget, és két külön fájlba menti őket.

**Parancs fájl elérési úttal:**

```bash
python split_dialogus.py "Tételek/A_hazassagkotes_eljaras_kellekei/Dialogus_Hazassagkotes_eljaras.txt"
```

**Interaktív mód (ha nincs argumentum):**

```bash
python split_dialogus.py
```

**Megjegyzés:** Windows-on drag & drop-tel is használható (húzd rá a fájlt a scriptre).

**Működés:**
- Létrehozza a `Dialogus` mappát a forrás fájl mappájában
- Generál két fájlt: `{forrás_fájl_neve}_kerdesek.txt` és `{forrás_fájl_neve}_valaszok.txt`
- Áthelyezi a forrás fájlt a `Dialogus` mappába
- Minden kérdés/válasz után beszúrja a `<break time="5s"/>` taget

---

## 📝 MEGJEGYZÉSEK

- A legtöbb script UTF-8 kódolást használ
- A scriptek általában a `script` mappából kell futtatni, vagy teljes útvonallal kell megadni őket
- A hang feldolgozó scriptekhez szükséges az FFmpeg telepítése
- Néhány script (pl. `feldolgozas_altalanos.py`) közvetlenül a kódban módosítandó konfigurációval működik
- A `split_dialogus.py` a projekt gyökerében található, nem a `script` mappában

---

## 🔗 KAPCSOLÓDÓ DOKUMENTÁCIÓK

- `script/README.md` - Általános README
- `script/HASZNALAT.md` - Használati útmutatók
- `script/PARANCSOK.md` - Parancsok gyűjteménye
- `script/SCRIPTEK_DOKUMENTACIO_2025.txt` - Részletes dokumentáció

