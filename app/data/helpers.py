# data helper methods
from config import Config
from typing import List, Dict


def weight_int_to_str(weight: int) -> str:
    if weight is not None:
        return int_to_str(weight) + " kg"
    return None


def height_int_to_str(height: int) -> str:
    if height is not None:
        return int_to_str(height) + " m"
    return None


def int_to_str(c: int) -> str:
    if c >= 100:
        s = str(c)
        return ".".join([s[:-2], s[-2:]])
    else:
        return "0." + f'{c:02}'


def weight_str_to_int(weight: str) -> int:
    # assumes format is 'xx.xx kg'
    if weight[-2:] == 'kg':
        weight = weight[:-2]

    try:
        return str_to_int(weight.strip())
    except:
        return None


def height_str_to_int(height: str) -> int:
    # assumes format is 'xx.xx m'
    if height[-1:] == 'm':
        height = height[:-1]
    try:
        return str_to_int(height.strip())
    except:
        return None


def str_to_int(c: str) -> int:
    if c.rfind('.') > 0:
        base = int(c[:c.rfind('.')]) * 100
        right = int(f"{c[c.rfind('.') + 1:]:0<2}")
        return base + right
    return int(c) * 100


