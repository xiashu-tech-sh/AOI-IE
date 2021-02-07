''' Mask数据类型 '''
import cv2
from collections import OrderedDict
from PyQt5 import QtGui


class Mask:
    def __init__(self, x=0, y=0, w=0, h=0, name=''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.pixmap = None  # pixmap，用于显示
        self.cvColorImage = None  # cv彩色图像
        self.cvGrayImage = None  # cv灰度图
        self.binaryImage = None  # cv二值图
        self.binaryThreshold = 0  # 二值化阈值
        self.round = None # 圆心坐标点
        self.reverse = False # 是否翻转
        self.radius = None # 半径
        self.meter = None # 半径阈值

    def __getitem__(self, index):
        return [self.x, self.y, self.w, self.h][index]

    def binary_threshold_changed(self, threshold):
        ''' 阈值变化后，重新生成用于显示用的pixmap，返回pixmap '''
        if self.cvGrayImage is None:
            raise Exception('程序错误')
        if threshold == self.binaryThreshold and self.pixmap is not None:
            return self.pixmap
        self.binaryThreshold = threshold
        if self.reverse:
            _, self.binaryImage = cv2.threshold(self.cvGrayImage, self.binaryThreshold, 255, cv2.THRESH_BINARY_INV)
        else:
            _, self.binaryImage = cv2.threshold(self.cvGrayImage, self.binaryThreshold, 255, cv2.THRESH_BINARY)
        rgbImage = cv2.cvtColor(self.binaryImage, cv2.COLOR_GRAY2RGB)
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        return self.pixmap

    def load_image(self, cvImage):
        ''' 传入原图，根据坐标截取Mask图片，并生成相应的pixmap、binaryImage、grayImage '''
        if not self.w or not self.h:
            return
        x, y, w, h = self.x, self.y, self.w, self.h
        self.cvColorImage = cvImage[y:y + h, x:x + w, :].copy()
        self.cvGrayImage = cv2.cvtColor(self.cvColorImage, cv2.COLOR_BGR2GRAY)
        _, self.binaryImage = cv2.threshold(self.cvGrayImage, self.binaryThreshold, 255, cv2.THRESH_BINARY)
        rgbImage = cv2.cvtColor(self.binaryImage, cv2.COLOR_GRAY2RGB)
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap.fromImage(image)

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
            'binaryThreshold': self.binaryThreshold,
            "round":self.round,
            "reverse":self.reverse,
            "radius":self.radius,
            "meter":self.meter}
        )
        return data

    @staticmethod
    def from_json(jsondata):
        obj = Mask()
        obj.x = jsondata['x']
        obj.y = jsondata['y']
        obj.w = jsondata['w']
        obj.h = jsondata['h']
        obj.name = jsondata['name']
        obj.binaryThreshold = jsondata['binaryThreshold']
        obj.round= jsondata['round']
        obj.reverse= jsondata['reverse']
        obj.radius= jsondata['radius']
        obj.meter= jsondata['meter']
        return obj

    @staticmethod
    def obj_data(jsondata, name, x, y):
        obj = Mask()
        obj.x = x
        obj.y = y
        obj.w = jsondata.w
        obj.h = jsondata.h
        obj.name = 'mask_%s' % (name + 1)
        obj.binaryThreshold = jsondata.binaryThreshold
        obj.round= jsondata.round
        obj.reverse= jsondata.reverse
        obj.radius= jsondata.radius
        obj.meter= jsondata.meter
        return obj
