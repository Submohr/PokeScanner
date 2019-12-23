import pytesseract
from PIL import Image
from config import Config
from typing import Dict, List, Union
import pandas

__all__ = ["scan_box_from_path", "scan_box", "scan_from_path", "scan"]

default_thresh = 140


# this class just exists to OCR.  little to no logic in here.

def scan_box_from_path(path: str, coords: List[int], thresh: int = default_thresh) -> \
        Dict[str, Union[int, pandas.DataFrame]]:
    img = Image.open(path)
    return scan_box(img, coords, thresh=thresh)


def scan_box(img: Image, coords: List[int], thresh: int = default_thresh) -> Dict[str, Union[int, pandas.DataFrame]]:
    box_img = img.crop((coords[0], coords[1], coords[2], coords[3]))
    return scan(box_img, thresh=thresh)


def scan_from_path(path: str, thresh: int = default_thresh) -> Dict[str, Union[int, pandas.DataFrame]]:
    img = Image.open(path)
    return scan(img, thresh=thresh)


def scan(img: Image, thresh: int = default_thresh) -> Dict[str, Union[int, pandas.DataFrame]]:
    try:
        def fn(x):
            if x > thresh:
                return 255
            return 0

        converted_img = img.convert('L').point(fn, mode='1')
        data = pytesseract.image_to_data(converted_img, output_type='data.frame',
                                         config=Config.TESSDATA_DIR_CONFIG)
        data = data[data.conf != -1]
        return {'code': 0, 'data': data}
    except Exception as e:
        Config.LOGGER.exception("Exception scanning.")
        return {'code': 1, 'data': None}
