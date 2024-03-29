import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from template_widget_ui import Ui_Form


class TemplateWidget(QtWidgets.QWidget, Ui_Form):

    savePatternSignal = QtCore.pyqtSignal(str, name='savePatternSignal')  # 保存pattern
    selectedChanged = QtCore.pyqtSignal(str, str, name='selectedChanged')
    parameterChanged = QtCore.pyqtSignal(name='parameterChanged')  # 任何程式相关的参数变化后都必须触发该信号告知父类pattern已被修改

    def __init__(self):
        ''' Template页面 '''
        super().__init__()
        self.setupUi(self)
        self.red_slider.valueChanged.connect(self.threshold_hue)
        self.green_slider.valueChanged.connect(self.threshold_saturation)
        self.blue_slider.valueChanged.connect(self.threshold_value)
        self.saveButton.clicked.connect(self.save_signal)
        self.pushButton.clicked.connect(self.save_signal)
        self.previewLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.listWidget.currentRowChanged.connect(self.item_changed)
        self.color_comboBox.activated.connect(self.color_uplimit)
        self.tabWidget.currentChanged['int'].connect(self.tab_index)
        self.currentTemplate = None
        self.templateList = []
        self.color_upper = None
        self.color_lower = None
        self.combox_index = 0
    def tab_index(self,index):
        if index == 0:
            self.color_upper = None
            self.color_lower = None
        else:
            self.color_upper = [180, 255, 255]
            self.color_lower = [156, 43, 46]
    def save_signal(self):
        self.savePatternSignal.emit(self.currentTemplate.name)
    def color_uplimit(self,index):
        self.combox_index = index
        # 红色上下界
        if index == 0:
            self.color_upper = [180, 255, 255]
            self.color_lower = [156, 43, 46]
            self.red_slider.setValue(156)
            self.green_slider.setValue(43)
            self.blue_slider.setValue(46)
        # 蓝色上下界
        elif index == 1:
            self.color_upper = [124, 255, 255]
            self.color_lower = [100, 43, 46]
            self.red_slider.setValue(100)
            self.green_slider.setValue(43)
            self.blue_slider.setValue(46)
        # 黄色上下界
        elif index == 2:
            self.color_upper = [34, 255, 255]
            self.color_lower = [26, 43, 46]
            self.red_slider.setValue(26)
            self.green_slider.setValue(43)
            self.blue_slider.setValue(46)
        # 绿色上下界
        elif index == 3:
            self.color_upper = [77, 255, 255]
            self.color_lower = [35, 43, 46]
            self.red_slider.setValue(35)
            self.green_slider.setValue(43)
            self.blue_slider.setValue(46)

    def threshold_hue(self):
        H = self.red_slider.value()
        S = self.green_slider.value()
        V = self.blue_slider.value()
        self.color_lower = [H,S,V]
        self.hsv_display()
        self.red_value.setText(str(H))

    def threshold_saturation(self):
        H = self.red_slider.value()
        S = self.green_slider.value()
        V = self.blue_slider.value()
        self.color_lower = [H,S,V]
        self.hsv_display()
        self.green_value.setText(str(S))

    def threshold_value(self):
        H = self.red_slider.value()
        S = self.green_slider.value()
        V = self.blue_slider.value()
        self.color_lower = [H,S,V]
        self.hsv_display()
        self.blue_value.setText(str(V))

    def hsv_display(self):
        image = self.currentTemplate.cvColorImage.copy()
        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(img_hsv, np.array(self.color_lower), np.array(self.color_upper))
        mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if cnts1:
            cnt = max(cnts1, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            if self.combox_index ==  0:
                data = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 4, 4)
            else:
                data = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 4, 4)
            rgbImage = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                                 QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(image)
            pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        else:
            pixmap = self.currentTemplate.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)

    def color_area(self):
        if self.template:
            image = self.template.cvColorImage.copy()
            r = self.template.cvColorImage[:, :, 0] > self.red
            g = self.template.cvColorImage[:, :, 1] > self.greed
            b = self.template.cvColorImage[:, :, 2] > self.blue
            image[r&g&b] = [0,0,255]
            w,h = image.shape[:-1]
            denominator = w*h
            molecular = np.sum([r & g & b])
            self.area_ratio = round(molecular / denominator,2)
            rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                                 QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(image)
            pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.previewLabel.setPixmap(pixmap)

    def set_template(self, template):
        self.currentTemplate = template
        pixmap = self.currentTemplate.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)

    def delete_by_name(self, name=''):
        index = -1
        for i, template in enumerate(self.templateList):
            if template.name == name:
                index = i
                break
        if index >= 0:
            self.templateList.pop(index)
            # self.listWidget.takeItem(index)  # remove row from qlistwidget
            self.update_listwidget()

    def threshold_changed(self, value):
        ''' 拖动slider后的响应函数，更新图片显示 '''
        if not self.currentTemplate:
            return
        # pixmap = self.currentTemplate.binary_threshold_changed(value)
        # pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        # self.previewLabel.setPixmap(pixmap)
        self.parameterChanged.emit()

    def update_pixmap_show(self):
        if self.currentTemplate:
            if self.currentTemplate.threshold[0]:
                self.tabWidget.setCurrentIndex(1)
                self.color_upper = self.currentTemplate.threshold[1]
                self.color_lower = self.currentTemplate.threshold[0]
                self.red_slider.setValue(self.currentTemplate.threshold[0][0])
                self.green_slider.setValue(self.currentTemplate.threshold[0][1])
                self.blue_slider.setValue(self.currentTemplate.threshold[0][2])
                self.color_comboBox.setCurrentIndex(self.currentTemplate.combox_index)

            else:
                self.tabWidget.setCurrentIndex(0)
                pixmap = self.currentTemplate.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
                self.previewLabel.setPixmap(pixmap)

            self.selectedChanged.emit('template', self.currentTemplate.name)

    def save_current(self):
        if not self.currentTemplate and not self.templateList:
            QtWidgets.QMessageBox.warning(self, '提示', '请先选择一个template')
            return
        elif self.currentTemplate and self.currentTemplate not in self.templateList:  # 新保存
            self.templateList.append(self.currentTemplate)
            self.currentTemplate = None
            self.update_listwidget()
            count = self.listWidget.count()
            self.listWidget.setCurrentRow(count-1)
            # print('add new template')
        else:  # 修改, TODO
            pass
        # self.savePatternSignal.emit()

    def update_listwidget(self):
        self.listWidget.clear()
        for template in self.templateList:
            self.listWidget.addItem(template.name)
        if self.templateList:
            self.listWidget.setCurrentRow(0)  # 显示第一个template
            self.item_changed(0)  # 显示第一个template
            self.selectedChanged.emit('template', self.currentTemplate.name)

    def item_changed(self, rowIndex):
        self.currentTemplate = self.templateList[rowIndex]
        if self.currentTemplate.threshold:
            self.tabWidget.setCurrentIndex(1)
            self.color_upper = self.currentTemplate.threshold[1]
            self.color_lower = self.currentTemplate.threshold[0]
            self.red_slider.setValue(self.currentTemplate.threshold[0][0])
            self.green_slider.setValue(self.currentTemplate.threshold[0][1])
            self.blue_slider.setValue(self.currentTemplate.threshold[0][2])
            self.color_comboBox.setCurrentIndex(self.currentTemplate.combox_index)
            self.hsv_display()
        else:
            self.tabWidget.setCurrentIndex(0)
            pixmap = self.currentTemplate.pixmap
            pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.previewLabel.setPixmap(pixmap)

        self.selectedChanged.emit('template', self.currentTemplate.name)

    def set_current_template_by_name(self, name):
        for i, template in enumerate(self.templateList):
            if template.name == name:
                # self.listWidget.setCurrentIndex(i)
                self.listWidget.setCurrentRow(i)
                return