# Hogyan használd a promptokat, hogy ne legyenek hibák?

## ⚠️ FONTOS: MELYIK FÁJLT HASZNÁLD?

**AI-nak kell (generáláshoz):**
- ✅ **AI_PROMPT_SABLON.txt** - Ezt másold be az AI-ba! (EZ AZ EGYETLEN!)

**Neked kell (ellenőrzéshez):**
- ✅ **KRITIKUS_SZABALYOK_ROVID.txt** - Gyors áttekintéshez
- ✅ **ELOTTE_ELLENORIZD_MINDIG.txt** - Részletes ellenőrzéshez
- ✅ **HASZNALATI_UTASITAS.md** - Ez a fájl (útmutató)

**Lásd:** `FILEK_SZEREPE.md` részletesebb magyarázathoz!

---

## A probléma
A részletes prompt túl hosszú, és a kritikus szabályok elvésznek benne. Ezért mégis előfordulnak logikátlan hibák.

## A megoldás

### 1. MINDEN generálás ELŐTT:
**MÁSOLD BE AZ `AI_PROMPT_SABLON.txt` FÁJLT AZ AI-BA!**
Ez tartalmazza MINDENT, amit az AI-nak tudnia kell.

### 2. MINDEN generálás UTÁN:
**FUTTASD AZ `ellenoriz_generalas.py` SCRIPTET!**

```bash
python script/ellenoriz_generalas.py "Tételek/podcast/fájl_neve.txt"
```

Ez automatikusan ellenőrzi:
- ❌ TILOS tárgyak (tükör, kristály, üveg, gömb)
- ❌ Lehetetlen cselekmények (deszka pulzál, fémlemezből golyó gurul)
- ⚠️ Túl hosszú leírások
- ⚠️ Absztrakt kifejezések

### 3. MINDEN mondatnál kérdezd meg magadtól:

1. **"Ez logikus? Lehetséges a valóságban?"**
   - ✅ JÓ: "lámpa kigyullad", "golyó gurul"
   - ❌ ROSSZ: "deszka pulzál", "fémlemezből golyó gurul"

2. **"Ez a tárgy valós? Konkrét? Nem absztrakt?"**
   - ✅ JÓ: "fogaskerék", "mérleg", "lámpa"
   - ❌ ROSSZ: "mechanizmus", "szerkezet", "tükör"

3. **"Ez a cselekmény lehetséges? Ez a tárgy ezt tudja csinálni?"**
   - ✅ JÓ: "lámpa kigyullad", "golyó gurul"
   - ❌ ROSSZ: "deszka pulzál", "pecsét pulzál"

4. **"Van benne tilos tárgy (tükör, kristály, üveg, gömb)?"**
   - Ha igen → cseréld ki lámpára, fémlemezre, stb.

5. **"A tárgy tulajdonságai kapcsolódnak a tananyaghoz?"**
   - ✅ JÓ: "két szintből álló piramis" (ha van "két szint" a tananyagban)
   - ❌ ROSSZ: "fekete tolmácsgép" (ha nincs "fekete" a tananyagban)

6. **"A leírás tömör? Maximum 2-3 szó?"**
   - ✅ JÓ: "tolmácsgép", "mérleg"
   - ❌ ROSSZ: "fekete fémből készült, precíziós tolmácsgép"

7. **"Az ok-okozati lánc folyamatos? Nem szakad meg?"**
   - ✅ JÓ: "golyó eléri a kockát, és amikor eléri, a rugó összenyomódik"
   - ❌ ROSSZ: "golyó eléri a kockát." [új bekezdés] "Ez a korrekciós funkció?"

## Munkafolyamat

1. **Generálás előtt:**
   - ✅ Másold be: `AI_PROMPT_SABLON.txt` az AI-ba
   - ✅ Add hozzá a tételt
   - (Opcionális: Olvasd el `KRITIKUS_SZABALYOK_ROVID.txt`-t, hogy megértsd a szabályokat)

2. **Generálás:**
   - Az AI generálja a szöveget
   - (Az AI_PROMPT_SABLON.txt már tartalmazza a kritikus szabályokat, az AI automatikusan ellenőrzi)

3. **Generálás után:**
   - ✅ Ellenőrizd kézzel (használd: `ELOTTE_ELLENORIZD_MINDIG.txt` checklistként)
   - ✅ Vagy futtasd: `python script/ellenoriz_generalas.py <fájl>`
   - ✅ Javítsd ki az összes hibát
   - ✅ Ismételd az ellenőrzést, amíg nincs hiba

## Fontos!

**NE generálj szöveget anélkül, hogy először elolvasnád a kritikus szabályokat!**

**NE fejezd be a generálást anélkül, hogy ellenőriznéd a scripttel!**

**NE engedj el egyetlen logikátlan mondatot sem!**

## Példa hibák és javítások

| ❌ ROSSZ | ✅ JÓ |
|---------|------|
| "deszka pulzálnak" | "deszka mellett lámpák vannak, amelyek pulzálnak" |
| "fémlemezből golyó gurul" | "golyó kiesik a dobozból" |
| "törött fémlemez" | "lehajlított fémlemez" vagy "törött deszka" |
| "fekete tolmácsgép" (ha nincs "fekete" a tananyagban) | "tolmácsgép" |
| "golyó eléri a kockát." [új bekezdés] | "golyó eléri a kockát, és amikor eléri, a rugó..." |

## Ha mégis hiba van:

1. Nézd meg, hogy elolvastad-e a `KRITIKUS_SZABALYOK_ROVID.txt` fájlt
2. Futtasd az `ellenoriz_generalas.py` scriptet
3. Javítsd ki az összes hibát
4. Frissítsd a promptot, ha új típusú hiba van

