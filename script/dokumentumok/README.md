# Feldolgozó szkript használati útmutató

## Szkript helye
A szkript most a fő mappában található: `/Users/tolgyesiattila/Desktop/Polgári jog/script/feldolgozas.py`

## Használat

### Alapvető parancs (a script mappából):
```bash
cd "/Users/tolgyesiattila/Desktop/Polgári jog/script"
python3 feldolgozas.py "../Polgari_Jog_jogi tények"
```

### Más mappákhoz:
```bash
# Még mindig a script mappából futtatva
cd "/Users/tolgyesiattila/Desktop/Polgári jog/script"

python3 feldolgozas.py "../Dologi_jog_fogalma_rendszere"
python3 feldolgozas.py "../A_polgari_jog_fogalma_Ptk_bevezeto"
python3 feldolgozas.py "../Családjog"
```

### Teljes útvonallal (bárhonnan):
```bash
python3 "/Users/tolgyesiattila/Desktop/Polgári jog/script/feldolgozas.py" "/Users/tolgyesiattila/Desktop/Polgári jog/Polgari_Jog_jogi tények"
```

## Követelmények

A célmappában szükséges fájlok:
- `kerdesek.txt` - kérdések sorszámozva
- `valaszok.txt` - válaszok sorszámozva
- `magyarazatok.txt` - magyarázatok sorszámozva

## Kimenet

A szkript létrehozza a következő fájlt a célmappában:
- `feldolgozott_tananyag/tananyag.txt` - a feldolgozott tananyag

## Példa teljes folyamat

```bash
# 1. Menj a script mappába
cd "/Users/tolgyesiattila/Desktop/Polgári jog/script"

# 2. Futtasd le a feldolgozást
python3 feldolgozas.py "../Polgari_Jog_jogi tények"

# 3. Várható kimenet:
# Feldolgozás indítása...
# Mappa: /Users/tolgyesiattila/Desktop/Polgári jog/Polgari_Jog_jogi tények
# Feldolgozás kész! 50 tétel feldolgozva.
# Kimeneti fájl: .../feldolgozott_tananyag/tananyag.txt
```

## Fontos megjegyzések

- ⚠️ **Idézőjelek szükségesek** az útvonal körül, ha szóköz van benne!
- A szkript bármelyik mappára működik, amely tartalmazza a szükséges fájlokat
- A kimeneti mappa automatikusan létrejön

