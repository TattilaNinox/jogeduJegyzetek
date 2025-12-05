# Jogeset Generátor REST API

REST API Flutter webalkalmazáshoz, amely LLM-mel generál egyedi jogeseteket.

## Telepítés

```bash
cd script/api
pip install -r requirements.txt
```

## Környezeti változók

Állítsd be az API kulcsokat:

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-..."
# vagy
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# vagy
$env:GEMINI_API_KEY = "..."
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

Vagy használj `.env` fájlt (lásd `.env.example`).

## Futtatás

```bash
python script/api/jogeset_api.py
```

Az API a `http://localhost:5000` címen lesz elérhető.

## API Endpoints

### 1. Health Check

**GET** `/api/health`

Válasz:
```json
{
  "status": "ok",
  "message": "Jogeset Generátor API működik"
}
```

### 2. Jogeset generálása

**POST** `/api/generate-jogeset`

Request body:
```json
{
  "paragrafus": "6:519",
  "kategoria": "kártérítés",
  "komplexitas": "közepes",
  "provider": "openai"
}
```

Response:
```json
{
  "success": true,
  "jogeset": {
    "cim": "Károkozás autóbalesetben",
    "tenyek": "...",
    "kerdes": "...",
    "alkalmazando_jogszabaly": "6:519. §",
    "megoldas": "...",
    "komplexitas": "közepes",
    "kategoria": "kártérítés"
  }
}
```

### 3. Paragrafus információk

**GET** `/api/paragrafus-info/<paragrafus>`

Példa: `GET /api/paragrafus-info/6:519`

Response:
```json
{
  "success": true,
  "paragrafus": "6:519. §",
  "kulcsszavak": ["károkozó", "kár", "köteles"],
  "joghatasok": ["keletkezés"],
  "elso_500_karakter": "..."
}
```

## Tesztelés

### cURL példa:

```bash
curl -X POST http://localhost:5000/api/generate-jogeset \
  -H "Content-Type: application/json" \
  -d '{
    "paragrafus": "6:519",
    "kategoria": "kártérítés",
    "komplexitas": "közepes",
    "provider": "openai"
  }'
```

### Python példa:

```python
import requests

response = requests.post(
    'http://localhost:5000/api/generate-jogeset',
    json={
        'paragrafus': '6:519',
        'kategoria': 'kártérítés',
        'komplexitas': 'közepes',
        'provider': 'openai'
    }
)

print(response.json())
```

## Flutter integráció

A Flutter webapp-ból így hívhatod meg:

```dart
Future<Map<String, dynamic>> generateJogeset({
  required String paragrafus,
  String? kategoria,
  String komplexitas = 'közepes',
  String provider = 'openai',
}) async {
  final response = await http.post(
    Uri.parse('http://localhost:5000/api/generate-jogeset'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'paragrafus': paragrafus,
      'kategoria': kategoria,
      'komplexitas': komplexitas,
      'provider': provider,
    }),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to generate jogeset');
  }
}
```

## Változatosság

Minden kérésnél automatikusan változatosságot ad a promptnak, így minden alkalommal más jogeset generálódik ugyanarra a jogszabályhelyre.

## Hibakezelés

Az API JSON formátumban adja vissza a hibákat:

```json
{
  "success": false,
  "error": "Hibaüzenet"
}
```

HTTP státusz kódok:
- `200`: Sikeres
- `400`: Hibás kérés (pl. hiányzó paragrafus)
- `500`: Szerver hiba

