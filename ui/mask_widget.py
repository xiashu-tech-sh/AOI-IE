import os
from PyQt5 import QtCore, QtGui, QtWidgets
from mask_widget_ui import Ui_Form
from mask import Mask


class MaskWidget(QtWidgets.QWidget, Ui_Form):

    # getMaskSignal = QtCore.pyqtSignal(QtWidgets.QLabel, name='getMaskSignal')  # 获取模板信号，参数为需要显示的控件
    # newMaskShape = QtCore.pyqtSignal(str, str, name='newMaskShape')  # 请求创建新的mask
    savePatternSignal = QtCore.pyqtSignal(name='savePatternSignal')  # 保存pattern
    selectedChanged = QtCore.pyqtSignal(str, str, name='selectedChanged')

    def __init__(self):
        ''' Maks页面 '''
        super().__init__()
        self.setupUi(self)
        self.threshSlider.setRange(0, 255)
        self.threshSlider.sliderMoved.connect(self.threshold_changed)
        self.previewLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.currentMask = None
        self.maskList = []
        # self.getCircleButton.clicked.connect(self.get_circle_button_clicked)
        self.saveButton.clicked.connect(self.savePatternSignal)
        self.listWidget.currentRowChanged.connect(self.item_changed)

    # def get_circle_button_clicked(self):
        # self.getMaskSignal.emit(self.previewLabel)

    def set_mask(self, mask):
        self.currentMask = mask
        self.threshSlider.setValue(self.currentMask.binaryThreshold)
        pixmap = self.currentMask.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)

    def delete_by_name(self, name=''):
        index = -1
        for i, mask in enumerate(self.maskList):
            if mask.name == name:
                index = i
                break
        if index >= 0:
            self.maskList.pop(index)
            self.listWidget.takeItem(index)  # remove row from qlistwidget

    def threshold_changed(self, value):
        ''' 拖动slider后的响应函数，更新图片显示 '''
        if not self.currentMask:
            return
        pixmap = self.currentMask.binary_threshold_changed(value)
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)

    def update_pixmap_show(self):
        if self.currentMask:
            pixmap = self.currentMask.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.previewLabel.setPixmap(pixmap)
            self.selectedChanged.emit('mask', self.currentMask.name)

    def save_current(self):
        if not self.currentMask and not self.maskList:
            QtWidgets.QMessageBox.warning(self, '提示', '请先选择一个mask')
            return
        elif self.currentMask and self.currentMask not in self.maskList:  # 新保存
            self.maskList.append(self.currentMask)
            self.currentMask = None
            self.update_listwidget()
            count = self.listWidget.count()
            self.listWidget.setCurrentRow(count-1)
            print('add new mask')
        else:  # 修改, TODO
            pass
        # self.savePatternSignal.emit()

    def update_listwidget(self):
        self.listWidget.clear()
        # for i in range(len(self.maskList)):
        #     self.listWidget.addItem('mask_{}'.format(i+1))
        for mask in self.maskList:
            self.listWidget.addItem(mask.name)
        if self.maskList:
            self.listWidget.setCurrentRow(0)  # 显示第一个mask
            self.threshSlider.setValue(self.maskList[0].binaryThreshold)
            # self.item_changed(0)  # 显示第一个mask
            # self.selectedChanged.emit('mask', self.currentMask.name)

    def item_changed(self, rowIndex):
        self.currentMask = self.maskList[rowIndex]
        pixmap = self.currentMask.pixmap
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.selectedChanged.emit('mask', self.currentMask.name)

    def set_current_mask_by_name(self, name):
        for i, mask in enumerate(self.maskList):
            if mask.name == name:
                # self.listWidget.setCurrentIndex(i)
                self.listWidget.setCurrentRow(i)
                return