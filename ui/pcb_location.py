import os
from PyQt5 import QtCore, QtGui, QtWidgets
from pcb_location_ui import Ui_Form


class PCBLocationWidget(QtWidgets.QWidget, Ui_Form):

    savePCBLocationInfomation = QtCore.pyqtSignal()  # PCB定位确定后，点击‘保存’按钮后触发

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 初始化
        self.clear()
        self.savePCBButton.clicked.connect(self.save_pcb_button_clicked)

    def clear(self):
        ''' 还原回初始状态 '''
        self.pcbImage = None  # pcb的pixmap
        self.pcbLabel.clear()
        self.pcbLabel.setEnabled(True)

    def set_pixmap(self, widget, pixmap):
        ''' 在指定的widget上显示图像 '''
        if widget == self.pcbLabel:
            self.pcbImage = pixmap
        else:
            return
        pixmap = pixmap.scaled(widget.size(), QtCore.Qt.KeepAspectRatio)
        widget.setPixmap(pixmap)

    def update_pixmap_show(self):
        if self.pcbImage:
            pixmap = self.pcbImage.scaled(self.pcbLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.pcbLabel.setPixmap(pixmap)

    def save_pcb_button_clicked(self):
        # 保证PCB板区域被选中
        if not self.pcbImage:
            QtWidgets.QMessageBox.warning(self, '提示', '请选中PCB板区域')
            return
        self.savePCBLocationInfomation.emit()