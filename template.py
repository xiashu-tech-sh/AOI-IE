''' Template数据类型 '''
import os
import cv2
from collections import OrderedDict
from PyQt5 import QtGui


class Template:
    def __init__(self, x=0, y=0, w=0, h=0, name=''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.pixmap = None  # pixmap，用于显示
        self.cvColorImage = None  # cv彩色图像
        self.threshold = None  # 匹配颜色阈值
        self.combox_index = 0  # 下拉框索引

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
    #
    # def get_detector(self):
    #     return self.detector

    def coordinates_changed(self, x, y, w, h, cvImage):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.load_image(cvImage)

    def to_json(self):
        data = OrderedDict({
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            'name': self.name,
            'threshold': self.threshold,
            'combox_index': self.combox_index})

        return data

    @staticmethod
    def from_json(jsondata):
        obj = Template()
        obj.x = jsondata['x']
        obj.y = jsondata['y']
        obj.w = jsondata['w']
        obj.h = jsondata['h']
        obj.name = jsondata['name']
        obj.threshold = jsondata['threshold']
        obj.combox_index = jsondata['combox_index']
        return obj

    @staticmethod
    def obj_data(jsondata, name, x, y):
        obj = Template()
        obj.x = x
        obj.y = y
        obj.w = jsondata.w
        obj.h = jsondata.h
        obj.name = 'template_%s' % (name + 1)
        obj.threshold = jsondata.threshold
        obj.combox_index = jsondata.combox_index
        return obj
