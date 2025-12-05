#!/usr/bin/env python3
"""
Jogeset JSON Adatbázis Kezelő
JSON fájlokból véletlenszerűen választ jogeseteket.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class JogesetDB:
    """Jogeset adatbázis struktúra"""
    paragrafus: str
    kategoria: str
    jogesetek: List[Dict]


class JogesetDatabase:
    """JSON alapú jogeset adatbázis kezelő"""
    
    def __init__(self, db_path: Path):
        """
        Inicializálja az adatbázist
        
        Args:
            db_path: A JSON fájlok mappájának elérési útja
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self._cache = {}  # Cache a betöltött fájlokhoz
    
    def _get_filename(self, paragrafus: str) -> str:
        """Paragrafus számból fájlnév generálása"""
        # "6:519" -> "6_519.json"
        # "4:15" -> "4_15.json"
        clean = paragrafus.replace("Ptk.", "").replace("§", "").strip()
        if clean.endswith("."):
            clean = clean[:-1]
        return clean.replace(":", "_") + ".json"
    
    def _load_paragrafus_file(self, paragrafus: str) -> Optional[JogesetDB]:
        """Betölt egy paragrafus fájlt"""
        filename = self._get_filename(paragrafus)
        filepath = self.db_path / filename
        
        # Cache ellenőrzés
        if filename in self._cache:
            return self._cache[filename]
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            db_obj = JogesetDB(
                paragrafus=data.get('paragrafus', paragrafus),
                kategoria=data.get('kategoria', 'általános'),
                jogesetek=data.get('jogesetek', [])
            )
            
            # Cache-be mentés
            self._cache[filename] = db_obj
            return db_obj
            
        except Exception as e:
            print(f"Hiba a fájl betöltésénél ({filepath}): {e}")
            return None
    
    def get_random_jogeset(self, paragrafus: str, komplexitas: Optional[str] = None) -> Optional[Dict]:
        """
        Véletlenszerűen választ egy jogesetet
        
        Args:
            paragrafus: Paragrafus száma (pl. "6:519")
            komplexitas: Opcionális komplexitás szűrés ("egyszerű", "közepes", "komplex")
        
        Returns:
            Jogeset dictionary vagy None
        """
        db_obj = self._load_paragrafus_file(paragrafus)
        
        if not db_obj or not db_obj.jogesetek:
            return None
        
        # Szűrés komplexitás szerint, ha meg van adva
        filtered_jogesetek = db_obj.jogesetek
        if komplexitas:
            filtered_jogesetek = [
                j for j in db_obj.jogesetek 
                if j.get('komplexitas', 'közepes') == komplexitas
            ]
        
        # Ha nincs megfelelő komplexitású, akkor mindet használjuk
        if not filtered_jogesetek:
            filtered_jogesetek = db_obj.jogesetek
        
        if not filtered_jogesetek:
            return None
        
        # Véletlenszerű választás
        selected = random.choice(filtered_jogesetek)
        
        # Hozzáadjuk a paragrafus számot és kategóriát
        selected['alkalmazando_jogszabaly'] = db_obj.paragrafus
        selected['kategoria'] = db_obj.kategoria
        
        return selected
    
    def get_all_jogesetek(self, paragrafus: str) -> Optional[List[Dict]]:
        """Visszaadja az összes jogesetet egy paragrafushoz"""
        db_obj = self._load_paragrafus_file(paragrafus)
        
        if not db_obj:
            return None
        
        # Hozzáadjuk a paragrafus számot és kategóriát minden jogesethez
        result = []
        for jogeset in db_obj.jogesetek:
            jogeset_copy = jogeset.copy()
            jogeset_copy['alkalmazando_jogszabaly'] = db_obj.paragrafus
            jogeset_copy['kategoria'] = db_obj.kategoria
            result.append(jogeset_copy)
        
        return result
    
    def add_jogeset(self, paragrafus: str, kategoria: str, jogeset: Dict) -> bool:
        """
        Hozzáad egy új jogesetet az adatbázishoz
        
        Args:
            paragrafus: Paragrafus száma
            kategoria: Kategória
            jogeset: Jogeset dictionary
        
        Returns:
            True ha sikeres, False ha hiba történt
        """
        filename = self._get_filename(paragrafus)
        filepath = self.db_path / filename
        
        # Betöltjük a meglévő fájlt vagy létrehozunk újat
        db_obj = self._load_paragrafus_file(paragrafus)
        
        if db_obj:
            # Hozzáadjuk az új jogesetet
            new_id = max([j.get('id', 0) for j in db_obj.jogesetek], default=0) + 1
            jogeset['id'] = new_id
            db_obj.jogesetek.append(jogeset)
        else:
            # Új fájl létrehozása
            new_id = 1
            jogeset['id'] = new_id
            db_obj = JogesetDB(
                paragrafus=paragrafus,
                kategoria=kategoria,
                jogesetek=[jogeset]
            )
        
        # Mentés
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(db_obj), f, ensure_ascii=False, indent=2)
            
            # Cache frissítése
            self._cache[filename] = db_obj
            return True
            
        except Exception as e:
            print(f"Hiba a fájl mentésénél ({filepath}): {e}")
            return False
    
    def list_paragrafusok(self) -> List[str]:
        """Visszaadja az összes elérhető paragrafus számot"""
        paragrafusok = []
        for filepath in self.db_path.glob("*.json"):
            # Fájlnévből paragrafus szám visszaállítása
            filename = filepath.stem  # "6_519"
            paragrafus = filename.replace("_", ":") + ". §"
            paragrafusok.append(paragrafus)
        return sorted(paragrafusok)
    
    def clear_cache(self):
        """Cache törlése"""
        self._cache.clear()

