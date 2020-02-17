import math

from app.data import db
from app.pokemon import constants
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


def get_extreme_last_updated_ts(name: str):
    return db.get_extreme_last_updated_ts(name)


def get_extreme_from_extreme_by_name(name, stat, type):
    ext = db.get_extreme_from_extreme_by_name(name, stat, type)
    try:
        return ext[0]
    except:
        if type == "MAX":
            return -1
        return 1000000000
    return None


'''def get_extreme_by_name(name, stat, type):
    if stat == "WEIGHT" and type=="MAX":
        return db.get_max_height_by_name(name)
    if stat == "HEIGHT" and type=="MAX":
        return db.get_max_height_by_name(name)
    if stat == "WEIGHT" and type == "MIN":
        return db.get_min_weight_by_name(name)
    if stat == "HEIGHT" and type == "MIN":
        return db.get_min_height_by_name(name)'''


def get_extremes_loose(name: str) -> List[int]:
    return [get_extreme_from_extreme_by_name(name, "WEIGHT", "MAX"),
            get_extreme_from_extreme_by_name(name, "HEIGHT", "MAX"),
            get_extreme_from_extreme_by_name(name, "WEIGHT", "MIN"),
            get_extreme_from_extreme_by_name(name, "HEIGHT", "MIN")]


def get_extremes(name: str) -> List[int]:
    return [get_max_weight(name), get_max_height(name), get_min_weight(name), get_min_height(name)]


def insert_pokemon(pokemon, source_type=None, source_name=None, created_timestamp=None, confidence_data=None,
                   extended_attributes=None, session=None, commit=True):
    success = False
    try:
        db.insert_pokemon(pokemon, source_type=source_type, source_id=source_name, created_timestamp=created_timestamp,
                          confidence_data=confidence_data, extended_attributes=extended_attributes, session=session,
                          commit=commit)
        success = True
    except:
        Config.LOGGER.exception()
    return {"success": success}


def get_all_extremes(name, evos=True, loose=True, include_null_data=2):
    ret = {"self": None, "evos": None}
    if loose:
        s = get_extremes_loose(name)
    else:
        s = get_extremes(name)
    if include_null_data < 2:
        ret["self"] = s
    else:
        if s[0] < 0 or s[1] < 0 or s[2] > 10000000 or s[3] > 10000000:
            pass
        else:
            ret["self"] = s

    try:
        ret["timestamp"] = get_extreme_last_updated_ts(name)
    except:
        pass
    if evos:
        evo_list = []
        try:
            evo_branch_list = constants.POKEMON_STATS[name]["evolutionBranch"]
            for evo in evo_branch_list:
                try:
                    evo_list.append(evo["evolution"])
                except:
                    pass
        except:
            pass
        if len(evo_list) > 0:
            evo_sizes = {}
            null_evo_sizes = {}
            try:
                self_w = constants.POKEMON_STATS[name]["weight"] * 100
                self_w_stdev = constants.POKEMON_STATS[name]["weight_std_dev"] * 100
                self_h = constants.POKEMON_STATS[name]["height"] * 100
                self_h_stdev = constants.POKEMON_STATS[name]["height_std_dev"] * 100
            except:
                pass
            i = 0
            while i < len(evo_list):
                evo = evo_list[i]
                try:
                    branch = constants.POKEMON_STATS[evo]["evolutionBranch"]
                    for b in branch:
                        try:
                            if b["evolution"] not in evo_list:
                                evo_list.append(b["evolution"])
                        except:
                            pass
                except:
                    pass
                try:
                    if loose:
                        evo_extreme = get_extremes_loose(evo)
                    else:
                        evo_extreme = get_extremes(evo)

                    evo_w = constants.POKEMON_STATS[evo]["weight"] * 100
                    evo_w_stdev = constants.POKEMON_STATS[evo]["weight_std_dev"] * 100
                    evo_h = constants.POKEMON_STATS[evo]["height"] * 100
                    evo_h_stdev = constants.POKEMON_STATS[evo]["height_std_dev"] * 100

                    evo_heavy_normalized = (evo_extreme[0] - evo_w) / evo_w_stdev
                    evo_tall_normalized = (evo_extreme[1] - evo_h) / evo_h_stdev
                    evo_light_normalized = (evo_extreme[2] - evo_w) / evo_w_stdev
                    evo_small_normalized = (evo_extreme[3] - evo_h) / evo_h_stdev

                    pre_evo_heavy = self_w + evo_heavy_normalized * self_w_stdev
                    pre_evo_tall = self_h + evo_tall_normalized * self_h_stdev
                    pre_evo_light = self_w + evo_light_normalized * self_w_stdev
                    pre_evo_small = self_h + evo_small_normalized * self_h_stdev

                    if include_null_data==1:
                        evo_sizes[evo] = [math.floor(pre_evo_heavy), math.floor(pre_evo_tall),
                                      math.ceil(pre_evo_light), math.ceil(pre_evo_small)]
                    else:
                        if evo_extreme[0] < 0 or evo_extreme[1] < 0 or evo_extreme[2] > 10000000 or evo_extreme[3] > 10000000:
                            null_evo_sizes[evo] = [math.floor(pre_evo_heavy), math.floor(pre_evo_tall),
                                              math.ceil(pre_evo_light), math.ceil(pre_evo_small)]
                        else:
                            evo_sizes[evo] = [math.floor(pre_evo_heavy), math.floor(pre_evo_tall),
                                              math.ceil(pre_evo_light), math.ceil(pre_evo_small)]
                except:
                    Config.LOGGER.exception()
                    pass
                i += 1
            if include_null_data == 2:
                if len(evo_sizes)==0:
                    evo_sizes.update(null_evo_sizes)
            ret["evos"] = evo_sizes

    return ret
