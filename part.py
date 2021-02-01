''' 元器件类 '''
import cv2
from collections import OrderedDict
import algorithm as alg
from PyQt5 import QtGui

MISSING, MISMATCH, REVERSE = 'missing', 'mismatch', 'reverse'


class Part:
    def __init__(self, x=0, y=0, w=0, h=0, name='', part_type=''):
        self.partNo = ''  # 料号
        self.part_type = part_type  # 元器件类别,如电阻、电容
        # 坐标，相对于Mask的坐标
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.folder = None
        # 漏件坐标
        self.leak_pos = []
        # 漏件模板图片路径
        self.leak_path = None
        #  漏件相似度
        self.leak_similar = None
        # 错件坐标
        self.erron_pos = None
        # 错件内容
        self.content = None
        # 正负极坐标 [ [正], [负] ]
        self.Z_F_pos = []
        # 正极灰度值
        self.Z_gray = None
        # 负极灰度值
        self.F_gray = None
        # 检查类型
        self.detection_type = []
        # 正负极阈值
        self.Z_F_hold = None
        # OCR旋转角度
        self.rotation_angle = None
        # 下拉框（颜色提取值）
        self.set_value = None
        self.cvColorImage = None
        self.pixmap = None

    def __getitem__(self, index):
        return [self.x, self.y, self.w, self.h][index]

    def load_image(self, cvImage):
        ''' 传入原图，根据坐标截取Mask图片，并生成相应的pixmap、binaryImage、grayImage '''
        if not self.w or not self.h:
            return
        x, y, w, h = self.x, self.y, self.w, self.h
        if w < 0:
            self.cvColorImage = cvImage[y + h:y, x + w:x, :].copy()
        else:
            self.cvColorImage = cvImage[y:y + h, x:x + w, :].copy()
        rgbImage = cv2.cvtColor(self.cvColorImage, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap.fromImage(image)

    def add_check_item(self, item):
        pass

    def coordinates_changed(self, x, y, w, h, cvImage):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.load_image(cvImage)

    def to_json(self):
        data = OrderedDict({
            'partNo': self.partNo,
            'part_type': self.part_type,
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            'name': self.name,

            'leak_pos': self.leak_pos,  # 漏检坐标点
            'leak_path': self.leak_path, # 漏检图片地址
            'leak_similar': self.leak_similar, # 漏检相似度
            'erron_pos':self.erron_pos, # 错件模板坐标点
            'content': self.content,# 内容
            'rotation_angle':self.rotation_angle, # OCR旋转角度
            'Z_F_pos': self.Z_F_pos, # 正负极坐标点
            'Z_F_hold' : self.Z_F_hold,# 灰度差阈值
            'Z_gray': self.Z_gray,# 正极灰度值
            'F_gray': self.F_gray,# 负极灰度值
            'detection_type': self.detection_type, # 检测类型
            'set_value':self.set_value
        }
        )

        return data

    @staticmethod
    def from_json(jsondata):
        obj = Part()
        obj.partNo = jsondata['partNo']
        obj.part_type = jsondata['part_type']
        obj.x = jsondata['x']
        obj.y = jsondata['y']
        obj.w = jsondata['w']
        obj.h = jsondata['h']
        obj.name = jsondata['name']
        obj.leak_pos = jsondata['leak_pos']
        obj.leak_path = jsondata['leak_path']
        obj.leak_similar = jsondata['leak_similar']
        obj.erron_pos = jsondata['erron_pos']
        obj.content = jsondata['content']
        obj.rotation_angle = jsondata['rotation_angle']
        obj.Z_F_pos = jsondata['Z_F_pos']
        obj.Z_F_hold = jsondata['Z_F_hold']
        obj.Z_gray = jsondata['Z_gray']
        obj.F_gray = jsondata['F_gray']
        obj.set_value = jsondata['set_value']
        obj.detection_type = jsondata['detection_type']
        obj.content = jsondata['content']

        # obj.ng_type= jsondata['detect_type']
        #
        # for key in [MISSING, MISMATCH, REVERSE]:
        #     if key not in obj.checkItems.keys():
        #         continue
        #     for item in jsondata[key]:
        #         obj.checkItems[key].append(alg.restore_alg_item(item))
        return obj

    @staticmethod
    def obj_data(jsondata, name, x, y):
        obj = Part()
        obj.partNo = jsondata.partNo
        obj.part_type = jsondata.part_type
        obj.x = x
        obj.y = y
        obj.w = jsondata.w
        obj.h = jsondata.h
        obj.name = 'part_%s' % (name + 1)
        obj.leak_pos = jsondata.leak_pos
        if jsondata.leak_path:
            template_path = jsondata.leak_path.split("_")[0] + "_%s.jpg" % (name + 1)
            obj.leak_path = template_path
        else:
            obj.leak_path = jsondata.leak_path
        obj.leak_similar = jsondata.leak_similar
        obj.Z_F_pos = jsondata.Z_F_pos
        obj.Z_F_hold = jsondata.Z_F_hold
        obj.Z_gray = jsondata.Z_gray
        obj.F_gray = jsondata.F_gray
        obj.detection_type = jsondata.detection_type
        obj.content = jsondata.content
        obj.rotation_angle = jsondata.rotation_angle
        obj.set_value = jsondata.set_value
        # obj.ng_type= jsondata['detect_type']
        #
        # for key in [MISSING, MISMATCH, REVERSE]:
        #     if key not in obj.checkItems.keys():
        #         continue
        #     for item in jsondata[key]:
        #         obj.checkItems[key].append(alg.restore_alg_item(item))
        return obj


import json

if __name__ == '__main__':
    # data = Part()
    # data.checkItems[MISSING].append(alg.TemplateMatching())
    # data.checkItems[MISSING].append(alg.EdgeMatching())
    # with open('abc.json', 'w', encoding='utf-8') as f:
    #     json.dump(data.to_json(), f)

    from pprint import pprint

    with open('./P/p1/info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(type(data))
        print(data)

        obj = Part.from_json(data)
        pprint(obj.to_json())
