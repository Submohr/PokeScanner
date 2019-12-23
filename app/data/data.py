from app.data import db
from config import Config
from typing import List, Dict


def get_max_weight(name: str) -> int:
    return db.get_max_weight_by_name(name)


def get_max_height(name: str) -> int:
    return db.get_max_height_by_name(name)


def get_min_weight(name: str) -> int:
    return db.get_min_weight_by_name(name)


def get_min_height(name: str) -> int:
    return db.get_min_height_by_name(name)


def get_extreme_from_extreme_by_name(name, stat, type):
    ext = db.get_extreme_from_extreme_by_name(name, stat, type)
    return ext


def get_extremes_loose(name: str) -> List[int]:
    return [get_extreme_from_extreme_by_name(name, "WEIGHT", "MAX"),
            get_extreme_from_extreme_by_name(name, "HEIGHT", "MAX"),
            get_extreme_from_extreme_by_name(name, "WEIGHT", "MIN"),
            get_extreme_from_extreme_by_name(name, "HEIGHT", "MIN")]


def get_extremes(name: str) -> List[int]:
    return [get_max_weight(name), get_max_height(name), get_min_weight(name), get_min_height(name)]


def get_upgrades(pokemon, evo=True) -> Dict[str, str]:
    return {}


def insert_pokemon(pokemon, source_type=None, source_name=None, created_timestamp=None, confidence_data=None,
                   extended_attributes=None, session=None, commit=True):
    success = False
    try:
        upgrades = get_upgrades(pokemon, evo=True)
        db.insert_pokemon(pokemon, source_type=source_type, source_id=source_name, created_timestamp=created_timestamp,
                          confidence_data=confidence_data, extended_attributes=extended_attributes, session=session,
                          commit=commit)
        success = True
    except:
        Config.LOGGER.exception()
    return {"success": success, "upgrades": upgrades}
