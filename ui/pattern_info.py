import os
from PyQt5 import QtCore, QtGui, QtWidgets
from pattern_info_ui import Ui_Form


class PatternInfoWidget(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        ''' 程式相关信息展示界面 '''
        super().__init__()
        self.setupUi(self)

    def show_pattern_info(self, folder):
        self.patternEdit.setText(folder)