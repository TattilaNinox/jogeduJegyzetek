# Feldolgozó szkript dokumentáció

## Mit csinál a feldolgozas.py?

A szkript **tanulási segédanyagot generál szövegfelolvasó programok számára** a következő lépésekben:

### 1. **Beolvasás**
- 3 fájlt olvas be: `kerdesek.txt`, `valaszok.txt`, `magyarazatok.txt`
- Sorszámozott tételeket válogat szét (pl. "1. ", "2. ", stb.)

### 2. **Szövegfeldolgozás** (felolvasó-program optimalizálás)
- **Rövidítések kibontása**: pl. → például, Ptk. → Polgári Törvénykönyv
- **Latin kifejezések fonetikusan**: numerus clausus → numerusz klauzusz
- **Számok fonetikusan**: 5:23. § → öt könyvének huszonhárom paragrafusa
- **Speciális karakterek eltávolítása**: zárójelek, nyilak szöveggé alakítása
- **Felsorolások átalakítása**: listajeles pontok folyó szöveggé
- **Duplikációk eltávolítása**: ismétlődő mondatok szűrése

### 3. **Narratív formába alakítás**
- Mondatokra bontás
- Bekezdésekre tagolás (3-5 mondat/bekezdés)
- Üres sorok elhelyezése a tételek között

### 4. **Kimenet generálása**
- `tananyag.txt` fájlba mentés
- 50 tétel, 2 üres sor közöttük

## Használható más esetekben is?

**Igen, de módosítás szükséges:**

### Speciális részek (mostani verzió):
- Ptk. hivatkozások kezelése
- Latin jogi kifejezések
- Jogi rövidítések

### Általánosítható részek:
- Rövidítések kibontása
- Számok fonetikusan írása
- Duplikációk eltávolítása
- Felsorolások átalakítása
- Narratív formába alakítás

## Hogyan adaptálható más témákhoz?

1. **Rövidítések lista módosítása** (`rovidites_kibontas` függvény)
2. **Latin kifejezések lista módosítása** (`latin_fonetikus` függvény)
3. **Törvényi hivatkozások módosítása** (`fonetikus_szamok` függvény)
4. **Fájl elérési utak módosítása** (`main` függvény)
5. **Tételek számának módosítása** (jelenleg 50)

## Példa használat más témákhoz:

- **Orvostudomány**: orvosi rövidítések, latin anatómiai kifejezések
- **Technika**: műszaki rövidítések, speciális karakterek
- **Általános tananyagok**: bármilyen kérdés-válasz-magyarázat formátum

