# API Működés Részletes Magyarázat

## Hívási lánc

```
Flutter Webalkalmazás
    ↓ HTTP POST kérés
Flask API (jogeset_api.py)
    ↓ Python függvényhívás
jogeset_generator.py (LLMGenerator osztály)
    ↓ HTTP API hívás
LLM Szolgáltató API (OpenAI / Anthropic / Gemini)
    ↓ Válasz (JSON)
jogeset_generator.py (feldolgozza a választ)
    ↓ Jogeset objektum
Flask API (JSON formátumba konvertálja)
    ↓ HTTP Response
Flutter Webalkalmazás
```

## Részletes lépések

### 1. Flutter App kérése

A Flutter app ezt a kérést küldi:
```dart
POST http://localhost:5000/api/generate-jogeset
{
  "paragrafus": "6:519",
  "kategoria": "kártérítés",
  "komplexitas": "közepes",
  "provider": "openai"
}
```

### 2. Flask API fogadja a kérést

**Fájl:** `script/api/jogeset_api.py`

```python
@app.route('/api/generate-jogeset', methods=['POST'])
def generate_jogeset():
    # 1. Kiolvassa a request adatokat
    data = request.get_json()
    paragrafus = data.get('paragrafus')
    
    # 2. Betölti a jogszabály fájlt
    teljes_fajl = load_jogszabaly_fajl()
    
    # 3. Kinyeri a paragrafust
    paragrafus_szoveg = get_paragrafus_szoveg(paragrafus, teljes_fajl)
    
    # 4. Elemzi a jogszabályt
    elemzo = JogszabalyElemzo(paragrafus_szoveg)
    
    # 5. Létrehozza az LLM generátort
    generator = LLMGenerator(provider="openai")
    
    # 6. Meghívja a generálást
    jogeset = generator.generate_jogeset(elemzo, komplexitas, kategoria)
    
    # 7. Visszaadja JSON-ben
    return jsonify({"success": True, "jogeset": {...}})
```

### 3. LLMGenerator.generate_jogeset() metódus

**Fájl:** `script/jogeset_generator.py`

```python
def generate_jogeset(self, jogszabaly_elemzo, komplexitas, kategoria):
    # 1. Létrehozza a promptot
    prompt = self._create_prompt(jogszabaly_elemzo, komplexitas, kategoria)
    
    # 2. Meghívja az LLM API-t (itt történik a külső API hívás!)
    if self.provider == "openai":
        response = self._generate_openai(prompt)  # ← ITT HÍVJA MEG AZ OPENAI API-T
    elif self.provider == "anthropic":
        response = self._generate_anthropic(prompt)  # ← ITT HÍVJA MEG AZ ANTHROPIC API-T
    elif self.provider == "gemini":
        response = self._generate_gemini(prompt)  # ← ITT HÍVJA MEG A GEMINI API-T
    
    # 3. Feldolgozza a választ
    return self._parse_response(response, ...)
```

### 4. _generate_openai() - OpenAI API hívás

**Fájl:** `script/jogeset_generator.py`

```python
def _generate_openai(self, prompt: str) -> str:
    # Ez a függvény HTTP kérést küld az OpenAI API-nak
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Te egy tapasztalt magyar jogász vagy."},
            {"role": "user", "content": prompt}  # ← A generált prompt
        ],
        temperature=0.7,
        max_tokens=2000
    )
    # Visszaadja az LLM válaszát (string)
    return response.choices[0].message.content
```

**Ez a rész hívja meg a külső OpenAI API-t!**

Az OpenAI API URL-je: `https://api.openai.com/v1/chat/completions`

### 5. Visszafelé a lánc

1. **OpenAI API válasza** → JSON string (jogeset leírása)
2. **LLMGenerator._parse_response()** → Jogeset objektum
3. **Flask API** → JSON formátumba konvertálja
4. **Flutter App** → megkapja a JSON-t

## Fontos pontok

### API kulcs szükséges!

Az LLM API-k hívásához **API kulcs szükséges**:

- **OpenAI**: `OPENAI_API_KEY` környezeti változó
- **Anthropic**: `ANTHROPIC_API_KEY` környezeti változó  
- **Gemini**: `GEMINI_API_KEY` környezeti változó

**Beállítás:**
```powershell
$env:OPENAI_API_KEY = "sk-proj-..."
```

### Mi történik, ha nincs API kulcs?

Ha nincs API kulcs, akkor a `_generate_template_based()` metódus fut le, ami csak előre definiált template-eket használ (nem LLM-mel generál).

### Hálózati kérés

Az LLM API hívás **internet kapcsolatot igényel**, mert HTTP kérést küld a külső szolgáltatóhoz (OpenAI, Anthropic, Gemini).

## Példa: Teljes folyamat

```
1. Flutter: "Generálj jogesetet a 6:519. §-hoz!"
   ↓
2. Flask API: "Oké, betöltöm a jogszabály fájlt..."
   ↓
3. Flask API: "Kinyertem a 6:519. § szövegét"
   ↓
4. Flask API: "Létrehozom a promptot az LLM-hez"
   ↓
5. Flask API: "Meghívom az OpenAI API-t..."
   ↓
6. OpenAI API: "Generálok egy jogesetet..." (ez 5-15 másodperc)
   ↓
7. OpenAI API: "Kész! Itt a válasz: {...}"
   ↓
8. Flask API: "Feldolgozom a választ..."
   ↓
9. Flask API: "Visszaküldöm JSON-ben a Flutter appnak"
   ↓
10. Flutter: "Megkaptam a jogesetet! Megjelenítem."
```

## Összefoglalás

**Az API mit hív meg?**

1. **Belső Python függvényeket** (jogszabály elemzés, paragrafus kinyerés)
2. **Külső LLM API-kat** (OpenAI, Anthropic, Gemini) HTTP kérésekkel

A külső LLM API hívás a `_generate_openai()`, `_generate_anthropic()`, vagy `_generate_gemini()` függvényekben történik, amelyek HTTP kérést küldenek az adott szolgáltató API-jához.

