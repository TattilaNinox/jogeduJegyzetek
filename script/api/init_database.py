#!/usr/bin/env python3
"""
Adatbázis inicializáló script
A meglévő template jogeseteket JSON formátumba konvertálja és több variációt hoz létre.
"""

import json
from pathlib import Path
from jogeset_db import JogesetDatabase

# Template jogesetek a meglévő kódból
TEMPLATE_JOGESETEK = {
    "6:519": {
        "kategoria": "kártérítés",
        "jogesetek": [
            {
                "id": 1,
                "cim": "Károkozás autóbalesetben",
                "tenyek": """2024. március 15-én, délután 14:30-kor Budapesten, a Rákóczi úton történt egy közúti baleset.

Kovács János (45 éves, Budapest) személygépkocsijával haladt a Rákóczi úton, amikor a piros lámpánál nem állt meg, és beleütközött Nagy Mária (32 éves, Szeged) autójába, aki a zöld lámpánál haladt át a kereszteződésen.

A baleset következményei:
- Nagy Mária autójának eleje jelentős mértékben megsérült
- A javítási költség 850.000 Ft
- Nagy Mária 3 napig nem tudta használni az autóját, ezért bérleti díjat kellett fizetnie (15.000 Ft/nap = 45.000 Ft)
- A baleset miatt késedelmi kamat is keletkezett

Kovács János azt állítja, hogy nem ő okozta a balesetet, mert Nagy Mária nem figyelt elég körültekintően.""",
                "kerdes": "Következik-e Kovács Jánosnak kártérítési kötelezettsége Nagy Mária kárának megtérítésére? Ha igen, mekkora összegben?",
                "megoldas": """A Ptk. 6:519. § (1) bekezdése szerint: "A károkozó köteles megtéríteni a kárt, ha nem bizonyítja, hogy a kár nem az ő hibájából következett be."

Esetünkben:
1. Károkozás: Kovács János piros lámpánál nem állt meg, és ütközést okozott
2. Kár: Nagy Mária autójának sérülése (850.000 Ft javítási költség)
3. Elmaradt haszon: 3 napos autóbérleti költség (45.000 Ft)
4. Összes kár: 895.000 Ft

Kovács János nem tudta bizonyítani, hogy a kár nem az ő hibájából következett be (sőt, ő volt a piros lámpánál), ezért köteles megtéríteni a teljes kárt.

Következtetés: Kovács János köteles megtéríteni Nagy Mária 895.000 Ft kárát.""",
                "komplexitas": "közepes"
            },
            {
                "id": 2,
                "cim": "Károkozás gyalogosnak",
                "tenyek": """2024. április 20-án, reggel 8:00-kor Debrecenben, a Piac utcán történt egy baleset.

Szabó Péter (28 éves, Debrecen) kerékpárral haladt, amikor nem figyelt elég körültekintően és beleütközött Tóth Éva (55 éves, Debrecen) gyalogosba, aki a járdán sétált.

A baleset következményei:
- Tóth Éva elest és megsérült a bokája
- Orvosi kezelési költség: 120.000 Ft
- 2 hétig nem tudott dolgozni, elmaradt jövedelem: 280.000 Ft
- Fájdalomdíj: 50.000 Ft

Szabó Péter azt állítja, hogy Tóth Éva váratlanul lépett elé, ezért nem ő a felelős.""",
                "kerdes": "Következik-e Szabó Péternek kártérítési kötelezettsége?",
                "megoldas": """A Ptk. 6:519. § szerint a károkozó köteles megtéríteni a kárt, ha nem bizonyítja, hogy a kár nem az ő hibájából következett be.

Esetünkben:
1. Károkozás: Szabó Péter kerékpárral ütközött Tóth Évába
2. Kár: Orvosi kezelés (120.000 Ft) + elmaradt jövedelem (280.000 Ft) + fájdalomdíj (50.000 Ft) = 450.000 Ft
3. Felelősség: Szabó Péter nem tudta bizonyítani, hogy nem az ő hibája volt

Következtetés: Szabó Péter köteles megtéríteni Tóth Éva 450.000 Ft kárát.""",
                "komplexitas": "közepes"
            },
            {
                "id": 3,
                "cim": "Károkozás lakásban - vízszivárgás",
                "tenyek": """2024. február 10-én Budapesten, a VIII. kerületben történt egy vízszivárgás.

Kiss András (40 éves) lakásában elromlott a mosogatógép csatlakozása, és víz szivárgott le az alatta lévő lakásba, ahol Horváth Zsuzsa (35 éves) lakik.

A kár:
- Horváth Zsuzsa lakásának mennyezete és falai megsérültek
- Bútorok károsodtak
- Javítási költség: 1.200.000 Ft
- Ideiglenes lakhatás költsége: 200.000 Ft

Kiss András azt állítja, hogy nem tudhatta, hogy a csatlakozás elromlott, ezért nem felelős.""",
                "kerdes": "Következik-e Kiss Andrásnak kártérítési kötelezettsége?",
                "megoldas": """A Ptk. 6:519. § szerint a károkozó köteles megtéríteni a kárt, ha nem bizonyítja, hogy a kár nem az ő hibájából következett be.

Esetünkben:
1. Károkozás: Kiss András lakásából víz szivárgott le
2. Kár: 1.200.000 Ft javítás + 200.000 Ft ideiglenes lakhatás = 1.400.000 Ft
3. Felelősség: Kiss András nem tudta bizonyítani, hogy nem az ő hibája volt

Következtetés: Kiss András köteles megtéríteni Horváth Zsuzsa 1.400.000 Ft kárát.""",
                "komplexitas": "komplex"
            }
        ]
    },
    "4:15": {
        "kategoria": "házasság",
        "jogesetek": [
            {
                "id": 1,
                "cim": "Házasság érvénytelenítési per indítása",
                "tenyek": """2023. június 10-én, Budapesten, Kovács Péter (22 éves) és Nagy Anna (17 éves) házasságot kötöttek.

A tények:
- Kovács Péter: 22 éves, nagykorú
- Nagy Anna: 17 éves, kiskorú, a gyámhatóság engedélye nélkül kötötte a házasságot
- A házasságkötéskor Anna még nem töltötte be a 18. életévét
- A házasság 2023. június 10-én köttetett meg

2024. január 15-én, miután Anna betöltötte a 18. életévét (2024. január 1.), Kovács Péter el akarja indítani a házasság érvénytelenítési pert, mert azt állítja, hogy a házasság érvénytelen volt, mert Anna kiskorú volt és nem volt gyámhatósági engedély.

Nagy Anna ellenben azt állítja, hogy a házasság érvényes, mert már betöltötte a 18. életévét.""",
                "kerdes": "Ki jogosult a házasság érvénytelenítési perének indítására? Érvényes-e a házasság?",
                "megoldas": """A Ptk. 4:15. § szerint az érvénytelenítési pert a házasság fennállása alatt és a házasság megszűnése után is meg lehet indítani.

Esetünkben:
1. Házasságkötés: 2023. június 10., Anna még kiskorú volt (17 éves)
2. Gyámhatósági engedély: Nem volt gyámhatósági engedély a házasságkötéshez
3. Nagykorúság elérése: Anna 2024. január 1-én töltötte be a 18. életévét
4. Perindítási szándék: 2024. január 15-én, 14 nappal a nagykorúság elérése után

A Ptk. 4:16. § (1) bekezdése szerint: "A nagykorúság elérése után a házasságkötési engedély hiányában a kiskorúság miatt... az a házastárs jogosult érvénytelenítési per indítására, akinek személyében az érvénytelenség oka megvalósult."

Esetünkben Anna személyében valósult meg az érvénytelenség oka (kiskorúság, engedély hiánya), ezért ő jogosult a per indítására. A pert a nagykorúság elérésétől számított hat hónapon belül lehet megindítani.

Következtetés: Nagy Anna jogosult a házasság érvénytelenítési perének indítására, mert ő az, akinek személyében az érvénytelenség oka megvalósult. A perindítási határidő: 2024. január 1-től számított 6 hónap (2024. július 1-ig).""",
                "komplexitas": "komplex"
            },
            {
                "id": 2,
                "cim": "Házasság érvénytelenítés fennálló házasság miatt",
                "tenyek": """2023. szeptember 5-én Szegeden, Tóth István (30 éves) és Varga Mária (28 éves) házasságot kötöttek.

Azonban később kiderült, hogy Tóth Istvánnak már volt egy korábbi házassága, amelyet 2023. augusztus 20-án bontottak fel, de a bírósági határozat csak 2023. szeptember 10-én lépett hatályba.

Varga Mária 2024. március 1-én szeretné érvényteleníttetni a házasságot, mert azt állítja, hogy a házasságkötéskor Tóth Istvánnak még fennállt a korábbi házassága.""",
                "kerdes": "Érvénytelen-e a házasság? Ki jogosult az érvénytelenítési per indítására?",
                "megoldas": """A Ptk. 4:13. § (1) bekezdése szerint: "Érvénytelen a házasság, ha a házasulók valamelyikének korábbi házassága fennáll."

A Ptk. 4:15. § szerint az érvénytelenítési pert bármelyik házastárs, az ügyész vagy az jogosult indíthatja meg, akinek a házasság érvénytelenségének megállapításához jogi érde jogi érdeke fűződik.

Esetünkben:
1. Házasságkötés: 2023. szeptember 5.
2. Korábbi házasság felbontása: 2023. augusztus 20., de hatálybalépés: 2023. szeptember 10.
3. Következés: A házasságkötéskor (szeptember 5.) még fennállt a korábbi házasság

Következtetés: A házasság érvénytelen, mert a házasságkötéskor Tóth Istvánnak még fennállt a korábbi házassága. Varga Mária, Tóth István, vagy az ügyész indíthat érvénytelenítési pert.""",
                "komplexitas": "közepes"
            }
        ]
    },
    "6:1": {
        "kategoria": "szerződés",
        "jogesetek": [
            {
                "id": 1,
                "cim": "Adás-vételi szerződés megkötése és teljesítése",
                "tenyek": """2024. január 10-én Budapesten, Kovács Péter (eladó) és Szabó Anna (vevő) adás-vételi szerződést kötöttek egy használt laptop eladásáról.

A szerződés tartalma:
- Eladó: Kovács Péter
- Vevő: Szabó Anna
- Tárgy: Dell Latitude 5520 laptop számítógép
- Vételár: 250.000 Ft
- Átadás: 2024. január 15-én
- Fizetés: átadáskor, készpénzben

2024. január 15-én Kovács Péter átadta a laptopot Szabó Annának, aki azonban csak 200.000 Ft-ot fizetett, mondván, hogy a laptop állapota rosszabb, mint amit ígért.

Kovács Péter követeli a maradék 50.000 Ft kifizetését.""",
                "kerdes": "Követelheti-e Kovács Péter a maradék 50.000 Ft-ot? Milyen jogkövetkezményekkel jár ez az eset?",
                "megoldas": """A Ptk. 6:1. § szerint a szerződés a felek megállapodása, amely kötelezettségeket keletkeztet.

Esetünkben:
1. Szerződés létrejötte: 2024. január 10-én megkötötték az adás-vételi szerződést
2. Kötelezettségek:
   - Kovács Péter: laptop átadása
   - Szabó Anna: 250.000 Ft fizetése
3. Teljesítés: Kovács Péter átadta a laptopot, de Szabó Anna csak részben fizetett

A szerződés szerint Szabó Anna köteles volt 250.000 Ft-ot fizetni. Ha a laptop állapota valóban rosszabb, mint amit ígértek, akkor Szabó Anna a szerződésszegés vagy a reklamáció jogát érvényesítheti, de ez nem mentesíti a teljes vételár fizetési kötelezettsége alól.

Következtetés: Kovács Péter követelheti a maradék 50.000 Ft-ot, hacsak Szabó Anna nem bizonyítja, hogy a szerződés megsértése miatt csökkent a vételár.""",
                "komplexitas": "közepes"
            },
            {
                "id": 2,
                "cim": "Szerződés létrejötte - ajánlat és elfogadás",
                "tenyek": """2024. február 1-én, Szegeden, Kovács Márk (eladó) emailben ajánlatot tett Nagy Péternek (vevő) egy használt autó eladására.

Az ajánlat tartalma:
- Autó: 2018-as Volkswagen Golf
- Ár: 3.500.000 Ft
- Ajánlat érvényessége: 2024. február 5-ig

Nagy Péter 2024. február 3-án emailben elfogadta az ajánlatot, de 3.400.000 Ft-ot ajánlott.

Kovács Márk azt állítja, hogy ez nem elfogadás, hanem új ajánlat, ezért nincs szerződés.""",
                "kerdes": "Létrejött-e a szerződés? Mi a helyzet?",
                "megoldas": """A Ptk. 6:1. § szerint a szerződés a felek megállapodása. A szerződés létrejötte az ajánlat és az elfogadás egybehangzásával történik.

Esetünkben:
1. Ajánlat: Kovács Márk 3.500.000 Ft-ot ajánlott
2. Válasz: Nagy Péter 3.400.000 Ft-ot ajánlott

Ez nem elfogadás, hanem új ajánlat (ellentétes ajánlat), mert az ár eltér.

Következtetés: Nem jött létre szerződés, mert nincs egybehangzás az ajánlat és az elfogadás között. Nagy Péter válasza új ajánlat, amit Kovács Márk elfogadhat vagy elutasíthat.""",
                "komplexitas": "egyszerű"
            }
        ]
    }
}


def init_database():
    """Inicializálja az adatbázist a template jogesetekkel"""
    db = Path(__file__).parent
    db_path = script / "jogesetek_db"
    db = JogesetDatabase(db_path)
    
    print("="*60)
    print("JOGESET ADATBÁZIS INICIALIZÁLÁSA")
    print("="*60)
    print()
    
    for paragrafus, data in TEMPLATE_JOGESETEK.items():
        kategoria = data["kategoria"]
        jogesetek = data["jogesetek"]
        
        print(f"Feldolgozás: {paragrafus} ({kategoria})")
        print(f"  Jogesetek száma: {len(jogesetek)}")
        
        # Minden jogesetet hozzáadjuk
        for jogeset in jogesetek:
            db.add_jogeset(paragrafus, kategoria, jogeset)
        
        print(f"  ✓ Mentve")
        print()
    
    print("="*60)
    print("ADATBÁZIS INICIALIZÁLÁSA KÉSZ!")
    print("="*60)
    print(f"\nAdatbázis helye: {db_path}")
    print(f"\nElérhető paragrafusok:")
    paragrafusok = db.list_paragrafusok()
    for p in paragrafusok:
        print(f"  - {p}")


if __name__ == "__main__":
    init_database()

