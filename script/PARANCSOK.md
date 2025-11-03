# HELYES PARANCSOK - Feldolgozás más mappákkal

## Probléma a régi paranccsal:
```bash
python3 feldolgozas.py "../Polgari_Jog_jogi tények
```
❌ **Hibák:**
- Nincs idézőjel az útvonal körül (szóköz miatt szükséges!)
- A szkriptet nem a helyes helyről futtatod

## ✅ HELYES MÓDOK:

### 1. MÓDSZER: A szkript mappájából futtatva
```bash
cd "/Users/tolgyesiattila/Desktop/Polgári jog/Dologi_jog_fogalma_rendszere"
python3 feldolgozas.py "../Polgari_Jog_jogi tények"
```

### 2. MÓDSZER: Teljes útvonallal (bárhonnan)
```bash
python3 "/Users/tolgyesiattila/Desktop/Polgári jog/Dologi_jog_fogalma_rendszere/feldolgozas.py" "/Users/tolgyesiattila/Desktop/Polgári jog/Polgari_Jog_jogi tények"
```

### 3. MÓDSZER: A célmappából futtatva
```bash
cd "/Users/tolgyesiattila/Desktop/Polgári jog/Polgari_Jog_jogi tények"
python3 "../Dologi_jog_fogalma_rendszere/feldolgozas.py" "."
```

### 4. MÓDSZER: Egyszerűbb (ha a szkript mappájában vagy)
```bash
cd "/Users/tolgyesiattila/Desktop/Polgári jog/Dologi_jog_fogalma_rendszere"
python3 feldolgozas.py "../Polgari_Jog_jogi tények"
```

## ⚠️ FONTOS:
- **Idézőjelek szükségesek**, ha az útvonalban szóköz van!
- A szkript mappájának tartalmaznia kell a `feldolgozas.py` fájlt
- A célmappának tartalmaznia kell: `kerdesek.txt`, `valaszok.txt`, `magyarazatok.txt`

## Tesztelés:
```bash
# 1. Menj a szkript mappájába
cd "/Users/tolgyesiattila/Desktop/Polgári jog/Dologi_jog_fogalma_rendszere"

# 2. Futtasd le a parancsot
python3 feldolgozas.py "../Polgari_Jog_jogi tények"

# Várható eredmény:
# Feldolgozás indítása...
# Mappa: /Users/tolgyesiattila/Desktop/Polgári jog/Polgari_Jog_jogi tények
# Feldolgozás kész! 50 tétel feldolgozva.
# Kimeneti fájl: .../feldolgozott_tananyag/tananyag.txt
```

