from PyQt5.QtWidgets import QLabel, QMenu, QAction
# from edit_shape import edit_shape
from qtpy import QtGui
from qtpy import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
import cv2
import numpy as np
class My_label(QLabel):

    def __init__(self):
        super().__init__()

        self.points = []

    def mouse_click(event):
        if event == cv2.EVENT_LBUTTONDOWN:  # 左边鼠标点击
            # print('PIX:', x, y)
            print("BGR:", img[y, x])
            # print("GRAY:", gray[y, x])
            print("HSV:", hsv[y, x])
            print(np.average(np.average(hsv, axis=0), axis=0))
            lower_red = hsv[y, x]  # 红色阈值下界
            higher_red = hsv[y, x] - 20  # 红色阈值上界
            hsvs = rgb2hsv(lower_red[0], lower_red[1], lower_red[2])
            print("hhhh", hsvs)
            mask_red = cv2.inRange(hsv, higher_red, lower_red)  # 可以认为是过滤出红色部分，获得红色的掩膜
            mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
            cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测 #红色
            if cnts1:
                for i in cnts1:  # 遍历所有的轮廓
                    x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
                    # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255,), 3)

                    # cnt = max(cnts1, key=cv2.contourArea)
                    # x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
                    #
                    # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来

                    # cv2.imshow('frame', img)
    def paintEvent(self, event):
        super().paintEvent(event)
        # if self.image_label:
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 4))
        #     font = QFont("Microsoft YaHei", 20,40)
        #     painter.setFont(font)
        #     for pos in self.ng_list:
        #         painter.drawText(pos[0]+pos[2]//2,pos[1]+pos[3]//2,"NG")
        # painter.drawRect(235, 143,100,100)
        if self.points:
            for pos in self.points:
                painter.drawRect(pos[0],pos[1],pos[2],pos[3])
        # painter.drawRect(1031*self.si,629+148)*self.si,143*self.si,177*self.si)
        painter.end()

