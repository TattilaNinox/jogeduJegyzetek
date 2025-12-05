# JSON Alapú Jogeset Generátor API

## Hogyan működik?

### Egyszerű magyarázat:

1. **JSON fájlokban vannak tárolva a jogesetek**
   - Minden paragrafushoz külön JSON fájl
   - Pl. `6_519.json` tartalmazza a 6:519. §-hoz tartozó jogeseteket

2. **Flutter app kérése:**
   ```
   POST /api/generate-jogeset
   {
     "paragrafus": "6:519"
   }
   ```

3. **API válasza:**
   - Betölti a `6_519.json` fájlt
   - Véletlenszerűen választ egy jogesetet a fájlból
   - Visszaküldi JSON-ben

4. **Változatosság:**
   - Minden kérésnél más jogesetet választ
   - Ugyanarra a paragrafusra több különböző jogeset van

## Előnyök

- ✅ **Nincs szükség API kulcsokra** - nincs OpenAI, Anthropic, Gemini
- ✅ **Gyors** - nincs LLM hívás, csak fájl olvasás
- ✅ **Költségmentes** - nincs token költség
- ✅ **Előre ellenőrzött** - minden jogeset minősített
- ✅ **Flutter app közvetlenül is használhatja** - letöltheti a JSON fájlokat

## Telepítés és futtatás

### 1. Adatbázis inicializálása

Először hozd létre a JSON fájlokat:

```bash
python script/api/init_database.py
```

Ez létrehozza a `script/api/jogesetek_db/` mappát és feltölti példa jogesetekkel.

### 2. API indítása

```bash
python script/api/jogeset_api_json.py
```

### 3. Tesztelés

```bash
python script/api/test_json_api.py
```

## API Endpoints

### POST /api/generate-jogeset

Véletlenszerűen választ egy jogesetet.

**Request:**
```json
{
  "paragrafus": "6:519",
  "komplexitas": "közepes"  // opcionális
}
```

**Response:**
```json
{
  "success": true,
  "jogeset": {
    "id": 2,
    "cim": "Károkozás gyalogosnak",
    "tenyek": "...",
    "kerdes": "...",
    "megoldas": "...",
    "komplexitas": "közepes",
    "kategoria": "kártérítés",
    "alkalmazando_jogszabaly": "6:519. §"
  }
}
```

### GET /api/jogesetek/<paragrafus>

Visszaadja az összes jogesetet egy paragrafushoz.

**Példa:** `GET /api/jogesetek/6:519`

### GET /api/paragrafusok

Visszaadja az összes elérhető paragrafus számot.

### GET /api/database/<filename>

Közvetlenül letölti a JSON fájlt (Flutter app számára).

**Példa:** `GET /api/database/6_519.json`

## JSON Fájl Struktúra

Minden paragrafushoz egy JSON fájl:

```json
{
  "paragrafus": "6:519. §",
  "kategoria": "kártérítés",
  "jogesetek": [
    {
      "id": 1,
      "cim": "Károkozás autóbalesetben",
      "tenyek": "...",
      "kerdes": "...",
      "megoldas": "...",
      "komplexitas": "közepes"
    },
    {
      "id": 2,
      "cim": "Károkozás gyalogosnak",
      "tenyek": "...",
      "kerdes": "...",
      "megoldas": "...",
      "komplexitas": "komplex"
    }
  ]
}
```

## Új jogesetek hozzáadása

### Módszer 1: JSON fájl szerkesztése

Nyisd meg a megfelelő fájlt (pl. `jogesetek_db/6_519.json`) és add hozzá az új jogesetet a `jogesetek` tömbhöz.

### Módszer 2: Python kóddal

```python
from jogeset_db import JogesetDatabase
from pathlib import Path

db = JogesetDatabase(Path("script/api/jogesetek_db"))
db.add_jogeset(
    paragrafus="6:519",
    kategoria="kártérítés",
    jogeset={
        "cim": "Új jogeset címe",
        "tenyek": "...",
        "kerdes": "...",
        "megoldas": "...",
        "komplexitas": "közepes"
    }
)
```

## Flutter integráció

### Opció 1: API használata

```dart
final response = await http.post(
  Uri.parse('http://localhost:5000/api/generate-jogeset'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'paragrafus': '6:519',
  }),
);
```

### Opció 2: Közvetlen JSON használat

A Flutter app letöltheti az összes JSON fájlt és lokálisan választ:

```dart
// Letöltés
final response = await http.get(
  Uri.parse('http://localhost:5000/api/database/6_519.json'),
);

final data = jsonDecode(response.body);
final jogesetek = data['jogesetek'];

// Véletlenszerű választás
final randomJogeset = jogesetek[Random().nextInt(jogesetek.length)];
```

## Összehasonlítás: LLM vs JSON

| Szempont | LLM API | JSON Adatbázis |
|----------|---------|----------------|
| API kulcs | ✅ Szükséges | ❌ Nem kell |
| Válaszidő | ⏱️ 5-15 másodperc | ⚡ Azonnal |
| Költség | 💰 Token költség | 🆓 Ingyenes |
| Változatosság | 🎨 Végtelen | 📚 Korlátozott |
| Minőség | ⚠️ Változó | ✅ Előre ellenőrzött |
| Internet | ✅ Szükséges | ❌ Nem kell (ha lokálisan) |

