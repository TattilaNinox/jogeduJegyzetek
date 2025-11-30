# Természetes Podcast Dialógus Generátor

Ez a szkript természetes, egyetemi szintű podcast dialógust generál tanulókártyákból, TTS (Text-to-Speech) programokhoz optimalizálva.

## Funkciók

- **Természetes dialógus**: Változatos, egyetemi szintű beszélgetés generálása
- **TTS optimalizáció**: 
  - Ptk. hivatkozások szöveges formába alakítása
  - Számok fonetikus írása
  - Rövidítések kibontása
  - Latin kifejezések fonetizálása
  - Speciális karakterek eltávolítása
- **3 kimeneti fájl**:
  - Teljes dialógus
  - Csak kérdések
  - Csak válaszok

## Használat

### Alapvető használat

```bash
python script/dialogus_generator_natural.py
```

Ez az alapértelmezett mappát használja: `Tételek/A_deliktualis_karfelelosseg`

### Egyedi mappa megadása

```bash
python script/dialogus_generator_natural.py "Tételek/A_cselekvokepesseg"
```

### Relatív útvonallal

```bash
python script/dialogus_generator_natural.py "../Masik_temakor"
```

## Követelmények

A célmappában szükséges fájlok:
- `kerdesek.txt` - Kérdések sorszámozva
- `valaszok.txt` - Válaszok sorszámozva
- `magyarazatok.txt` - Magyarázatok sorszámozva

## Kimenet

A szkript létrehozza a `Dialógus` almappát a célmappában, és 3 fájlt generál:

1. `Tanulokartya-Dialogus_{témakör}.txt` - Teljes dialógus
2. `Tanulokartya-Dialogus_{témakör}_kerdezo.txt` - Csak kérdések
3. `Tanulokartya-Dialogus_{témakör}_valaszolo.txt` - Csak válaszok

## Példa

```bash
# Deliktuális kárfelelősség
python script/dialogus_generator_natural.py "Tételek/A_deliktualis_karfelelosseg"

# Cselekvőképesség
python script/dialogus_generator_natural.py "Tételek/A_cselekvokepesseg"

# Más témakör
python script/dialogus_generator_natural.py "Tételek/Masik_temakor"
```

## TTS Optimalizációk

- **Ptk. hivatkozások**: `Ptk. 6:518. §` → `a Polgári Törvénykönyv hatodik könyvének ötszáztizennyolcadik paragrafusa`
- **Számok**: `18` → `tizennyolc`
- **Rövidítések**: `pl.` → `például`
- **Latin**: `ex tunc` → `ex tunk`
- **Speciális karakterek**: Zárójelek, listák eltávolítása

## Jellemzők

- Természetes, változatos kérdések és válaszok
- Egyetemi szintű, tudományos, de természetes stílus
- Nincs "van egy kérdésem" típusú ismétlődés
- Minden blokk után `<break time="5s"/>` szünet

## Python verzió

Python 3.7 vagy újabb


















