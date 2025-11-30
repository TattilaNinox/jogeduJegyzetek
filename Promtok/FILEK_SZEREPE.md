# Fájlok szerepe és használata

## 🎯 MELYIK FÁJLT HASZNÁLD?

### 1. **AI_PROMPT_SABLON.txt** ⭐ (EZ A FŐ!)
**Kinek kell:** Az AI-nak  
**Mikor:** MINDEN generálás előtt  
**Mit csinálsz:** Másold be az AI prompt mezőbe + add hozzá a tételt  
**Miért:** Ez tartalmazza MINDENT, amit az AI-nak tudnia kell

---

### 2. **KRITIKUS_SZABALYOK_ROVID.txt**
**Kinek kell:** NEKED (nem az AI-nak!)  
**Mikor:** Ha gyorsan át akarod nézni a szabályokat  
**Mit csinálsz:** Olvasd el, hogy megértsd a szabályokat  
**Miért:** Ha nem akarod a teljes sablont használni, vagy gyorsan át akarod nézni

**⚠️ FONTOS:** Ez NEM kell az AI-nak, mert az AI_PROMPT_SABLON.txt már tartalmazza!

---

### 3. **ELOTTE_ELLENORIZD_MINDIG.txt**
**Kinek kell:** NEKED (nem az AI-nak!)  
**Mikor:** Amikor ELLENŐRZÖD a generált szöveget  
**Mit csinálsz:** Használd ellenőrzési checklistként  
**Miért:** Részletesebb ellenőrzési lista, mint a sablonban

**⚠️ FONTOS:** Ez NEM kell az AI-nak, csak neked az ellenőrzéshez!

---

### 4. **HASZNALATI_UTASITAS.md**
**Kinek kell:** NEKED (nem az AI-nak!)  
**Mikor:** Amikor először használod a rendszert  
**Mit csinálsz:** Olvasd el, hogy megértsd a teljes folyamatot  
**Miért:** Teljes útmutató a munkafolyamathoz

**⚠️ FONTOS:** Ez NEM kell az AI-nak, csak neked!

---

## 📋 MUNKAFOLYAMAT (EGYSZERŰEN):

### Generálás:
1. ✅ Másold be: **AI_PROMPT_SABLON.txt** az AI-ba
2. ✅ Add hozzá a tételt
3. ✅ Generálj
4. ✅ **AZ AI AUTOMATIKUSAN ellenőrzi és javítja a hibákat!**

### Opcionális utólagos ellenőrzés (ha mégis hiba van):
1. ✅ Ellenőrizd kézzel (használd: **ELOTTE_ELLENORIZD_MINDIG.txt**)
2. ✅ Vagy futtasd: `python script/ellenoriz_generalas.py <fájl>`
3. ✅ Ha van hiba, kérj javítást az AI-tól

**⚠️ FONTOS:** Az AI_PROMPT_SABLON.txt tartalmazza az automatikus ellenőrzési mechanizmust, így az AI-nak AUTOMATIKUSAN hibamentes szöveget kell generálnia!

---

## ❓ GYAKORI KÉRDÉSEK:

**Q: Kell-e a KRITIKUS_SZABALYOK_ROVID.txt az AI-nak?**  
A: NEM! Az AI_PROMPT_SABLON.txt már tartalmazza mindent.

**Q: Kell-e az ELOTTE_ELLENORIZD_MINDIG.txt az AI-nak?**  
A: NEM! Ez csak neked kell, amikor ellenőrzöd a generált szöveget.

**Q: Melyik fájlt másoljam be az AI-ba?**  
A: Csak az **AI_PROMPT_SABLON.txt**-t! Ez tartalmazza mindent.

**Q: Miért van akkor 4 külön fájl?**  
A: 
- **AI_PROMPT_SABLON.txt** = AI-nak (generáláshoz)
- **KRITIKUS_SZABALYOK_ROVID.txt** = Neked (gyors áttekintéshez)
- **ELOTTE_ELLENORIZD_MINDIG.txt** = Neked (ellenőrzéshez)
- **HASZNALATI_UTASITAS.md** = Neked (útmutató)

---

## ✅ ÖSSZEFOGLALÁS:

**AI-nak kell:**
- ✅ AI_PROMPT_SABLON.txt (EZ AZ EGYETLEN!)

**Neked kell:**
- ✅ KRITIKUS_SZABALYOK_ROVID.txt (gyors áttekintés)
- ✅ ELOTTE_ELLENORIZD_MINDIG.txt (ellenőrzés)
- ✅ HASZNALATI_UTASITAS.md (útmutató)

**Egyszerűen:** Csak az **AI_PROMPT_SABLON.txt**-t másold be az AI-ba, a többi neked kell!

