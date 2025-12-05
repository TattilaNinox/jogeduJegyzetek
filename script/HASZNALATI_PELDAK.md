# Jogeset Generátor - Használati Példák

## 🎯 Gyors Start

### ⚠️ FONTOS: PowerShell vs Bash

**PowerShell-ben** (Windows):
- Használj backtick (`) sortöréshez VAGY
- Írd egy sorba

**Bash/Linux/Mac:**
- Használhatod a `\` sortörést

### 1. Egyszerű használat - közvetlen jogszabály szöveg

**PowerShell:**
```powershell
python script/jogeset_generator.py --jogszabaly "Ptk. 6:519. § A károkozó köteles megtéríteni a kárt."
```

**Bash:**
```bash
python script/jogeset_generator.py --jogszabaly "Ptk. 6:519. § A károkozó köteles megtéríteni a kárt."
```

### 2. Fájlból olvasás - teljes jogszabály

**PowerShell:**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt"
```

**Bash:**
```bash
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt"
```

Ez az egész fájlt használja. Ha a fájl nagy, előfordulhat, hogy nem működik jól a template módban. LLM-mel jobban működik.

### 3. Fájlból olvasás - konkrét paragrafus

**Ez a legjobb módszer!** Megadod a fájlt és a paragrafus számot:

**PowerShell (egy sorban):**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519"
```

**PowerShell (több sor, backtick használatával):**
```powershell
python script/jogeset_generator.py `
  --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" `
  --paragrafus "6:519" `
  --kategoria "kártérítés"
```

**Bash:**
```bash
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519"
```

### 4. Teljes példa kategóriával és komplexitással

**PowerShell (egy sorban):**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519" --kategoria "kártérítés" --komplexitas "komplex" --provider "template"
```

**PowerShell (több sor):**
```powershell
python script/jogeset_generator.py `
  --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" `
  --paragrafus "6:519" `
  --kategoria "kártérítés" `
  --komplexitas "komplex" `
  --provider "template"
```

**Bash:**
```bash
python script/jogeset_generator.py \
  --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" \
  --paragrafus "6:519" \
  --kategoria "kártérítés" \
  --komplexitas "komplex" \
  --provider "template"
```

## 📋 További Példák

### Szerződéses jogeset

**PowerShell:**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:1" --kategoria "szerződés" --komplexitas "közepes"
```

**Bash:**
```bash
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:1" --kategoria "szerződés" --komplexitas "közepes"
```

### Tulajdonjog átruházás

**PowerShell:**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "5:38" --kategoria "tulajdonjog" --komplexitas "komplex"
```

**Bash:**
```bash
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "5:38" --kategoria "tulajdonjog" --komplexitas "komplex"
```

### Jogképesség

**PowerShell:**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "2:1" --kategoria "jogképesség" --komplexitas "közepes"
```

**Bash:**
```bash
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "2:1" --kategoria "jogképesség" --komplexitas "közepes"
```

### Tetszőleges paragrafus (pl. házasság)

**PowerShell:**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "4:15" --kategoria "házasság"
```

## 🔍 Paragrafus szám formátumok

A paragrafus számot többféle formátumban is megadhatod:

- `6:519` ✅
- `6:519.` ✅
- `6:519. §` ✅
- `Ptk. 6:519` ✅
- `Ptk. 6:519. §` ✅

## 💡 Tippek

1. **Mindig add meg a kategóriát**, ha tudod - így jobb template-et kapod
2. **Használj paragrafus számot** fájlból olvasáskor - így csak a releváns részt használja
3. **Template mód** jó példa jogesetekhez, de **LLM mód** (OpenAI/Anthropic/Gemini) egyedi, kreatív jogesetekhez

## 🚀 LLM mód használata

Ha van API kulcsod:

**PowerShell:**
```powershell
# OpenAI
$env:OPENAI_API_KEY = "sk-..."
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519" --provider openai

# Anthropic Claude
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519" --provider anthropic

# Google Gemini
$env:GEMINI_API_KEY = "..."
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519" --provider gemini
```

**Bash:**
```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
python script/jogeset_generator.py --fajl "forrasok/..." --paragrafus "6:519" --provider openai

# Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."
python script/jogeset_generator.py --fajl "forrasok/..." --paragrafus "6:519" --provider anthropic

# Google Gemini
export GEMINI_API_KEY="..."
python script/jogeset_generator.py --fajl "forrasok/..." --paragrafus "6:519" --provider gemini
```

## 📁 Kimeneti fájlok

A generált jogesetek automatikusan a `jogesetek/` mappába kerülnek:

```
jogesetek/
  ├── jogeset_6_519_20250115_143022.json
  ├── jogeset_6_1_20250115_143045.json
  └── ...
```

Ha egyedi fájlnevet szeretnél:

**PowerShell:**
```powershell
python script/jogeset_generator.py --fajl "forrasok/2013. évi V. törvény a Polgári Törvénykönyvről.txt.txt" --paragrafus "6:519" --kimenet "jogesetek/saját_fájl.json"
```

**Bash:**
```bash
python script/jogeset_generator.py --fajl "forrasok/..." --paragrafus "6:519" --kimenet "jogesetek/saját_fájl.json"
```

