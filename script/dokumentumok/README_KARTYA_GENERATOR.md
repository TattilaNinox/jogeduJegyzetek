# Tanulókártya-generátor Script

Ez a script törvényi szövegből automatikusan generál tanulókártyákat (kérdések, válaszok, magyarázatok) LLM API segítségével.

## Telepítés

### 1. Python package-ek telepítése

```bash
pip install openai anthropic
```

vagy

```bash
pip install -r requirements.txt
```

### 2. API kulcs beállítása

**OpenAI API-hoz:**
```bash
export OPENAI_API_KEY='sk-...'
```

**Anthropic API-hoz:**
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

Az API kulcsokat az alábbi helyeken lehet megszerezni:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

## Használat

### Alapvető használat

```bash
# 2. könyv 8-15. paragrafusaihoz, 2 kártya/paragrafus (alapértelmezett)
python3 script/kartya_generator.py --konyv 2 --tol 8 --ig 15
```

### Opcionális paraméterek

```bash
# 3 kártya paragrafusonként
python3 script/kartya_generator.py --konyv 2 --tol 8 --ig 15 --kartyak 3

# GPT-4 használata (drágább, de jobb minőség)
python3 script/kartya_generator.py --konyv 4 --tol 21 --ig 25 --model gpt-4

# Anthropic Claude API használata
python3 script/kartya_generator.py --konyv 2 --tol 8 --ig 15 --api anthropic --model claude-3-opus

# Kimeneti mappa megadása
python3 script/kartya_generator.py --konyv 2 --tol 8 --ig 15 --output-dir "./kimenet_mappa"
```

## Kimenet

A script három fájlt hoz létre:

- **kerdesek.txt**: A generált kérdések
- **valaszok.txt**: A generált válaszok
- **magyarazatok.txt**: A generált magyarázatok

A fájlok formátuma megegyezik a jelenlegi `feldolgozas.py` script kimenetével, így közvetlenül használhatók további feldolgozásra.

## Paraméterek

### Kötelező paraméterek

- `--konyv`: Könyv száma (pl. 2, 4)
- `--tol`: Kezdő paragrafus száma (pl. 8)
- `--ig`: Végző paragrafus száma (pl. 15)

### Opcionális paraméterek

- `--kartyak`: Kártyák száma paragrafusonként (1-5, alapértelmezett: 2)
- `--api`: API provider ('openai' vagy 'anthropic', alapértelmezett: 'openai')
- `--model`: Model neve (pl. 'gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', alapértelmezett: 'gpt-3.5-turbo')
- `--output-dir`: Kimeneti mappa (alapértelmezett: aktuális mappa)

## Költségek

Az API hívások költségeket generálnak:

- **GPT-3.5-turbo**: ~$0.0015/1K token (ajánlott kezdéshez, olcsó)
- **GPT-4**: ~$0.03/1K token (job minőség, de drágább)

Becslés: 50 paragrafus × 3 kártya ≈ $0.10-0.50 (GPT-3.5-turbo) vagy $1-5 (GPT-4)

## Hibakezelés

A script automatikusan kezeli:
- Rate limiting (várakozással és újrapróbálkozással)
- API hibákat (retry logika, max 3 próbálkozás)
- Hiányzó API kulcsokat (értesítés a felhasználónak)
- Hiányzó paragrafusokat (figyelmeztetés és kihagyás)

## Példa teljes folyamat

```bash
# 1. API kulcs beállítása
export OPENAI_API_KEY='sk-...'

# 2. Script futtatása
cd "/Users/tolgyesiattila/Desktop/Polgári jog/script"
python3 kartya_generator.py --konyv 2 --tol 8 --ig 15 --kartyak 2

# 3. Kimenet használata
# A generált kerdesek.txt, valaszok.txt, magyarazatok.txt fájlok
# közvetlenül használhatók a feldolgozas.py scripttel
```

## Megjegyzések

- A script a `feldolgozas.py`-ból újrafelhasználja a `torveny_fajl_beolvasas` és `torvenyi_szoveg_kinyerese` függvényeket
- A generált kérdések egyetemi szintűek, professzori minőségűek
- A kimenet automatikusan számozott, közvetlenül használható további feldolgozásra

