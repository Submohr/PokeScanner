from PIL import Image
from app.scan.scan import *
from config import Config
from typing import List, Dict
from pandas import DataFrame

__all__ = ["Screenshot"]


# represents the 'screenshot' - tries to OCR to get relevant data, but does no logic i.e. does not smooth Pokemon
# names, etc.

def df_to_lists(df):
    conf = df['conf'].tolist()
    text = df['text'].tolist()
    return {'conf': conf, 'text': text}


class Screenshot(object):
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.props = ['name', 'weight', 'height', 'lucky', 'type']
        self.thresholds = {'name': 160, 'weight': 160, 'height': 160, 'lucky': 220, 'type': 210}
        self.boxes = {'name': [180, 880, 950, 1000], 'weight': [100, 1150, 400, 1250],
                      'height': [730, 1150, 1030, 1250], 'lucky': [400, 1010, 530, 1050],
                      'type': [400, 1250, 750, 1300]}
        self.lucky_offset = 0
        self.lucky = False

        # data objects below are dicts with 'conf' and 'text' lists.
        self.name_data = None
        self.weight_data = None
        self.height_data = None
        self.type_data = None
        self.created_ts = None

        try:
            self.created_ts = self.image._getexif()[36867]
        except:
            pass

        try:
            if 'LUCKY' == self.get_data('lucky', scan_type="WORDS")['data']['text'].str.cat(sep=' '):
                self.lucky_offset = 50
                self.lucky = True
        except:
            pass

        try:
            name_df = self.get_data('name', scan_type="WORDS")['data']
            self.name_data = df_to_lists(name_df)
        except:
            pass

        try:
            weight_df = self.get_data('weight', scan_type="NUMBERS")['data']
            self.weight_data = df_to_lists(weight_df)
        except:
            pass

        try:
            height_df = self.get_data('height', scan_type="NUMBERS")['data']
            self.height_data = df_to_lists(height_df)
        except:
            pass

        try:
            type_df = self.get_data('type', scan_type="WORDS")['data']
            self.type_data = df_to_lists(type_df)
        except:
            pass

        self.image.close()

    def get_box(self, prop: str) -> List[int]:
        if prop in ['name', 'lucky']:
            return self.boxes[prop]
        elif prop in ['weight', 'height', 'type']:
            ret = self.boxes[prop]
            ret[1] = ret[1] + self.lucky_offset
            ret[3] = ret[3] + self.lucky_offset
            return ret
        raise Exception

    def get_data(self, prop: str, scan_type: str = "DEFAULT") -> Dict:
        if prop in self.props:
            box = self.get_box(prop)
            threshold = self.thresholds[prop]
            return scan_box(self.image, box, thresh=threshold, scan_type=scan_type)
        raise Exception

    def __repr__(self):
        return f"{self.image_path}, {self.name_data}, {self.weight_data}, {self.height_data}"
