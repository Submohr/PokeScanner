from app.pokemon import Pokemon, constants
from app.scan import Screenshot
import re
from typing import List, Dict
from app.data import helpers as dhelp
from config import Config

type_regex = re.compile('[^a-zA-Z]')


# converts screenshot data (mostly - raw strings, etc) into Pokemon data.

def pokemon_from_screenshot(screenshot: Screenshot) -> Pokemon:
    name = None
    name_conf = -1
    weight = -1
    weight_conf = -1
    height = -1
    height_conf = -1
    types = []
    types_conf = -1
    try:
        types = handle_types(screenshot.type_data['text'])
    except:
        types = None
    try:
        names = screenshot.name_data['text']
        name = " ".join(names)
        name = handle_name(name, types)
    except:
        Config.LOGGER.exception()
        name = None

    try:
        weight_strs = screenshot.weight_data['text']
        for i, w in enumerate(weight_strs):
            try:
                weight = handle_weight_str(w)
                weight_conf = screenshot.weight_data['conf'][i]
                break
            except:
                continue
    except:
        weight = None
        weight_conf = -1

    try:
        height_strs = screenshot.height_data['text']
        for i, h in enumerate(height_strs):
            try:
                height = handle_height_str(h)
                height_conf = screenshot.height_data['conf'][i]
                break
            except:
                continue
    except:
        height = None
        height_conf = -1
    return Pokemon(name, weight, height)


def handle_types(types_list: List[str]) -> List[str]:
    ret_list = []
    for type in types_list:
        try:
            formatted_type = type_regex.sub('', type)
            if formatted_type in constants.POKEMON_TYPES:
                ret_list = ret_list + [formatted_type]
        except:
            continue

    return ret_list


def handle_name(nm: str, types: List[str]) -> str:
    name = nm.capitalize()
    if name in constants.ALOLAN_NAMES:
        alolan_name = handle_regional_name(name, types, "Alolan")
        if alolan_name is not None:
            return alolan_name

    if name in constants.GALARIAN_NAMES:
        galarian_name = handle_regional_name(name, types, "Galarian")
        if galarian_name is not None:
            return galarian_name

    if name == "Castform":
        return handle_castform_name(types)

    if name in constants.POKEMON_NAMES:
        return name

    return handle_known_errors(name)


def handle_regional_name(nm: str, types: List[str], region: str) -> str:
    if region == "Alolan":
        regional_type_list = constants.ALOLAN_TYPES
    if region == "Galarian":
        regional_type_list = constants.GALARIAN_TYPES

    region_types = regional_type_list.get(nm)
    for region_type in region_types:
        if region_type not in types:
            return None

    return " ".join([region, nm]).capitalize()


def handle_castform_name(types: List[str]) -> str:
    if "FIRE" in types:
        return "Castform fire"
    if "WATER" in types:
        return "Castform water"
    if "ICE" in types:
        return "Castform ice"
    if "NORMAL" in types:
        return "Castform normal"


def handle_known_errors(nm: str) -> str:
    return constants.KNOWN_OCR_ERRORS.get(nm, None)


def handle_weight_str(weight_str: str) -> int:
    weight_str = weight_str.lower()
    try:
        if weight_str[-1:] == "k" or weight_str[-1:] == "g":
            weight_str = weight_str[:-1]
    except:
        pass
    try:
        if weight_str[-1:] == "k" or weight_str[-1:] == "g":
            weight_str = weight_str[:-1]
    except:
        pass
    return dhelp.weight_str_to_int(weight_str)


def handle_height_str(height_str: str) -> int:
    height_str = height_str.lower()
    try:
        if height_str[-1:] == "m":
            height_str = height_str[:-1]
    except:
        pass
    return dhelp.height_str_to_int(height_str)
