# Jogeset Generátor - Használati Útmutató

Ez a Python szkript lehetővé teszi **fiktív, de reális jogesetek** generálását egy adott jogszabály alapján. A szkript LLM (Large Language Model) technológiát használ a jogesetek létrehozásához.

## 📋 Tartalomjegyzék

1. [Áttekintés](#áttekintés)
2. [Telepítés](#telepítés)
3. [Használat](#használat)
4. [Input formátumok](#input-formátumok)
5. [Példák](#példák)
6. [LLM Szolgáltatók](#llm-szolgáltatók)
7. [Output formátum](#output-formátum)

## 🎯 Áttekintés

A jogeset generátor a következőket teszi:

1. **Jogszabály elemzése**: Kinyeri a paragrafus számot, kulcsszavakat, joghatásokat
2. **Jogeset generálása**: LLM segítségével létrehoz egy reális jogesetet
3. **Strukturált output**: JSON formátumban menti az eredményt

### Generált jogeset struktúra:

- **Cím**: Rövid, beszédes cím
- **Tényállás**: Részletes tények leírása (személyek, dátumok, események)
- **Jogi kérdés**: Mi a jogi probléma?
- **Alkalmazandó jogszabály**: Melyik jogszabály vonatkozik?
- **Megoldás**: Részletes jogi elemzés

## 📦 Telepítés

### 1. Alapkövetelmények

```bash
pip install openai anthropic google-generativeai
```

Vagy csak az egyiket, amit használni szeretnél:

```bash
# OpenAI
pip install openai

# Anthropic Claude
pip install anthropic

# Google Gemini
pip install google-generativeai
```

### 2. API kulcsok beállítása

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = "your-api-key-here"
# vagy
$env:ANTHROPIC_API_KEY = "your-api-key-here"
# vagy
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Windows CMD:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🚀 Használat

### Alapvető használat

```bash
python script/jogeset_generator.py --jogszabaly "Ptk. 6:519. § - A károkozó köteles megtéríteni a kárt"
```

### Fájlból olvasás

```bash
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519"
```

### Interaktív mód

```bash
python script/jogeset_generator.py --interaktiv
```

### Paraméterek

| Paraméter | Leírás | Példa |
|-----------|--------|-------|
| `--jogszabaly` | Jogszabály szövege közvetlenül | `"Ptk. 6:519. §"` |
| `--fajl` | Fájl elérési útja | `"forrasok/jogszabaly.txt"` |
| `--paragrafus` | Paragrafus száma | `"6:519"` |
| `--komplexitas` | Komplexitás szintje | `egyszerű`, `közepes`, `komplex` |
| `--kategoria` | Jogi kategória | `szerződés`, `kártérítés`, `tulajdonjog` |
| `--provider` | LLM szolgáltató | `openai`, `anthropic`, `gemini`, `template` |
| `--kimenet` | Kimeneti fájl | `"jogesetek/pelda.json"` |
| `--interaktiv` | Interaktív mód | (nincs érték) |

## 📝 Input formátumok

### 1. Közvetlen jogszabály szöveg

```bash
python script/jogeset_generator.py \
  --jogszabaly "Ptk. 6:519. § (1) A károkozó köteles megtéríteni a kárt, ha nem bizonyítja, hogy a kár nem az ő hibájából következett be."
```

### 2. Fájlból olvasás

A fájl tartalmazhatja:
- Teljes jogszabályt
- Egy konkrét paragrafust
- Több paragrafust

```bash
python script/jogeset_generator.py \
  --fajl "Tételek/A_polgari_jogi_tenyek.txt" \
  --komplexitas "komplex"
```

### 3. Strukturált input (JSON)

Létrehozhatsz egy JSON fájlt is:

```json
{
  "jogszabaly": "Ptk. 6:519. §",
  "szoveg": "A károkozó köteles megtéríteni a kárt...",
  "komplexitas": "közepes",
  "kategoria": "kártérítés"
}
```

## 💡 Példák

### Példa 1: Egyszerű szerződéses jogeset

```bash
python script/jogeset_generator.py \
  --jogszabaly "Ptk. 6:1. § A szerződés a felek megállapodása." \
  --komplexitas "egyszerű" \
  --kategoria "szerződés" \
  --kimenet "jogesetek/szerzodes_egyszeru.json"
```

### Példa 2: Komplex kártérítési eset

```bash
python script/jogeset_generator.py \
  --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" \
  --paragrafus "6:519" \
  --komplexitas "komplex" \
  --kategoria "kártérítés" \
  --provider "openai" \
  --kimenet "jogesetek/karterites_komplex.json"
```

### Példa 3: Template alapú generálás (LLM nélkül)

Ha nincs API kulcsod, használhatod a template módot:

```bash
python script/jogeset_generator.py \
  --jogszabaly "Ptk. 2:1. § Minden ember jogképes." \
  --provider "template" \
  --kimenet "jogesetek/template_pelda.json"
```

## 🤖 LLM Szolgáltatók

### OpenAI (GPT-4)

**Előnyök:**
- Nagyon jó minőség
- Gyors válaszidő
- Megbízható

**Hátrányok:**
- Fizetős API
- API kulcs szükséges

**Használat:**
```bash
export OPENAI_API_KEY="sk-..."
python script/jogeset_generator.py --provider openai ...
```

### Anthropic (Claude)

**Előnyök:**
- Kiváló minőség
- Hosszabb válaszok
- Jó magyar nyelvű támogatás

**Használat:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python script/jogeset_generator.py --provider anthropic ...
```

### Google Gemini

**Előnyök:**
- Ingyenes tier elérhető
- Jó minőség

**Használat:**
```bash
export GEMINI_API_KEY="..."
python script/jogeset_generator.py --provider gemini ...
```

### Template (LLM nélkül)

**Előnyök:**
- Nincs API kulcs szükséges
- Ingyenes
- Gyors
- Előre definiált, minőségi példa jogesetek

**Hátrányok:**
- Csak előre definiált kategóriákhoz (kártérítés, szerződés, tulajdonjog, jogképesség)
- Nincs kreatív, egyedi generálás
- Korlátozott számú példa

**Használat:**
```bash
python script/jogeset_generator.py --provider template ...
```

**Megjegyzés:** A template mód most már részletes, reális példa jogeseteket tartalmaz a leggyakoribb kategóriákhoz. Ha más kategóriát vagy egyedi jogesetet szeretnél, használj LLM szolgáltatót.

## 📤 Output formátum és mentési hely

### Mentési hely

A generált jogeseteket a szkript **automatikusan menti** a következő helyre:

- **Alapértelmezett mappa**: `jogesetek/` (a projekt gyökerében)
- **Fájlnév**: Ha nem adsz meg fájlnevet, automatikusan generál egyet:
  - Formátum: `jogeset_{paragrafus}_{timestamp}.json`
  - Példa: `jogeset_6_519_20250115_143022.json`

### Kimeneti fájl megadása

- **Egyedi fájlnév**: `--kimenet "jogesetek/saját_fájl.json"`
- **Relatív útvonal**: A projekt root-hoz képest
- **Abszolút útvonal**: Teljes elérési út megadása

**Példa:**
```bash
# Alapértelmezett helyre ment (jogesetek/ mappa)
python script/jogeset_generator.py --jogszabaly "Ptk. 6:519. §"

# Egyedi fájlnév megadása
python script/jogeset_generator.py --jogszabaly "Ptk. 6:519. §" --kimenet "jogesetek/karterites_pelda.json"
```

### Output formátum

A generált jogeset JSON formátumban kerül mentésre:

```json
{
  "cim": "Károkozás autóbalesetben",
  "tenyek": "2024. március 15-én, délután 14:30-kor Budapesten...",
  "kerdes": "Következik-e kártérítési kötelezettség?",
  "alkalmazando_jogszabaly": "Ptk. 6:519. §",
  "megoldas": "A Ptk. 6:519. § (1) bekezdése szerint...",
  "komplexitas": "közepes",
  "kategoria": "kártérítés"
}
```

## 🔍 Milyen inputra van szükség?

### Minimális input:

1. **Jogszabály szövege** - legalább egy paragrafus vagy részlet
2. **Paragrafus szám** (opcionális, de ajánlott)

### Ajánlott input:

1. **Teljes jogszabály szöveg** - jobb kontextus
2. **Paragrafus szám** - pontos azonosítás
3. **Kategória** - jobb kategorizálás
4. **Komplexitás** - a kívánt nehézségi szint

### Példa input fájl struktúra:

```
Ptk. 6:519. § [A kártérítési kötelezettség]

(1) A károkozó köteles megtéríteni a kárt, ha nem bizonyítja, 
hogy a kár nem az ő hibájából következett be.

(2) A kártérítés magában foglalja a kár megtérítését és a 
megtérített kár megtérítését is.
```

## ⚠️ Fontos megjegyzések

1. **Fiktív jogesetek**: A generált jogesetek **fiktívek**, tanulási célokra készülnek
2. **Jogi tanácsadás**: Nem helyettesíti a valódi jogi tanácsadást
3. **Ellenőrzés**: Mindig ellenőrizd a generált jogeseteket
4. **API költségek**: Az LLM API-k használata költségekkel járhat

## 🛠️ Fejlesztési lehetőségek

- [ ] Több jogeset egyszerre generálása
- [ ] Batch feldolgozás fájlokból
- [ ] Jogesetek validálása
- [ ] Helyi LLM támogatás (Ollama, LM Studio)
- [ ] Webes felület
- [ ] Jogesetek adatbázisa

## 📚 Kapcsolódó dokumentáció

- [Polgári Törvénykönyv](forrasok/2013.%20évi%20V.%20törvény%20a%20Polgári%20Törvénykönyvről.txt.txt)
- [Jogi tények](Tételek/A_polgari_jogi_tenyek.txt)

