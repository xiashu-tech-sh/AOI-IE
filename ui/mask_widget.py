from PyQt5 import QtCore, QtWidgets
from mask_widget_ui import Ui_Form
import cv2
import numpy as np
from PyQt5 import QtGui


class MaskWidget(QtWidgets.QWidget, Ui_Form):
    savePatternSignal = QtCore.pyqtSignal(name='savePatternSignal')  # 保存pattern
    selectedChanged = QtCore.pyqtSignal(str, str, name='selectedChanged')
    parameterChanged = QtCore.pyqtSignal(name='parameterChanged')  # 任何程式相关的参数变化后都必须触发该信号告知父类pattern已被修改

    def __init__(self):
        ''' Maks页面 '''
        super().__init__()
        self.setupUi(self)
        self.threshSlider.setRange(0, 255)
        self.threshSlider.sliderMoved.connect(self.threshold_changed) # 滑块响应
        self.previewLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.getCircleButton.clicked.connect(self.get_circle_button_clicked) # 提取圆心响应
        self.saveButton.clicked.connect(self.savePatternSignal)# 保存
        self.listWidget.currentRowChanged.connect(self.item_changed)
        self.reverseCheckBox.stateChanged.connect(self.checkLanguage)

        self.currentMask = None
        self.maskList = []
        self.thickness = 1
        self.lineType = 4
        self.point_color = (255, 0, 0)
    def checkLanguage(self,data ):
        if data == 2:
            self.currentMask.reverse = True
        else:
            self.currentMask.reverse = False

    def right_click_add(self):
        self.Pcanvase.menus = (QtWidgets.QMenu(), QtWidgets.QMenu())

        self.copyShapeAction = QtWidgets.QAction('复制Mask')
        self.pasteShapeAction = QtWidgets.QAction('粘贴Mask')
        self.delShapeAction = QtWidgets.QAction('删除Mask')
        # self.delShapeAction = QtWidgets.QAction('复制Mask')
        self.delShapeAction.triggered.connect(self.Pcanvase.delete_shape_action_clicked)
        self.copyShapeAction.triggered.connect(self.Pcanvase.copy_shape_action_clicke)
        self.pasteShapeAction.triggered.connect(self.Pcanvase.paste_shape_action_clicke)
        self.Pcanvase.menus[1].addAction(self.copyShapeAction)
        self.Pcanvase.menus[1].addAction(self.pasteShapeAction)
        self.Pcanvase.menus[1].addAction(self.delShapeAction)

    def set_mask(self, mask):
        self.currentMask = mask
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
            # self.listWidget.takeItem(index)  # remove row from qlistwidget
            self.update_listwidget()

    def threshold_changed(self, value):
        ''' 拖动slider后的响应函数，更新图片显示 '''
        if not self.currentMask:
            return
        self.label.setText(str(value))
        pixmap = self.currentMask.binary_threshold_changed(value)
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.parameterChanged.emit()

    def update_pixmap_show(self, enter):
        if self.currentMask:
            if enter:
                self.updete_data()
            else:
                pixmap = self.currentMask.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
                self.previewLabel.setPixmap(pixmap)

    def updete_data(self):
        # 更新数据
        rgbImage = cv2.cvtColor(self.currentMask.binaryImage, cv2.COLOR_GRAY2RGB)
        self.threshSlider.setValue(self.currentMask.binaryThreshold)
        self.reverseCheckBox.setChecked(self.currentMask.reverse)
        self.label.setText(str(self.currentMask.binaryThreshold))
        self.spinBox.setValue(self.currentMask.meter[0])
        self.spinBox_3.setValue(self.currentMask.meter[1])
        round_x, round_y = self.currentMask.round[0], self.currentMask.round[1]
        radius = self.currentMask.radius
        self.label_6.setText(
            "圆心：（%s, %s） 半径：%s" % (round_x, round_y, radius))
        cv2.circle(rgbImage, (round_x, round_y), radius, self.point_color, 2)
        # 绘制最小外接圆
        cv2.line(rgbImage, (round_x - radius, round_y), (round_x + radius, round_y),self.point_color, self.thickness, self.lineType)
        cv2.line(rgbImage, (round_x, round_y - radius),
                 (round_x, round_y + radius), self.point_color, self.thickness, self.lineType)
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
    def save_current(self):
        if not self.currentMask and not self.maskList:
            QtWidgets.QMessageBox.warning(self, '提示', '请先选择一个mask')
            return
        elif self.currentMask and self.currentMask not in self.maskList:  # 新保存
            self.maskList.append(self.currentMask)
            self.currentMask = None
            self.update_listwidget()
            count = self.listWidget.count()
            self.listWidget.setCurrentRow(count - 1)
            self.threshSlider.setValue(self.currentMask.binaryThreshold)
            self.reverseCheckBox.setChecked(False)
            self.label.setText(str(self.currentMask.binaryThreshold))
            self.label_6.setText("")
        else:  # 修改, TODO
            pass
            # self.savePatternSignal.emit()

    def paste_by_name(self, new_part):
        self.maskList.append(new_part)
        self.update_listwidget()

    def update_listwidget(self):
        self.listWidget.clear()
        for mask in self.maskList:
            self.listWidget.addItem(mask.name)
        if self.maskList:
            self.listWidget.setCurrentRow(0)  # 显示第一个mask
            self.threshSlider.setValue(self.maskList[0].binaryThreshold)

    def item_changed(self, rowIndex):
        self.currentMask = self.maskList[rowIndex]
        if self.currentMask.round:
            self.updete_data()
        else:
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

    def get_circle_button_clicked(self):
        contours, hierarchy = cv2.findContours(self.currentMask.binaryImage,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        rgbImage = cv2.cvtColor(self.currentMask.binaryImage, cv2.COLOR_GRAY2RGB)
        max_radius = self.spinBox_3.value()
        min_radius = self.spinBox.value()
        radius_list = []
        for i in contours:
            center, radius = cv2.minEnclosingCircle(i)
            center = np.int0(center)
            if center[0] - radius > 0 and center[0] + radius < rgbImage.shape[1] and min_radius < radius < max_radius :
                radius_list.append([center,int(radius)])
                # 绘制最小外接圆
                cv2.circle(rgbImage, tuple(center), int(radius),self.point_color , 2)
                cv2.line(rgbImage, (int(center[0]-radius),int(center[1])), (int(center[0]+radius),int(center[1]),), self.point_color, self.thickness, self.lineType)
                cv2.line(rgbImage, (int(center[0]), int(center[1]-radius)),
                         (int(center[0]), int(center[1]+radius)), self.point_color, self.thickness, self.lineType)
        if len(radius_list) == 0:
            QtWidgets.QMessageBox.warning(self, '提示', '未能获取圆心，请重新选择')
            return
        if len(radius_list) > 1:
            or_radius = ""
            for i in radius_list:
                or_radius+=str(i[1])+","
            QtWidgets.QMessageBox.warning(self, '提示', '获取多个圆心，请重新选择,当前获取半径 %s'%or_radius)
            return
        self.label_6.setText("圆心：（%s, %s） 半径：%s"%(str(radius_list[0][0][0]),str(radius_list[0][0][1]),str(radius_list[0][1])))
        self.currentMask.round = radius_list[0][0].tolist()
        self.currentMask.radius = radius_list[0][1]
        self.currentMask.meter = [min_radius,max_radius]
        self.currentMask.reverse = self.reverseCheckBox.isChecked()

        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.parameterChanged.emit()