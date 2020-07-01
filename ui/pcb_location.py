import os
from PyQt5 import QtCore, QtGui, QtWidgets
from pcb_location_ui import Ui_Form


class PCBLocationWidget(QtWidgets.QWidget, Ui_Form):

    getPCBSignal = QtCore.pyqtSignal(name='getPCBSignal')  # 获取PCB板信号
    getImageSignal = QtCore.pyqtSignal(QtWidgets.QLabel, name='getImageSignal')  # 获取模板信号，参数为需要显示的控件
    savePCBLocationInfomation = QtCore.pyqtSignal()  # PCB定位确定后，点击‘保存’按钮后触发
    saveTemplateInfomation =  QtCore.pyqtSignal()   # 模板确定后，点击‘保存’按钮后触发

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 初始化
        self.clear()
        # 按钮点击信号连接槽函数
        for obj in [self.getTemplateButton_1, self.getTemplateButton_2, self.getPCBButton]:
            obj.clicked.connect(self.get_image_sender)
        # checkbox信号
        self.checkBox_1.stateChanged.connect(self.checkbox_status_change)
        self.checkBox_2.stateChanged.connect(self.checkbox_status_change)

        self.savePCBButton.clicked.connect(self.save_pcb_button_clicked)
        self.saveTemplateButton.clicked.connect(self.save_template_button_clicked)

    def clear(self):
        ''' 还原回初始状态 '''
        self.template_1 = None  # 模板1的pixmap
        self.template_2 = None  # 模板2的pixmap
        self.pcbImage = None  # pcb的pixmap
        
        self.templateLabel_1.clear()
        self.templateLabel_2.clear()
        self.pcbLabel.clear()
        self.pcbLabel.setEnabled(True)
        self.set_template_enable(False)

    def set_template_enable(self, enable):
        self.checkBox_1.setEnabled(enable)
        self.checkBox_2.setEnabled(enable)
        self.getTemplateButton_1.setEnabled(enable)
        self.getTemplateButton_2.setEnabled(enable)
        self.templateLabel_1.setEnabled(enable)
        self.templateLabel_2.setEnabled(enable)
        self.saveTemplateButton.setEnabled(enable)
        self.resetTemplateButton.setEnabled(enable)

    def set_pixmap(self, widget, pixmap):
        ''' 在指定的widget上显示图像 '''
        if widget == self.templateLabel_1:
            self.template_1 = pixmap
            self.checkBox_1.setChecked(True)
        elif widget == self.templateLabel_2:
            self.template_2 = pixmap
            self.checkBox_2.setChecked(True)
        elif widget == self.pcbLabel:
            self.pcbImage = pixmap
        else:
            return
        pixmap = pixmap.scaled(widget.size(), QtCore.Qt.KeepAspectRatio)
        widget.setPixmap(pixmap)

    def update_pixmap_show(self):
        if self.template_1:
            pixmap = self.template_1.scaled(self.templateLabel_1.size(), QtCore.Qt.KeepAspectRatio)
            self.templateLabel_1.setPixmap(pixmap)
        if self.template_2:
            pixmap = self.template_2.scaled(self.templateLabel_2.size(), QtCore.Qt.KeepAspectRatio)
            self.templateLabel_2.setPixmap(pixmap)
        if self.pcbImage:
            pixmap = self.pcbImage.scaled(self.pcbLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.pcbLabel.setPixmap(pixmap)

    def get_image_sender(self):
        ''' 点击按钮获取模板（或PCB）时，通过此函数发射信号给上层界面，截取图像并显示在本界面相应位置 '''
        obj = self.sender()
        if obj == self.getTemplateButton_1:
            self.getImageSignal.emit(self.templateLabel_1)
        elif obj == self.getTemplateButton_2:
            self.getImageSignal.emit(self.templateLabel_2)
        elif obj == self.getPCBButton:
            self.getPCBSignal.emit()

    def checkbox_status_change(self, state):
        obj = self.sender()
        if obj == self.checkBox_1:
            button = self.getTemplateButton_1
            label = self.templateLabel_1
        elif obj == self.checkBox_2:
            button = self.getTemplateButton_2
            label = self.templateLabel_2
        else:
            return
        button.setEnabled(state == QtCore.Qt.Checked)
        label.setEnabled(state == QtCore.Qt.Checked)

    def save_pcb_button_clicked(self):
        # 保证PCB板区域被选中
        if not self.pcbImage:
            QtWidgets.QMessageBox.warning(self, '提示', '请选中PCB板区域')
            return
        self.savePCBLocationInfomation.emit()
        self.set_template_enable(True)

    def save_template_button_clicked(self):
        check_1 = self.checkBox_1.checkState() == QtCore.Qt.Checked
        check_2 = self.checkBox_2.checkState() == QtCore.Qt.Checked
        # 保证PCB板区域被选中
        if not self.pcbImage:
            QtWidgets.QMessageBox.warning(self, '提示', '请选中PCB板区域')
            return
        # 保证至少有一个模板有图片，且被选中
        if not ((self.template_1 and check_1) or (self.template_2 and check_2)):
            QtWidgets.QMessageBox.warning(self, '提示', '请至少选中一个模板')
            return
        self.saveTemplateInfomation.emit()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = PCBLocationWidget()
    win.show()
    image = QtGui.QImage('../test.jpg')
    win.set_image(win.templateLabel_2, image)
    os._exit(app.exec())