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
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 4))
        if self.points:
            for pos in self.points:
                painter.drawRect(pos[0],pos[1],pos[2],pos[3])
        painter.end()

