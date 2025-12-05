#!/usr/bin/env python3
"""
Jogeset Generátor - Fiktív jogesetek generálása jogszabályok alapján

Ez a szkript lehetővé teszi, hogy egy adott jogszabály (vagy jogszabály részlet) alapján
fiktív, de reális jogeseteket generáljunk tanulási vagy gyakorlási célokra.

Használat:
    python jogeset_generator.py --jogszabaly "Ptk. 6:519. §" --szoveg "jogszabaly_szoveg.txt"
    python jogeset_generator.py --interaktiv
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Figyelem: az openai könyvtár nincs telepítve. Telepítés: pip install openai")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


@dataclass
class Jogeset:
    """Jogeset struktúra"""
    cim: str
    tenyek: str  # A tényállás részletes leírása
    kerdes: str  # A jogi kérdés
    alkalmazando_jogszabaly: str  # Melyik jogszabály vonatkozik
    megoldas: str  # A jogi megoldás/elemzés
    komplexitas: str  # "egyszerű", "közepes", "komplex"
    kategoria: str  # pl. "szerződés", "kártérítés", "tulajdonjog"


class JogszabalyElemzo:
    """Jogszabály elemző és strukturáló osztály"""
    
    def __init__(self, jogszabaly_szoveg: str):
        self.jogszabaly_szoveg = jogszabaly_szoveg
        self.paragrafus_szam = self._kinyer_paragrafus_szam()
        self.kulcsszavak = self._kinyer_kulcsszavak()
        self.joghatasok = self._kinyer_joghatasok()
    
    def _kinyer_paragrafus_szam(self) -> Optional[str]:
        """Kinyeri a paragrafus számot a szövegből"""
        import re
        # Ptk. 6:519. § vagy 6:519. § vagy 6:519.§ formátum keresése
        # Különböző formátumok: "6:519. §", "6:519§", "Ptk. 6:519. §"
        patterns = [
            r'(?:Ptk\.\s*)?(\d+:\d+\.?\s*§)',  # Standard formátum
            r'(\d+:\d+)\s*§',  # Szóköz nélküli pont
            r'(\d+:\d+)\.?\s*§',  # Ponttal vagy anélkül
        ]
        for pattern in patterns:
            match = re.search(pattern, self.jogszabaly_szoveg)
            if match:
                return match.group(1) + ". §" if not match.group(1).endswith("§") else match.group(1)
        return None
    
    @staticmethod
    def kinyer_paragrafus_fajlbol(fajl_szoveg: str, paragrafus_szam: str) -> Optional[str]:
        """Kinyeri egy adott paragrafust a teljes jogszabály fájlból"""
        import re
        
        # Normalizáljuk a paragrafus számot (pl. "6:519" -> "6:519")
        # Eltávolítjuk a "Ptk." előtagot és a "§" jelet, ha van
        paragrafus_szam = paragrafus_szam.replace("Ptk.", "").replace("§", "").strip()
        if paragrafus_szam.endswith("."):
            paragrafus_szam = paragrafus_szam[:-1]
        
        # A fájlban a formátum: "6:519. § [Címke]" vagy "6:519. §" majd tartalom
        # Keresési minta: paragrafus szám + pont + szóköz + § + opcionális címke + tartalom
        # Amíg nem jön következő paragrafus (pl. "6:520. §")
        
        # Escape-elt verzió a kereséshez
        paragrafus_escaped = re.escape(paragrafus_szam)
        
        # Keresési minta: "6:519. §" vagy "6:519. § [Címke]" formátum
        # A fájlban lehet szóköz vagy speciális karakter a pont és § között: "4:15. §" vagy "4:15. §"
        # Aztán minden tartalom, amíg nem jön következő paragrafus
        # Próbáljuk több mintával is
        
        # Első próbálkozás: pontos formátum "4:15. §" vagy "4:15. § [Címke]"
        pattern1 = rf'{paragrafus_escaped}\.\s*§(?:\s*\[.*?\])?\s*(.*?)(?=\d+:\d+\.\s*§|$)'
        match = re.search(pattern1, fajl_szoveg, re.DOTALL | re.IGNORECASE)
        
        # Ha nem találta, próbáljuk meg anélkül, hogy a pont után szóköz legyen
        if not match:
            pattern2 = rf'{paragrafus_escaped}\.\s*§\s*(.*?)(?=\d+:\d+\.\s*§|$)'
            match = re.search(pattern2, fajl_szoveg, re.DOTALL | re.IGNORECASE)
        
        # Ha még mindig nem találta, próbáljuk meg anélkül, hogy a § előtt szóköz legyen
        if not match:
            pattern3 = rf'{paragrafus_escaped}\.§\s*(.*?)(?=\d+:\d+\.\s*§|$)'
            match = re.search(pattern3, fajl_szoveg, re.DOTALL | re.IGNORECASE)
        if match:
            # Visszaadjuk a teljes paragrafust (szám + tartalom)
            start_pos = match.start()
            end_pos = match.end()
            paragrafus_teljes = fajl_szoveg[start_pos:end_pos].strip()
            
            # Ha túl rövid, próbáljuk meg több sort is
            if len(paragrafus_teljes) < 100:
                # Keressük meg a következő paragrafust
                kovetkezo_pattern = r'\d+:\d+\.\s*§'
                kovetkezo_match = re.search(kovetkezo_pattern, fajl_szoveg[end_pos:end_pos+10000], re.IGNORECASE)
                if kovetkezo_match:
                    # Vegyük a tartalmat a jelenlegi és következő paragrafus között
                    end_pos_final = end_pos + kovetkezo_match.start()
                    paragrafus_teljes = fajl_szoveg[start_pos:end_pos_final].strip()
            
            return paragrafus_teljes
        
        # Második próbálkozás: egyszerűbb minta (csak a szám része)
        pattern2 = rf'{paragrafus_escaped}.*?(?=\d+:\d+\.\s*§|$)'
        match2 = re.search(pattern2, fajl_szoveg, re.DOTALL | re.IGNORECASE)
        if match2:
            return match2.group(0).strip()
        
        return None
    
    def _kinyer_kulcsszavak(self) -> List[str]:
        """Kinyeri a kulcsszavakat a jogszabályból"""
        kulcsszavak = []
        # Gyakori jogi kulcsszavak keresése
        jogi_kulcsszavak = [
            'köteles', 'jogosult', 'kötelme', 'jog', 'kötelezettség',
            'szerződés', 'kártérítés', 'tulajdonjog', 'birtok',
            'jogviszony', 'jogi tény', 'joghatás', 'érvénytelen',
            'semmis', 'megtámadható', 'teljesítés', 'felmondás'
        ]
        
        szoveg_lower = self.jogszabaly_szoveg.lower()
        for kulcsszo in jogi_kulcsszavak:
            if kulcsszo in szoveg_lower:
                kulcsszavak.append(kulcsszo)
        
        return kulcsszavak
    
    def _kinyer_joghatasok(self) -> List[str]:
        """Kinyeri a joghatásokat (keletkezés, módosítás, megszűnés)"""
        joghatasok = []
        szoveg_lower = self.jogszabaly_szoveg.lower()
        
        if any(szo in szoveg_lower for szo in ['keletkezik', 'létrejön', 'jön létre']):
            joghatasok.append('keletkezés')
        if any(szo in szoveg_lower for szo in ['módosul', 'változik', 'módosít']):
            joghatasok.append('módosítás')
        if any(szo in szoveg_lower for szo in ['megszűnik', 'szűnik meg', 'lejár']):
            joghatasok.append('megszűnés')
        
        return joghatasok if joghatasok else ['keletkezés']  # Alapértelmezett
    
    def strukturalt_leiras(self) -> Dict:
        """Visszaadja a strukturált leírást"""
        return {
            'paragrafus': self.paragrafus_szam,
            'kulcsszavak': self.kulcsszavak,
            'joghatasok': self.joghatasok,
            'teljes_szoveg': self.jogszabaly_szoveg[:500] + '...' if len(self.jogszabaly_szoveg) > 500 else self.jogszabaly_szoveg
        }


class LLMGenerator:
    """LLM alapú jogeset generátor"""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self._initialize_provider()
    
    def _get_api_key(self) -> Optional[str]:
        """API kulcs lekérése környezeti változókból"""
        import os
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        return None
    
    def _initialize_provider(self):
        """Inicializálja a megfelelő LLM szolgáltatót"""
        if self.provider == "openai" and OPENAI_AVAILABLE:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY környezeti változó nincs beállítva")
            openai.api_key = self.api_key
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY környezeti változó nincs beállítva")
            self.client = Anthropic(api_key=self.api_key)
        elif self.provider == "gemini" and GEMINI_AVAILABLE:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY környezeti változó nincs beállítva")
            genai.configure(api_key=self.api_key)
        else:
            print(f"Figyelem: {self.provider} provider nem elérhető vagy nincs API kulcs")
    
    def generate_jogeset(self, jogszabaly_elemzo: JogszabalyElemzo, 
                       komplexitas: str = "közepes",
                       kategoria: Optional[str] = None) -> Jogeset:
        """Generál egy jogesetet a megadott jogszabály alapján"""
        
        prompt = self._create_prompt(jogszabaly_elemzo, komplexitas, kategoria)
        
        if self.provider == "openai" and OPENAI_AVAILABLE:
            response = self._generate_openai(prompt)
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            response = self._generate_anthropic(prompt)
        elif self.provider == "gemini" and GEMINI_AVAILABLE:
            response = self._generate_gemini(prompt)
        else:
            # Fallback: egyszerű template alapú generálás
            print("⚠ Figyelem: Template mód használata - csak példa jogesetek generálódnak.")
            print("   Valódi, részletes jogesethez használj LLM szolgáltatót (--provider openai/anthropic/gemini)")
            response = self._generate_template_based(jogszabaly_elemzo, komplexitas, kategoria)
        
        return self._parse_response(response, jogszabaly_elemzo, komplexitas, kategoria)
    
    def _create_prompt(self, elemzo: JogszabalyElemzo, komplexitas: str, kategoria: Optional[str]) -> str:
        """Létrehozza a promptot a jogeset generálásához"""
        
        prompt = f"""Te egy tapasztalt jogász vagy, aki fiktív, de reális jogeseteket készít tanulási célokra.

FELADAT: Hozz létre egy {komplexitas} komplexitású jogesetet a következő jogszabály alapján:

JOGSZABÁLY:
{elemzo.jogszabaly_szoveg}

PARAGRAFUS: {elemzo.paragrafus_szam or 'Ismeretlen'}
KULCSSZAVAK: {', '.join(elemzo.kulcsszavak) if elemzo.kulcsszavak else 'Nincs'}
JOGHATÁSOK: {', '.join(elemzo.joghatasok)}

{'KATEGÓRIA: ' + kategoria if kategoria else ''}

A jogesetnek tartalmaznia kell:

1. CÍM: Egy rövid, beszédes cím (pl. "Károkozás autóbalesetben")
2. TÉNYÁLLÁS: Részletes, konkrét tények leírása (személyek nevei, dátumok, események)
3. JOGI KÉRDÉS: Mi a jogi probléma, amit meg kell oldani?
4. ALKALMAZANDÓ JOGSZABÁLY: Melyik jogszabály vonatkozik erre az esetre?
5. MEGOLDÁS: Részletes jogi elemzés és megoldás

A jogeset legyen:
- Reális és hiteles
- Konkrét tényekkel (nevek, dátumok, helyszínek)
- Jogi szempontból helyes
- Tanulási célokra alkalmas
- Magyarországi polgári jogi környezetben játszódjon

Válaszolj JSON formátumban a következő struktúrával:
{{
    "cim": "...",
    "tenyek": "...",
    "kerdes": "...",
    "alkalmazando_jogszabaly": "...",
    "megoldas": "..."
}}
"""
        return prompt
    
    def _generate_openai(self, prompt: str) -> str:
        """OpenAI API használata"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Te egy tapasztalt magyar jogász vagy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Hiba OpenAI API hívásnál: {e}")
            return ""
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Anthropic Claude API használata"""
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Hiba Anthropic API hívásnál: {e}")
            return ""
    
    def _generate_gemini(self, prompt: str) -> str:
        """Google Gemini API használata"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Hiba Gemini API hívásnál: {e}")
            return ""
    
    def _generate_template_based(self, elemzo: JogszabalyElemzo, 
                                 komplexitas: str, kategoria: Optional[str]) -> Dict:
        """Template alapú generálás LLM nélkül (fallback) - részletes példa jogesetekkel"""
        
        paragrafus = elemzo.paragrafus_szam or "ismeretlen"
        kategoria_lower = (kategoria or "általános").lower()
        
        # Kategória-specifikus példa jogesetek
        template_jogesetek = {
            "kártérítés": {
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
                "megoldas": f"""A Ptk. {paragrafus} § (1) bekezdése szerint: "A károkozó köteles megtéríteni a kárt, ha nem bizonyítja, hogy a kár nem az ő hibájából következett be."

Esetünkben:
1. Károkozás: Kovács János piros lámpánál nem állt meg, és ütközést okozott
2. Kár: Nagy Mária autójának sérülése (850.000 Ft javítási költség)
3. Elmaradt haszon: 3 napos autóbérleti költség (45.000 Ft)
4. Összes kár: 895.000 Ft

Kovács János nem tudta bizonyítani, hogy a kár nem az ő hibájából következett be (sőt, ő volt a piros lámpánál), ezért köteles megtéríteni a teljes kárt.

Következtetés: Kovács János köteles megtéríteni Nagy Mária 895.000 Ft kárát."""
            },
            "szerződés": {
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
                "megoldas": f"""A Ptk. {paragrafus} § szerint a szerződés a felek megállapodása, amely kötelezettségeket keletkeztet.

Esetünkben:
1. Szerződés létrejötte: 2024. január 10-én megkötötték az adás-vételi szerződést
2. Kötelezettségek:
   - Kovács Péter: laptop átadása
   - Szabó Anna: 250.000 Ft fizetése
3. Teljesítés: Kovács Péter átadta a laptopot, de Szabó Anna csak részben fizetett

A szerződés szerint Szabó Anna köteles volt 250.000 Ft-ot fizetni. Ha a laptop állapota valóban rosszabb, mint amit ígértek, akkor Szabó Anna a szerződésszegés vagy a reklamáció jogát érvényesítheti, de ez nem mentesíti a teljes vételár fizetési kötelezettsége alól.

Következtetés: Kovács Péter követelheti a maradék 50.000 Ft-ot, hacsak Szabó Anna nem bizonyítja, hogy a szerződés megsértése miatt csökkent a vételár."""
            },
            "tulajdonjog": {
                "cim": "Ingatlan tulajdonjog átruházása",
                "tenyek": """2023. november 20-án, Budapesten, Tóth István (eladó) és Varga Éva (vevő) adás-vételi szerződést kötöttek egy budapesti lakás eladásáról.

A szerződés tartalma:
- Eladó: Tóth István
- Vevő: Varga Éva  
- Tárgy: 2 szobás lakás Budapest, VIII. kerület, Rákóczi út 45. 2. emelet, 3. ajtó
- Vételár: 35.000.000 Ft
- Fizetés: 2023. december 1-én történt
- Birtokbaadás: 2023. december 5-én történt

Azonban az ingatlan-nyilvántartási bejegyzés csak 2024. január 10-én történt meg, amikor a tulajdonjog hivatalosan is Varga Évára szállt át.

2024. január 15-én Tóth István elhunyt. Örökösei azt állítják, hogy a lakás még Tóth István tulajdonában volt a halálakor, mert az ingatlan-nyilvántartási bejegyzés csak később történt meg.""",
                "kerdes": "Ki a lakás tulajdonosa? Mikor szállt át a tulajdonjog Varga Évára?",
                "megoldas": f"""A Ptk. {paragrafus} § szerint az ingatlan tulajdonjogának átruházásánál az ingatlan-nyilvántartási bejegyzés konstitutív hatályú, vagyis a tulajdonjog a bejegyzéssel száll át.

Esetünkben:
1. Szerződés megkötése: 2023. november 20.
2. Fizetés: 2023. december 1.
3. Birtokbaadás: 2023. december 5.
4. Ingatlan-nyilvántartási bejegyzés: 2024. január 10.

A tulajdonjog csak az ingatlan-nyilvántartási bejegyzéssel (2024. január 10.) szállt át Varga Évára. Ez előtt Tóth István volt a tulajdonos, még akkor is, ha már fizettek és birtokba is adták a lakást.

Következtetés: Varga Éva a lakás tulajdonosa 2024. január 10-től. Tóth István halálakor (2024. január 15.) már nem volt a tulajdonos, ezért az örökösöknek nincs jogalapjuk a követelésre."""
            },
            "jogképesség": {
                "cim": "Kiskorú szerződéskötési képessége",
                "tenyek": """2024. február 5-én, Szegeden, egy 16 éves tanuló, Kovács Márk megkötött egy szerződést egy telefonboltban egy okostelefon vásárlásáról.

A tények:
- Kovács Márk: 16 éves, tanuló, nincs saját jövedelme
- Szerződés tárgya: iPhone 15 Pro Max, 450.000 Ft
- Fizetési mód: részletfizetés, 12 hónapra, havi 37.500 Ft
- A szerződést Kovács Márk szülei nem hagyták jóvá

Kovács Márk 3 hónapig fizette a részleteket (összesen 112.500 Ft), majd abbahagyta a fizetést. A telefonbolt követeli a maradék összeg kifizetését.""",
                "kerdes": "Érvényes-e a szerződés? Ki felelős a fizetési kötelezettségért?",
                "megoldas": f"""A Ptk. {paragrafus} § szerint minden ember jogképes: jogai és kötelezettségei lehetnek. A jogképesség a fogamzás időpontjától illeti meg az embert.

A cselekvőképesség (szerződéskötési képesség) kérdése:
- 16 éves korig: csak szülői hozzájárulással köthet szerződést
- 16-18 év között: bizonyos szerződéseket önállóan is köthet (pl. mindennapi élethez szükséges dolgok)
- 18 év felett: teljes cselekvőképesség

Esetünkben:
- Kovács Márk 16 éves, de egy 450.000 Ft értékű okostelefon vásárlása nem minősül mindennapi élethez szükséges dolognak
- A szülők nem hagyták jóvá a szerződést
- A szerződés megtámadható lehet

Következtetés: A szerződés megtámadható, mert a szülők nem hagyták jóvá, és nem mindennapi élethez szükséges dologról van szó. A telefonbolt nem követelheti a maradék összeget, hacsak a szülők nem hagyják jóvá a szerződést."""
            },
            "házasság": {
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
                "megoldas": f"""A Ptk. {paragrafus} § szerint az érvénytelenítési pert a házasság fennállása alatt és a házasság megszűnése után is meg lehet indítani.

Esetünkben:
1. Házasságkötés: 2023. június 10., Anna még kiskorú volt (17 éves)
2. Gyámhatósági engedély: Nem volt gyámhatósági engedély a házasságkötéshez
3. Nagykorúság elérése: Anna 2024. január 1-én töltötte be a 18. életévét
4. Perindítási szándék: 2024. január 15-én, 14 nappal a nagykorúság elérése után

A Ptk. 4:16. § (1) bekezdése szerint: "A nagykorúság elérése után a házasságkötési engedély hiányában a kiskorúság miatt... az a házastárs jogosult érvénytelenítési per indítására, akinek személyében az érvénytelenség oka megvalósult."

Esetünkben Anna személyében valósult meg az érvénytelenség oka (kiskorúság, engedély hiánya), ezért ő jogosult a per indítására. A pert a nagykorúság elérésétől számított hat hónapon belül lehet megindítani.

Következtetés: Nagy Anna jogosult a házasság érvénytelenítési perének indítására, mert ő az, akinek személyében az érvénytelenség oka megvalósult. A perindítási határidő: 2024. január 1-től számított 6 hónap (2024. július 1-ig)."""
            }
        }
        
        # Ha van kategória-specifikus template, használjuk
        if kategoria_lower in template_jogesetek:
            template = template_jogesetek[kategoria_lower].copy()
            template["alkalmazando_jogszabaly"] = paragrafus
            # Komplexitás szerint módosítjuk
            if komplexitas == "egyszerű":
                # Rövidítjük a megoldást
                template["megoldas"] = template["megoldas"].split("\n\n")[0] + "\n\nKövetkeztetés: " + template["megoldas"].split("Következtetés: ")[-1]
            return template
        
        # Általános template, ha nincs kategória-specifikus
        # Próbáljuk kitalálni a kategóriát a kulcsszavakból
        kulcsszavak_lower = [kw.lower() for kw in elemzo.kulcsszavak]
        
        if any(kw in kulcsszavak_lower for kw in ["károkozó", "kár", "kártérítés", "károsult"]):
            kategoria_lower = "kártérítés"
        elif any(kw in kulcsszavak_lower for kw in ["szerződés", "köteles", "teljesítés"]):
            kategoria_lower = "szerződés"
        elif any(kw in kulcsszavak_lower for kw in ["tulajdonjog", "tulajdonos", "ingatlan"]):
            kategoria_lower = "tulajdonjog"
        elif any(kw in kulcsszavak_lower for kw in ["jogképesség", "jogképes", "cselekvőképesség"]):
            kategoria_lower = "jogképesség"
        
        if kategoria_lower in template_jogesetek:
            template = template_jogesetek[kategoria_lower].copy()
            template["alkalmazando_jogszabaly"] = paragrafus
            if komplexitas == "egyszerű":
                template["megoldas"] = template["megoldas"].split("\n\n")[0] + "\n\nKövetkeztetés: " + template["megoldas"].split("Következtetés: ")[-1]
            return template
        
        # Ha semmi sem illeszkedik, alapértelmezett részletes template
        # Próbáljuk generálni egy reálisabb példát a kulcsszavak alapján
        kulcsszavak_str = ', '.join(elemzo.kulcsszavak) if elemzo.kulcsszavak else 'általános jogi viszonyok'
        joghatasok_str = ', '.join(elemzo.joghatasok) if elemzo.joghatasok else 'keletkezés'
        
        # Generálunk egy általános, de részletesebb példát
        return {
            "cim": f"Jogeset - Ptk. {paragrafus}",
            "tenyek": f"""2024. március 20-án, Budapesten történt egy jogi esemény, amely a Ptk. {paragrafus} § rendelkezéseihez kapcsolódik.

A tények részletes leírása:
- Szereplők: Kovács Péter (45 éves, Budapest) és Nagy Anna (32 éves, Szeged)
- Időpont: 2024. március 20., délután 14:00
- Helyszín: Budapest, Váci út 45.
- Események: A felek között jogi viszony alakult ki, amely a Ptk. {paragrafus} § rendelkezéseihez kapcsolódik.

A jogszabály releváns elemei:
- Kulcsszavak: {kulcsszavak_str}
- Joghatások: {joghatasok_str}

A tényállás tartalmazza a releváns jogi tényeket, körülményeket, a felek személyét, az események időpontját és helyét, valamint a jogi kérdéshez kapcsolódó minden releváns információt.""",
            "kerdes": f"Milyen jogi következményekkel jár ez az eset a Ptk. {paragrafus} § alapján? Milyen jogok és kötelezettségek keletkeznek?",
            "alkalmazando_jogszabaly": f"Ptk. {paragrafus}",
            "megoldas": f"""A Ptk. {paragrafus} § alapján elemezve az esetet:

1. Jogi tények azonosítása:
   - Az esetben szereplő tények közül melyek minősülnek jogi ténynek?
   - Milyen típusú jogi tényről van szó (jogügylet, esemény, hatósági aktus)?

2. Joghatások:
   - Milyen joghatások következnek be a jogi tények alapján?
   - Jogviszony keletkezik, módosul vagy megszűnik?
   - Milyen jogok és kötelezettségek alakulnak ki?

3. Következmények:
   - Milyen jogi következményekkel jár ez az eset?
   - Milyen jogok illetik meg és milyen kötelezettségek terhelik a feleket?

A megoldás a Ptk. {paragrafus} § rendelkezéseinek alkalmazásával történik. A jogszabály kulcsszavai ({kulcsszavak_str}) és a joghatások ({joghatasok_str}) alapján a következő következtetések vonhatók le."""
        }
    
    def _parse_response(self, response, elemzo: JogszabalyElemzo,
                       komplexitas: str, kategoria: Optional[str]) -> Jogeset:
        """Feldolgozza az LLM válaszát és létrehozza a Jogeset objektumot"""
        try:
            # Konvertáljuk stringgé, ha nem az
            if isinstance(response, dict):
                # Ha már dictionary, használjuk közvetlenül
                data = response
            elif isinstance(response, str):
                # Próbáljuk JSON-ként értelmezni
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    # Ha nem JSON, próbáljuk strukturálni
                    data = self._parse_text_response(response)
            else:
                # Egyéb típus esetén stringgé konvertáljuk
                response_str = str(response)
                import re
                json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    data = self._parse_text_response(response_str)
            
            return Jogeset(
                cim=data.get("cim", "Névtelen jogeset"),
                tenyek=data.get("tenyek", ""),
                kerdes=data.get("kerdes", ""),
                alkalmazando_jogszabaly=data.get("alkalmazando_jogszabaly", elemzo.paragrafus_szam or ""),
                megoldas=data.get("megoldas", ""),
                komplexitas=komplexitas,
                kategoria=kategoria or "általános"
            )
        except Exception as e:
            print(f"Hiba a válasz feldolgozásánál: {e}")
            # Fallback - biztonságos string konverzió
            try:
                if isinstance(response, str):
                    response_str = response[:500] if len(response) > 500 else response
                elif isinstance(response, dict):
                    response_str = json.dumps(response, ensure_ascii=False)[:500]
                else:
                    response_str = str(response)[:500]
            except:
                response_str = "Nem sikerült feldolgozni a választ"
            
            return Jogeset(
                cim="Hibás generálás",
                tenyek=response_str,
                kerdes="",
                alkalmazando_jogszabaly=elemzo.paragrafus_szam or "",
                megoldas="",
                komplexitas=komplexitas,
                kategoria=kategoria or "általános"
            )
    
    def _parse_text_response(self, text: str) -> Dict:
        """Szöveges válasz strukturálása"""
        data = {}
        lines = text.split('\n')
        current_key = None
        current_value = []
        
        for line in lines:
            if ':' in line and not line.strip().startswith(' '):
                if current_key:
                    data[current_key] = ' '.join(current_value).strip()
                parts = line.split(':', 1)
                current_key = parts[0].strip().lower()
                current_value = [parts[1].strip()] if len(parts) > 1 else []
            elif current_key:
                current_value.append(line.strip())
        
        if current_key:
            data[current_key] = ' '.join(current_value).strip()
        
        return data


def main():
    parser = argparse.ArgumentParser(
        description="Fiktív jogesetek generálása jogszabályok alapján"
    )
    parser.add_argument(
        "--jogszabaly",
        type=str,
        help="A jogszabály szövege vagy paragrafus száma"
    )
    parser.add_argument(
        "--fajl",
        type=str,
        help="Fájl elérési útja, amely tartalmazza a jogszabály szövegét"
    )
    parser.add_argument(
        "--paragrafus",
        type=str,
        help="Paragrafus száma (pl. '6:519')"
    )
    parser.add_argument(
        "--komplexitas",
        type=str,
        choices=["egyszerű", "közepes", "komplex"],
        default="közepes",
        help="A generált jogeset komplexitása"
    )
    parser.add_argument(
        "--kategoria",
        type=str,
        help="Kategória (pl. 'szerződés', 'kártérítés', 'tulajdonjog')"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "anthropic", "gemini", "template"],
        default="template",
        help="LLM szolgáltató (alapértelmezett: template - LLM nélkül)"
    )
    parser.add_argument(
        "--kimenet",
        type=str,
        help="Kimeneti fájl elérési útja (JSON formátum)"
    )
    parser.add_argument(
        "--interaktiv",
        action="store_true",
        help="Interaktív mód - bevitel a konzolról"
    )
    
    args = parser.parse_args()
    
    # Jogszabály szövegének megszerzése
    jogszabaly_szoveg = None
    
    if args.interaktiv:
        print("=== JOGESET GENERÁTOR - Interaktív mód ===\n")
        print("Adja meg a jogszabály szövegét (üres sor + Enter a befejezéshez):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        jogszabaly_szoveg = "\n".join(lines)
        
        komplexitas = input("\nKomplexitás (egyszerű/közepes/komplex) [közepes]: ").strip() or "közepes"
        kategoria = input("Kategória (opcionális): ").strip() or None
        provider = input("Provider (openai/anthropic/gemini/template) [template]: ").strip() or "template"
    else:
        if args.fajl:
            fajl_path = Path(args.fajl)
            if not fajl_path.exists():
                print(f"Hiba: A fájl nem található: {args.fajl}")
                return
            
            teljes_fajl_szoveg = fajl_path.read_text(encoding='utf-8')
            
            # Ha megadtak paragrafus számot, csak azt a részt nyerjük ki
            if args.paragrafus:
                print(f"\nParagrafus kinyerése a fájlból: {args.paragrafus}")
                paragrafus_szoveg = JogszabalyElemzo.kinyer_paragrafus_fajlbol(teljes_fajl_szoveg, args.paragrafus)
                
                if paragrafus_szoveg:
                    jogszabaly_szoveg = paragrafus_szoveg
                    print(f"✓ Paragrafus megtalálva ({len(paragrafus_szoveg)} karakter)")
                else:
                    print(f"⚠ Figyelem: A paragrafus ({args.paragrafus}) nem található a fájlban.")
                    print("  Az egész fájl szövegét használjuk.")
                    jogszabaly_szoveg = teljes_fajl_szoveg
            else:
                # Ha nincs megadva paragrafus, az egész fájlt használjuk
                jogszabaly_szoveg = teljes_fajl_szoveg
                print(f"✓ Fájl betöltve ({len(teljes_fajl_szoveg)} karakter)")
        elif args.jogszabaly:
            jogszabaly_szoveg = args.jogszabaly
        else:
            print("Hiba: Meg kell adni --jogszabaly vagy --fajl paramétert, vagy --interaktiv módot használni")
            parser.print_help()
            return
        
        komplexitas = args.komplexitas
        kategoria = args.kategoria
        provider = args.provider
    
    if not jogszabaly_szoveg or not jogszabaly_szoveg.strip():
        print("Hiba: A jogszabály szövege üres")
        return
    
    # Jogszabály elemzése
    print("\nJogszabály elemzése...")
    elemzo = JogszabalyElemzo(jogszabaly_szoveg)
    struktura = elemzo.strukturalt_leiras()
    print(f"Paragrafus: {struktura['paragrafus']}")
    print(f"Kulcsszavak: {', '.join(struktura['kulcsszavak']) if struktura['kulcsszavak'] else 'Nincs'}")
    print(f"Joghatások: {', '.join(struktura['joghatasok'])}")
    
    # Jogeset generálása
    print(f"\nJogeset generálása ({komplexitas} komplexitás, {provider} provider)...")
    generator = LLMGenerator(provider=provider)
    
    try:
        jogeset = generator.generate_jogeset(elemzo, komplexitas, kategoria)
        
        # Eredmény kiírása
        print("\n" + "="*70)
        print("GENERÁLT JOGESET")
        print("="*70)
        print(f"\nCÍM: {jogeset.cim}")
        print(f"\nTÉNYÁLLÁS:\n{jogeset.tenyek}")
        print(f"\nJOGI KÉRDÉS:\n{jogeset.kerdes}")
        print(f"\nALKALMAZANDÓ JOGSZABÁLY:\n{jogeset.alkalmazando_jogszabaly}")
        print(f"\nMEGOLDÁS:\n{jogeset.megoldas}")
        print(f"\nKomplexitás: {jogeset.komplexitas}")
        print(f"Kategória: {jogeset.kategoria}")
        print("="*70)
        
        # JSON exportálás
        # Alapértelmezett mappa: projekt_root/jogesetek/
        script_dir = Path(__file__).parent
        projekt_root = script_dir.parent
        alapertelmezett_mappa = projekt_root / "jogesetek"
        alapertelmezett_mappa.mkdir(exist_ok=True)  # Létrehozza a mappát, ha nem létezik
        
        kimenet_fajl = args.kimenet
        
        # Interaktív módban kérdezzük meg, ha nincs megadva
        if args.interaktiv and not kimenet_fajl:
            kimenet_fajl = input(f"\nMentés fájlba? (Enter = alapértelmezett: jogesetek/, vagy fájlnév): ").strip()
        
        # Ha nincs megadva fájlnév, generálunk egyet
        if not kimenet_fajl:
            # Generálunk egy fájlnevet: jogeset_YYYYMMDD_HHMMSS.json vagy jogeset_paragrafus.json
            paragrafus_clean = (elemzo.paragrafus_szam or "ismeretlen").replace(":", "_").replace(".", "").replace(" ", "")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fajlnev = f"jogeset_{paragrafus_clean}_{timestamp}.json"
            kimenet_fajl = str(alapertelmezett_mappa / fajlnev)
        
        # Ha relatív útvonal, akkor az alapértelmezett mappába kerül
        kimenet_path = Path(kimenet_fajl)
        if not kimenet_path.is_absolute():
            # Ha csak fájlnév (nincs mappa), akkor az alapértelmezett mappába
            if "/" not in str(kimenet_path) and "\\" not in str(kimenet_path):
                kimenet_path = alapertelmezett_mappa / kimenet_path
            else:
                # Relatív útvonal a projekt root-hoz képest
                kimenet_path = projekt_root / kimenet_path
        
        # Biztosítjuk, hogy a mappa létezik
        kimenet_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON mentés
        with open(kimenet_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(jogeset), f, ensure_ascii=False, indent=2)
        print(f"\n✓ Jogeset mentve: {kimenet_path}")
        
    except Exception as e:
        print(f"\nHiba a generálás során: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

