# TTS Dialógus Feldolgozó - Használati Útmutató

Ez az útmutató részletesen bemutatja, hogyan használd a `webm_dialogus_osszeallito.py` scriptet TTS hangfelvételek feldolgozására és podcast-szerű dialógusok készítésére.

## Tartalomjegyzék

1. [Áttekintés](#áttekintés)
2. [Telepítés](#telepítés)
3. [Munkafolyamat](#munkafolyamat)
4. [Script használata](#script-használata)
5. [Paraméterek finomhangolása](#paraméterek-finomhangolása)
6. [Hibaelhárítás](#hibaelhárítás)
7. [Példák](#példák)

## Áttekintés

### Mit csinál ez a script?

A `webm_dialogus_osszeallito.py` script három fő feladatot lát el:

1. **Szegmentálás**: WEBM hangfájlokat szétdarabol csend alapján (5 mp szünetek)
2. **Párosítás**: Az N-edik kérdést az N-edik válasszal párosítja
3. **Kimenet generálás**: 
   - 50 db egyedi MP3 fájl (minden kérdés-válasz párhoz)
   - 1 db teljes dialógus MP3 (az egész beszélgetés)

### Miért hasznos?

- **Podcast készítés**: Természetes beszélgetéseket hozhatsz létre két szereplővel
- **Tanulási eszköz**: Kérdés-válasz alapú tananyagokat alakíthatsz át hanganyaggá
- **Rugalmas felhasználás**: Az egyedi fájlokat külön-külön, vagy a teljes dialógust egyben használhatod

## Telepítés

### 1. Előfeltételek ellenőrzése

Futtasd a teszt scriptet:

```cmd
cd "script/Hang jegyzetek"
python teszt_dialogus_feldolgozo.py
```

Ha minden zöld ✓, akkor készen állsz!

### 2. Ha hiányzik valami

Részletes telepítési útmutató: [TELEPITES_DIALOGUS_FELDOLGOZO.md](TELEPITES_DIALOGUS_FELDOLGOZO.md)

**Gyors telepítés:**

```cmd
# Python könyvtárak
pip install pydub numpy

# FFmpeg (Windows, Winget-tel)
winget install --id=Gyan.FFmpeg -e
```

## Munkafolyamat

### 1. Szöveg előkészítése

A dialógus szövegek már TTS-re optimalizálva vannak:
- `Tételek/A_cselekvokepesseg/Dialógus/Csak_Kerdesek_A_cselekvokepesseg.txt`
- `Tételek/A_cselekvokepesseg/Dialógus/Csak_Valaszok_A_cselekvokepesseg.txt`

**Fontos**: Minden kérdés/válasz után van egy `<break time="5s"/>` SSML tag, ami 5 másodperc szünetet jelöl a TTS programban.

### 2. TTS hangfelvétel készítése (Apowersoft Online Screen Audio Recorder)

#### Kérdések felvétele:

1. Nyisd meg: https://www.apowersoft.com/free-audio-recorder-online
2. Töltsd be a `Csak_Kerdesek_A_cselekvokepesseg.txt` fájlt a TTS programodba
3. Állítsd be az Anna hangot (női hang)
4. **FONTOS**: Ellenőrizd, hogy a TTS program felismeri a `<break time="5s"/>` tag-et
5. Indítsd el az Apowersoft felvételt
6. Indítsd el a TTS felolvasást
7. Várj, amíg az összes kérdés elhangzik (5 mp szünetekkel)
8. Állítsd le a felvételt
9. Mentsd el: `MP3/kerdesek.webm`

#### Válaszok felvétele:

1. Töltsd be a `Csak_Valaszok_A_cselekvokepesseg.txt` fájlt
2. Állítsd be a Péter hangot (férfi hang)
3. Ismételd meg a fenti lépéseket
4. Mentsd el: `MP3/valaszok.webm`

### 3. Feldolgozás a scripttel

```cmd
python "script/Hang jegyzetek/webm_dialogus_osszeallito.py" ^
    --kerdesek "MP3/kerdesek.webm" ^
    --valaszok "MP3/valaszok.webm" ^
    --kimenet "Tételek/A_cselekvokepesseg/Dialógus/Audio" ^
    --tetel "A_cselekvokepesseg"
```

### 4. Kimenet ellenőrzése

A script létrehoz:

```
Tételek/A_cselekvokepesseg/Dialógus/Audio/
├── Egyéni/
│   ├── Q01_A_cselekvokepesseg.mp3
│   ├── Q02_A_cselekvokepesseg.mp3
│   ├── ...
│   └── Q50_A_cselekvokepesseg.mp3
├── Teljes_Dialogus_A_cselekvokepesseg.mp3
└── feldolgozas_log.txt
```

## Script használata

### Alapvető parancs

```cmd
python webm_dialogus_osszeallito.py ^
    --kerdesek <kérdések_fájl> ^
    --valaszok <válaszok_fájl> ^
    --kimenet <kimeneti_mappa>
```

### Összes paraméter

| Paraméter | Kötelező | Alapértelmezett | Leírás |
|-----------|----------|----------------|---------|
| `--kerdesek` | ✓ | - | Kérdések WEBM fájlja |
| `--valaszok` | ✓ | - | Válaszok WEBM fájlja |
| `--kimenet` | ✓ | - | Kimeneti mappa az MP3 fájloknak |
| `--tetel` | ✗ | "tetel" | Tétel neve a fájlnév generáláshoz |
| `--csend-hossz` | ✗ | 4000 | Minimális csend hossza ms-ben |
| `--csend-kuszob` | ✗ | -40 | Csend küszöbérték dB-ben |
| `--no-egyeni` | ✗ | False | Ne hozza létre az egyedi fájlokat |
| `--no-teljes` | ✗ | False | Ne hozza létre a teljes dialógust |

### Példák különböző használatokra

#### 1. Csak a teljes dialógus (gyorsabb)

```cmd
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/kerdesek.webm ^
    --valaszok MP3/valaszok.webm ^
    --kimenet Audio/ ^
    --no-egyeni
```

#### 2. Csak az egyedi fájlok

```cmd
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/kerdesek.webm ^
    --valaszok MP3/valaszok.webm ^
    --kimenet Audio/ ^
    --no-teljes
```

#### 3. Egyedi tétel névvel

```cmd
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/kerdesek.webm ^
    --valaszok MP3/valaszok.webm ^
    --kimenet "Tételek/A_tulajdonjog/Dialógus/Audio" ^
    --tetel "A_tulajdonjog"
```

## Paraméterek finomhangolása

### Csend detektálás beállítása

Ha a script nem találja meg megfelelően a szegmenseket, módosítsd ezeket:

#### `--csend-hossz` (Minimális csend hossza)

- **Alapértelmezett**: 4000 ms (4 másodperc)
- **Ajánlott**: 4000-5000 ms
- **Mikor csökkentsd**: Ha túl sok szegmenst hagy ki
- **Mikor növeld**: Ha túl sok hamis szegmenst talál

```cmd
# Szigorúbb detektálás (csak 5+ mp csend)
python webm_dialogus_osszeallito.py ... --csend-hossz 5000

# Lazább detektálás (3+ mp csend is elég)
python webm_dialogus_osszeallito.py ... --csend-hossz 3000
```

#### `--csend-kuszob` (Hangerő küszöb)

- **Alapértelmezett**: -40 dB
- **Ajánlott**: -40 dB vagy -35 dB
- **Mikor csökkentsd** (pl. -45 dB): Ha háttérzaj van, és túl sok hamis szegmenst talál
- **Mikor növeld** (pl. -35 dB): Ha a csendes részeket is beszédnek veszi

```cmd
# Érzékenyebb (csendesebb zajt is szünetnek vesz)
python webm_dialogus_osszeallito.py ... --csend-kuszob -45

# Kevésbé érzékeny (csak a valódi csöndet veszi szünetnek)
python webm_dialogus_osszeallito.py ... --csend-kuszob -35
```

### Tesztelési stratégia

1. **Először tesztelj csak a teljes dialógussal**:
   ```cmd
   python webm_dialogus_osszeallito.py ... --no-egyeni
   ```

2. **Ellenőrizd a log fájlt**: `feldolgozas_log.txt`
   - Hány szegmenst talált?
   - Egyezik-e a várt számmal (50-50)?

3. **Ha nem egyezik, finomhangold a paramétereket**

4. **Ha jó, futtasd le mindent**:
   ```cmd
   python webm_dialogus_osszeallito.py ... 
   ```

## Hibaelhárítás

### "HIBA: A pydub nincs telepítve!"

**Megoldás**:
```cmd
pip install pydub numpy
```

### "HIBA: FFmpeg nem található"

**Megoldás**:
1. Telepítsd az FFmpeg-et (lásd: TELEPITES_DIALOGUS_FELDOLGOZO.md)
2. Ellenőrizd: `ffmpeg -version`
3. Indítsd újra a terminált

### "FIGYELMEZTETÉS: A kérdések (48) és válaszok (52) száma eltér!"

**Okok**:
- A TTS program nem azonosan dolgozta fel a szüneteket
- Hibás `<break>` tag-ek a szövegben
- Eltérő csend hosszak a két fájlban

**Megoldás**:
1. Ellenőrizd a log fájlt, hogy mely szegmensek hiányoznak
2. Próbálj más `--csend-hossz` értéket (pl. 3500 vagy 4500)
3. Hallgasd meg a WEBM fájlokat, hogy valóban 5 mp-es szünetek vannak-e

### Túl sok vagy túl kevés szegmens

**Megoldás**:
```cmd
# Ha TÖBB szegmenst talál, mint kellene (pl. 60 helyett 50)
python webm_dialogus_osszeallito.py ... --csend-hossz 5000

# Ha KEVESEBB szegmenst talál (pl. 40 helyett 50)
python webm_dialogus_osszeallito.py ... --csend-hossz 3500
```

### Rossz minőségű hang

A script 192 kbps VBR minőségben exportál, ami kiváló minőség. Ha mégis rossz:
- Ellenőrizd a bemeneti WEBM fájlok minőségét
- A TTS felvétel minősége határozza meg a végeredményt

## Példák

### 1. Teljes munkafolyamat - A cselekvőképesség tétel

```cmd
# 1. Kérdések felvétele az Apowersoft-tal
#    - Betöltés: Csak_Kerdesek_A_cselekvokepesseg.txt
#    - Hang: Anna (női)
#    - Mentés: MP3/kerdesek.webm

# 2. Válaszok felvétele
#    - Betöltés: Csak_Valaszok_A_cselekvokepesseg.txt
#    - Hang: Péter (férfi)
#    - Mentés: MP3/valaszok.webm

# 3. Feldolgozás
cd "script/Hang jegyzetek"
python webm_dialogus_osszeallito.py ^
    --kerdesek "../../MP3/kerdesek.webm" ^
    --valaszok "../../MP3/valaszok.webm" ^
    --kimenet "../../Tételek/A_cselekvokepesseg/Dialógus/Audio" ^
    --tetel "A_cselekvokepesseg"

# 4. Ellenőrzés
#    - Hallgasd meg: Teljes_Dialogus_A_cselekvokepesseg.mp3
#    - Ellenőrizd az Egyéni mappában az első 2-3 fájlt
#    - Nézd meg a feldolgozas_log.txt-t
```

### 2. Gyors tesztelés új tétellel

```cmd
# Először csak a teljes dialógust hozd létre (gyorsabb)
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/uj_tetel_kerdesek.webm ^
    --valaszok MP3/uj_tetel_valaszok.webm ^
    --kimenet Test_Audio/ ^
    --no-egyeni

# Ha jó, akkor az egyedi fájlokat is
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/uj_tetel_kerdesek.webm ^
    --valaszok MP3/uj_tetel_valaszok.webm ^
    --kimenet "Tételek/Uj_tetel/Dialógus/Audio" ^
    --tetel "Uj_tetel"
```

### 3. Hibajavítás finomhangolással

```cmd
# 1. Alap futtatás
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/kerdesek.webm ^
    --valaszok MP3/valaszok.webm ^
    --kimenet Audio/ ^
    --no-egyeni

# Eredmény: Talált 55 kérdést és 48 választ (nem jó!)

# 2. Szigorúbb csend detektálás
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/kerdesek.webm ^
    --valaszok MP3/valaszok.webm ^
    --kimenet Audio/ ^
    --csend-hossz 4500 ^
    --no-egyeni

# Eredmény: Talált 50 kérdést és 50 választ (jó!)

# 3. Most már létrehozhatod az összes fájlt
python webm_dialogus_osszeallito.py ^
    --kerdesek MP3/kerdesek.webm ^
    --valaszok MP3/valaszok.webm ^
    --kimenet "Tételek/A_cselekvokepesseg/Dialógus/Audio" ^
    --tetel "A_cselekvokepesseg" ^
    --csend-hossz 4500
```

## Tippek és trükkök

### 1. Ellenőrizd a szövegfájlokat TTS előtt

Minden kérdés/válasz után legyen `<break time="5s"/>`:

```text
Mi a cselekvőképesség?

<break time="5s"/>

Mi a jogképesség?

<break time="5s"/>
```

### 2. Használj konzisztens TTS beállításokat

- Ugyanaz a beszédsebesség mindkét felvételnél
- Ugyanaz a hangerő
- Ugyanaz a TTS motor (ne válts közben)

### 3. Tesztelj kis mintával először

Először csak 5 kérdés-válasszal próbáld ki:
- Gyorsabb visszajelzés
- Könnyebb hibakeresés
- Kisebb fájlok

### 4. Log fájl használata

A `feldolgozas_log.txt` mindent tartalmaz:
- Milyen szegmenseket talált
- Melyik hol kezdődik és végződik
- Hibák és figyelmeztetések

## Következő lépések

Most már készen állsz arra, hogy:

1. ✅ TTS felvételeket készíts
2. ✅ Feldolgozd őket a scripttel
3. ✅ Podcast-szerű dialógusokat hozz létre
4. ✅ Webalkalmazásba integráld őket

**Jó tanulást és sikeres podcast készítést!** 🎙️

