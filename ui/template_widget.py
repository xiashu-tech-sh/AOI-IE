from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtGui
from template_widget2 import Ui_Form
import cv2
import numpy as np

class TemplateWidget(QtWidgets.QWidget, Ui_Form):

    savePatternSignal = QtCore.pyqtSignal(name='savePatternSignal')  # 保存pattern
    selectedChanged = QtCore.pyqtSignal(str, str, name='selectedChanged')
    parameterChanged = QtCore.pyqtSignal(name='parameterChanged')  # 任何程式相关的参数变化后都必须触发该信号告知父类pattern已被修改

    def __init__(self):
        ''' Template页面 '''
        super().__init__()
        self.setupUi(self)
        self.threshSlider.setRange(0, 255)
        self.threshSlider.valueChanged.connect(self.threshold_changed)
        self.previewLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.currentTemplate = None
        self.template = []
        self.saveButton.clicked.connect(self.savePatternSignal)
        self.listWidget.currentRowChanged.connect(self.item_changed)
        self.threshold = None
        self.num_features = None
        self.set_value = None

    def paste_by_name(self, new_part):
        self.template = new_part
        self.update_listwidget()
    # def right_click_add(self):
    #     self.Pcanvase.menus = (QtWidgets.QMenu(), QtWidgets.QMenu())
    #     self.delShapeAction = QtWidgets.QAction('删除模板')
    #     self.copyShapeAction =  QtWidgets.QAction('复制模板')
    #     self.pasteShapeAction =  QtWidgets.QAction('粘贴模板')
    #     self.delShapeAction.triggered.connect(self.Pcanvase.delete_shape_action_clicked)
    #     self.copyShapeAction.triggered.connect(self.Pcanvase.copy_shape_action_clicke)
    #     self.pasteShapeAction.triggered.connect(self.Pcanvase.paste_shape_action_clicke)
    #     self.Pcanvase.menus[1].addAction(self.copyShapeAction)
    #     self.Pcanvase.menus[1].addAction(self.pasteShapeAction)
    #     self.Pcanvase.menus[1].addAction(self.delShapeAction)
    def set_template(self, template):
        self.currentTemplate = template
        pixmap = self.currentTemplate.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)

    # def delete_by_name(self, name=''):
    #     index = -1
    #     for i, template in enumerate(self.templateList):
    #         if template.name == name:
    #             index = i
    #             break
    #     if index >= 0:
    #         self.templateList.pop(index)
    #         # self.listWidget.takeItem(index)  # remove row from qlistwidget
    #         self.update_listwidget()

    def threshold_changed(self):
        ''' 拖动slider后的响应函数，更新图片显示 '''
        if not self.currentTemplate:
            return
        diff = self.threshSlider.value()
        index = self.comboBox.currentIndex()
        self.set_value = [diff,index]
        if index == 5:
            self.threshold = [[35, 60, 90] ,[77, 255, 255]]  # 绿色阈值上下界
        elif index == 1:
            self.threshold = [[100, 43, 46],[124, 255, 255]]  # 蓝色阈值上下界
        elif index == 2:
            self.threshold = [[0, 43, 46],[diff, 255, 255]]  # 红色阈值上下界
        elif index == 3:
            self.threshold = [[26, 43, 46], [34, 255, 255]]  # 黄色阈值上下界
        elif index == 4:
            self.threshold = [[125, 43, 46], [155, 255, 255]]  # 紫色阈值上下界
        elif index == 0:
            self.threshold = [[diff, 0, 150],[180, 60, 255]]  # 白色阈值上下界
        elif index == 6:
            self.threshold = [[diff, 0, 0],[188, 255, 77]]  # 黑色阈值上下界
        # elif index == 7:
        #     self.threshold = [[0, 0, 46],[180, 43, 220]]  # 灰色阈值上下界
        img_hsv = cv2.cvtColor(self.template.cvColorImage, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, np.array(self.threshold[0]), np.array(self.threshold[1]))
        mask = cv2.medianBlur(mask, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        w_h_list = []
        for i in cnts1:  # 遍历所有的轮廓
            x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
            if x != 0:
                w_h_list.append(i)
        if w_h_list:
            cnt = max(w_h_list, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
        else:
            return
        self.num_features = [x,y,w,h]
        temp_array = self.currentTemplate.cvColorImage.copy()
        data = cv2.rectangle(temp_array, (x,y), (x+w,y+h), (0, 0, 255) , 2, 4)
        rgbImage = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.label.setText(str(self.threshSlider.value()))
    def update_pixmap_show(self):
        if self.currentTemplate:
            if self.currentTemplate.num_features:
                x,y,w,h = self.currentTemplate.num_features
                temp_array = self.currentTemplate.cvColorImage.copy()
                data = cv2.rectangle(temp_array, (x, y), (x + w, y + h), (0, 0, 255), 2, 4)
                rgbImage = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
                image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                                     QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(image)
                pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
                self.previewLabel.setPixmap(pixmap)
                self.label.setText(str(self.currentTemplate.set_value[0]))
                self.threshSlider.setValue(self.currentTemplate.set_value[0])
                self.comboBox.setCurrentIndex(self.currentTemplate.set_value[1])
            else:
                pixmap = self.currentTemplate.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
                self.previewLabel.setPixmap(pixmap)
                self.selectedChanged.emit('template', self.currentTemplate.name)


    def save_current(self):
        if not self.currentTemplate and not self.template:
            QtWidgets.QMessageBox.warning(self, '提示', '请先选择一个template')
            return
        # elif self.currentTemplate and self.currentTemplate not in self.template:  # 新保存
        #     self.template.append(self.currentTemplate)
        #     self.currentTemplate = None
        #     self.update_listwidget()
        #     count = self.listWidget.count()
        #     self.listWidget.setCurrentRow(count-1)
            # print('add new template')
        else:  # 修改, TODO
            self.template= self.currentTemplate
            self.currentTemplate = None
            self.update_listwidget()
            count = self.listWidget.count()
            self.listWidget.setCurrentRow(count - 1)
        # self.savePatternSignal.emit()

    def update_listwidget(self):
        self.listWidget.clear()
        # for i in range(len(self.templateList)):
        #     self.listWidget.addItem('template_{}'.format(i+1))
        if self.template:
            self.listWidget.addItem(self.template.name)
            if self.template:
                self.listWidget.setCurrentRow(0)  # 显示第一个template
            # self.item_changed(0)  # 显示第一个template
            # self.selectedChanged.emit('template', self.currentTemplate.name)

    def item_changed(self, rowIndex):
        if rowIndex == -1:
            return
        self.currentTemplate = self.template
        pixmap = self.currentTemplate.pixmap
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.selectedChanged.emit('template', self.currentTemplate.name)

    def set_current_template_by_name(self, name):
        for i, template in enumerate(self.template):
            if template.name == name:
                # self.listWidget.setCurrentIndex(i)
                self.listWidget.setCurrentRow(i)
                return

