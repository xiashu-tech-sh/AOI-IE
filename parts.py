''' 元器件类 '''
import json
from collections import OrderedDict
import algorithm as alg


MISSING, MISMATCH, REVERSE = 'missing', 'mismatch', 'reverse'

class Part:
    def __init__(self):
        self.partNo = ''  # 料号
        self.classes = ''  # 元器件类别,如电阻、电容
        # 坐标，相对于Mask的坐标
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        # 检查项目, 比如： {'missing': [], 'mismatch': [], 'reverse': []}
        self.checkItems = {
            MISSING: [],
            MISMATCH: [],
            REVERSE: []
        }

    def add_check_item(self, item):
        pass

    def to_json(self):
        data = OrderedDict({
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            MISSING: [],
            MISMATCH: [],
            REVERSE: []})
        for classes in [MISSING, MISMATCH, REVERSE]:
            for item in self.checkItems[classes]:
                data[classes].append(item.to_json())
        return data

    @staticmethod
    def from_json(jsondata):
        obj = Part()
        obj.x = jsondata['x']
        obj.y = jsondata['y']
        obj.w = jsondata['w']
        obj.h = jsondata['h']
        for key in [MISSING, MISMATCH, REVERSE]:
            if key not in obj.checkItems.keys():
                continue
            for item in jsondata[key]:
                obj.checkItems[key].append(alg.restore_alg_item(item))
                # print(item)
        return obj



if __name__ == '__main__':
    # data = Part()
    # data.checkItems[MISSING].append(alg.TemplateMatching())
    # data.checkItems[MISSING].append(alg.EdgeMatching())
    # with open('abc.json', 'w', encoding='utf-8') as f:
    #     json.dump(data.to_json(), f)

    from pprint import pprint
    with open('abc.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        # print(type(data))
        # print(data)

        obj = Part.from_json(data)
        pprint(obj.to_json())
    