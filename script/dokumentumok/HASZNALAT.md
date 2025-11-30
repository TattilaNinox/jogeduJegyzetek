# Használati útmutató - feldolgozas.py

## Hogyan használd más mappákkal?

### 1. Parancssori argumentumként (Terminál)

```bash
# Teljes útvonallal
python3 feldolgozas.py "/Users/tolgyesiattila/Desktop/Polgári jog/Családjog"

# Relatív útvonallal (ha a szkript mappájában vagy)
python3 feldolgozas.py "../Családjog"

# Ha a célmappában vagy
cd "/Users/tolgyesiattila/Desktop/Polgári jog/Családjog"
python3 /Users/tolgyesiattila/Desktop/Polgári\ jog/Dologi_jog_fogalma_rendszere/feldolgozas.py .
```

### 2. Python kódban

```python
from feldolgozas import main

# Mappa megadása
main("/Users/tolgyesiattila/Desktop/Polgári jog/Családjog")

# Vagy a szkript mappájának használata (alapértelmezett)
main()
```

### 3. Követelmények

A mappában **szükséges fájlok**:
- `kerdesek.txt` - a kérdések sorszámozva
- `valaszok.txt` - a válaszok sorszámozva  
- `magyarazatok.txt` - a magyarázatok sorszámozva

### 4. Kimenet

A szkript létrehozza a következő mappát és fájlt:
- `feldolgozott_tananyag/tananyag.txt` - a feldolgozott tananyag

### Példa használat

```bash
# Példa 1: Családjog mappa feldolgozása
python3 feldolgozas.py "/Users/tolgyesiattila/Desktop/Polgári jog/Családjog"

# Példa 2: Kötelmi jog mappa feldolgozása
python3 feldolgozas.py "/Users/tolgyesiattila/Desktop/Polgári jog/Kötelmi_jog"
```

### Figyelmeztetések

- Ha hiányzik valamelyik fájl, a szkript figyelmeztetést ad, de folytatja a feldolgozást
- Ha a mappa nem létezik, hibát ad és leáll
- A kimeneti mappa (`feldolgozott_tananyag`) automatikusan létrejön

