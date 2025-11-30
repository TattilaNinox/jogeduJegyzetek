# Dialógus Voice Tag Hozzáadó Script Használata

Ez a script átalakítja a dialógus fájlokat úgy, hogy a `MENTOR:` és `TANULÓ:` címkéket eltávolítja, és a megfelelő voice tag-ek közé helyezi a szövegeket.

## Előkészítés

1. Nyisd meg a `dialogus_voice_tag_hozzaado.py` fájlt
2. A script elején, a **BEÁLLÍTÁSOK** részben módosítsd a voice tag-eket:

```python
# Mentor voice tag-ek
MENTOR_VOICE_START = '<voice voice-id="..." speaker-id="..." language="hu" seed="...">'
MENTOR_VOICE_END = '</voice>'

# Tanuló voice tag-ek
TANULO_VOICE_START = '<voice voice-id="..." speaker-id="..." language="hu" seed="...">'
TANULO_VOICE_END = '</voice>'
```

## Használat

### Alapvető használat (felülírja az eredeti fájlt)

```bash
python script/dialogus_voice_tag_hozzaado.py Tételek/podcast/dialogus.txt
```

### Kimeneti fájl megadása (nem írja felül az eredetit)

```bash
python script/dialogus_voice_tag_hozzaado.py Tételek/podcast/dialogus.txt Tételek/podcast/dialogus_atalakított.txt
```

## Bemeneti fájl formátuma

A script olyan fájlokat vár, ahol a sorok így néznek ki:

```
MENTOR: Szia! Ma a polgári jog alapelveiről szeretnék beszélni.
TANULÓ: Értem, tehát ez az épület maga a polgári jogi alapelvek struktúráját reprezentálja.
MENTOR: Pontosan. Az üvegtáblán látható...
```

## Kimeneti fájl formátuma

A script átalakítja a fájlt így:

```xml
<voice voice-id="3af57f25-0c84-4202-9381-47f013458d29" speaker-id="c5680bed-a453-402e-a95b-ebef56707136" language="hu" seed="f07dddb4-6af4-4132-8379-50ee5e1c80a7">
Szia! Ma a polgári jog alapelveiről szeretnék beszélni.
</voice>

<voice voice-id="f99a416d-6943-4541-90c6-8ea0b282e39a" speaker-id="8a67d393-1ff8-41eb-a7d6-e7641c8cf9b3" language="hu" seed="8023d092-d0b2-4b00-8034-5102eec293d9">
Értem, tehát ez az épület maga a polgári jogi alapelvek struktúráját reprezentálja.
</voice>
```

## Példa

```bash
# Átalakítjuk a fájlt (felülírja az eredetit)
python script/dialogus_voice_tag_hozzaado.py Tételek/podcast/A_polgari_jog_alapelvei_joggal_valo_visszaeles_teljes_dialogus.txt

# Vagy új fájlba mentjük
python script/dialogus_voice_tag_hozzaado.py Tételek/podcast/dialogus.txt Tételek/podcast/dialogus_voice_tagokkal.txt
```

## Megjegyzések

- A script UTF-8 kódolású fájlokat kezel
- Az üres sorok megmaradnak
- Ha a sor nem kezdődik `MENTOR:` vagy `TANULÓ:` címkével, akkor változatlanul marad
- A script biztonságosan kezeli a hibákat és értesít, ha valami nem stimmel


