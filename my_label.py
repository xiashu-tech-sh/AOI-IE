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

