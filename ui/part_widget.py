import os

import imutils
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView, QMessageBox
import numpy as np
from part_widget_ui import Ui_Form
from edit_widget_ui import Ui_Form_edit
import cv2
from PyQt5.QtGui import QFont
from canvas import Canvas
from shape import Shape
import logging

logger = logging.getLogger('main.mod.submod')

class PartWidget(QtWidgets.QWidget, Ui_Form):
    savePatternSignal = QtCore.pyqtSignal(name='savePatternSignal')  # 保存pattern
    selectedChanged = QtCore.pyqtSignal(str, str, name='selectedChanged')
    parameterChanged = QtCore.pyqtSignal(name='parameterChanged')  # 任何程式相关的参数变化后都必须触发该信号告知父类pattern已被修改
    extremely_negative_emit = QtCore.pyqtSignal(list, str, int, list, str)
    wrong_piece_emit = QtCore.pyqtSignal(list, str, str, str, str)
    color_emait = QtCore.pyqtSignal(list, str, int, list, str)

    def __init__(self):
        ''' part页面 '''
        super().__init__()
        self.setupUi(self)
        self.folder = None
        self.currentPart = None
        self.partList = []
        self.saveButton.clicked.connect(self.savePatternSignal)
        self.tableWidget.currentCellChanged.connect(self.item_changed)
        self.edit_window = None
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tab_index = -1
        self.tableWidget.clicked.connect(self.VerSectionClicked)
        # 按钮 Edit 功能
        self.editButton.clicked.connect(self.debug_shape_action_clicke)

        self.menus = (QtWidgets.QMenu(), QtWidgets.QMenu())
        self.debugShapeAction = QtWidgets.QAction('调试元件')
        self.copyShapeAction = QtWidgets.QAction('复制元件')
        self.pasteShapeAction = QtWidgets.QAction('粘贴元件')
        self.delShapeAction = QtWidgets.QAction('删除元件')
        self.debugShapeAction.triggered.connect(self.debug_shape_action_clicke)

    def right_click_add(self):

        self.Pcanvase.menus = self.menus

        self.copyShapeAction.triggered.connect(self.Pcanvase.copy_shape_action_clicke)
        self.pasteShapeAction.triggered.connect(self.Pcanvase.paste_shape_action_clicke)
        self.delShapeAction.triggered.connect(self.Pcanvase.delete_shape_action_clicked)
        self.Pcanvase.menus[1].addAction(self.debugShapeAction)
        self.Pcanvase.menus[1].addAction(self.copyShapeAction)
        self.Pcanvase.menus[1].addAction(self.pasteShapeAction)
        self.Pcanvase.menus[1].addAction(self.delShapeAction)

    def VerSectionClicked(self, index):
        self.tab_index = index.row()

    def delete_shape_action_clicked(self):
        if not self.hShape and not self.selectedShapes:
            return
        shape = self.selectedShapes.pop()
        self.deleteShape.emit(shape.shape_type, shape.name)
        self.shapes.remove(shape)

    def debug_shape_action_clicke(self):
        logger.debug("点击编辑元件按钮")
        # 实例化子窗口
        self.edit_window = EditWiget(self.partList[self.tab_index], self.folder)
        # self.edit_window.raw_imange.ng_type = "extremely_negative"
        self.edit_window.extremelyNegative.connect(self.extremely_negative_emit)
        self.edit_window.Sigtemplate.connect(self.wrong_piece_emit)
        self.edit_window.colorSignal.connect(self.color_emait)

    def set_part(self, part):
        self.currentPart = part
        pixmap = self.currentPart.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)

    def delete_by_name(self, name=''):
        index = -1
        for i, part in enumerate(self.partList):
            if part.name == name:
                index = i
                break
        if index >= 0:
            self.partList.pop(index)
            for i in range(1, len(self.partList) + 1):
                path = self.folder + "/%s.jpg" % self.partList[i - 1].name
                self.partList[i - 1].name = "part_%s" % i
                new_path = self.folder + "/%s.jpg" % self.partList[i - 1].name
                if os.path.exists(path):
                    os.rename(path, new_path)
            self.update_tablewidget()

    def paste_by_name(self, new_part):
        self.partList.append(new_part)
        self.update_tablewidget()

    def update_pixmap_show(self):
        if self.currentPart:
            pixmap = self.currentPart.pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.previewLabel.setPixmap(pixmap)
            self.selectedChanged.emit('part', self.currentPart.name)

    def save_current(self):
        if not self.currentPart and not self.partList:
            QtWidgets.QMessageBox.warning(self, '提示', '请先选择一个部件')
            return
        elif self.currentPart and self.currentPart not in self.partList:  # 新保存
            self.partList.append(self.currentPart)
            self.currentPart = None
            self.update_tablewidget()
            count = self.tableWidget.rowCount()
            self.tableWidget.setCurrentCell(count - 1, 0)
        else:
            pass

    def update_tablewidget(self):
        self.tableWidget.clearContents()
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowCount)
        self.tableWidget.setRowCount(len(self.partList))
        for i, part in enumerate(self.partList):
            name = part.name
            part_type = part.part_type
            for col, text in enumerate([name, part_type]):
                self.tableWidget.setItem(i, col, QtWidgets.QTableWidgetItem(text))
        if self.partList:
            self.tableWidget.setCurrentCell(0, 0)

    def item_changed(self, row, col, preRow, preCol):
        if row == preRow:
            return
        if row >= len(self.partList):
            return
        if row == -1:
           return
        self.currentPart = self.partList[row]
        pixmap = self.currentPart.pixmap
        pixmap = pixmap.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.selectedChanged.emit('part', self.currentPart.name)

    def set_current_part_by_name(self, name):
        for i, part in enumerate(self.partList):
            if part.name == name:
                self.tableWidget.setCurrentCell(i, 0)
                self.tab_index = i
                return


class EditWiget(QtWidgets.QWidget, Ui_Form_edit):
    # 自定义消息
    dialogSignel = pyqtSignal(int, list)
    # 极反
    extremelyNegative = QtCore.pyqtSignal(list, str, int, list, str)
    # 模板（漏件）
    Sigtemplate = QtCore.pyqtSignal(list, str, str, str, str)
    # # 颜色抽取
    colorSignal = QtCore.pyqtSignal(list, str, int, list, str)

    def __init__(self, currentPart, folder):
        super().__init__()
        self.currentParts = currentPart
        self.folder = folder
        self.setupUi(self)
        self.show()
        self.special = False
        self.type_distinguish()
        rgbImage = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2RGB)
        self.new_canvas(rgbImage)
        # 自适应的伸缩模式
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 不可编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # tableWidget 控制NG类型界面显示
        self.tableWidget.clicked.connect(self.tabel_clicked)
        # 生成模板按钮
        self.pushButton_19.clicked.connect(self.generate_template)
        self.pushButton_4.clicked.connect(self.wrong_template)
        # 检测按钮
        self.pushButton_22.clicked.connect(self.push_button)
        self.pushButton_15.clicked.connect(self.push_button)
        # 获取检测区域按钮
        self.pushButton_21.clicked.connect(self.find_button)
        self.pushButton_11.clicked.connect(self.find_button)
        #  整体扩充
        self.pushButton_2.clicked.connect(self.overall_expansion)
        # 正负极左右旋转
        self.pushButton_14.clicked.connect(self.z_f_updown)
        # 正负极上下旋转
        self.pushButton_9.clicked.connect(self.z_f_spin)
        # 正负极左右旋转
        self.pushButton_12.clicked.connect(self.f_updown)
        # 正负极上下旋转
        self.pushButton_13.clicked.connect(self.f_spin)
        # 错件类型下拉框处理
        self.NG_value.activated.connect(self.ngType)
        # 检测算法下拉框
        # self.dete_alg_value.activated.connect(self.dete_alg)
        # 提取颜色区域
        # self.pushButton_6.clicked.connect(self.extract_color)
        # self.pcb_color.currentIndexChanged.connect(self.color_part)
        # 检测按钮  生成模板
        self.pushButton_3.clicked.connect(self.color_parameter)
        # 根据元器件种类划分检测类型
        # 向上填充
        self.pushButton_6.clicked.connect(self.on_expansion)
        # 向下填充
        self.pushButton_7.clicked.connect(self.un_expansion)
        # 向左填充
        self.updown.clicked.connect(self.left_expansion)
        # 向右填充
        self.aboutButton.clicked.connect(self.right_expansion)
        # 生成模板
        self.pushButton.clicked.connect(self.cap_templ)

        # 上下检测
        self.pushButton_8.clicked.connect(self.up_dow_delete)
        # 左右检测
        self.pushButton_10.clicked.connect(self.about_delete)
        self.Z_ = 0
        self.F_ = 0
        self.rotation_angle = 0
        self.TempQimage = []
        self.TempNumpy = []
        self.pcbColor = None
        self.compColor = None
        # 二极管黑色阈值
        self.diode_value = 40
        self.type_name.setText(self.currentParts.part_type)
        # 白色阈值
        self.cap_value = 0
        self.cap_color_diff = []
        self.lower = None
        self.supplement_diff = 20
        self.po = None
        self.temp()
        # 默认提取红色
        self.color_lower = np.array([0, 43, 46])
        self.color_upper = np.array([10, 255, 255])
        self.color = 'red'
        self.area_ratio = 0
        self.set_value = None
        # 电容类型控件
        self.cap_type = self.currentParts.leak_similar
        # 电容颜色额阈值(默认白色阈值)
        self.cap_diff = 0
        logger.debug("初始化元件参数成功，当前元件名称：%s, 类型：%s"%(self.currentParts.name,self.currentParts.part_type))
        self.color_reverse = False
        self.horizontalSlider.valueChanged.connect(self.color_slider)
        self.horizontalSlider_2.valueChanged.connect(self.color_slider)
        self.horizontalSlider_3.valueChanged.connect(self.color_slider)
        self.horizontalSlider_5.valueChanged.connect(self.rotationSlider)
        self.checkBox.stateChanged.connect(self.checkLanguage)

        self.pushButton_5.clicked.connect(self.wrong_color)
    def color_parameter(self):
        label_point = [int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())]
        self.colorSignal.emit(label_point, self.currentParts.name, self.area_ratio, [self.horizontalSlider.value(),self.horizontalSlider_2.value(),self.horizontalSlider_3.value(),self.upper_limit.value(),self.color_reverse],"wrong_piece")
        logger.debug("生成模板成功。元件名称：%s"%self.currentParts.name)
    def wrong_color(self):
        self.measurements.setText(str(self.area_ratio))
    def checkLanguage(self,index ):
        self.color_reverse = True if index == 2 else False
    def rotationSlider(self):
        self.rotation_angle = self.horizontalSlider_5.value()
        self.worr_angle()

    def color_slider(self):
        red = self.horizontalSlider.value()
        greed = self.horizontalSlider_2.value()
        blue = self.horizontalSlider_3.value()
        x1, y1, x2, y2 = int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())
        image = self.currentParts.cvColorImage.copy()
        data = image[x1:y1,x2:y2]
        if self.color_reverse:
            r = data[:, :, 0] > red
            g = data[:, :, 1] > greed
            b = data[:, :, 2] > blue
        else:
            r = data[:, :, 0] < red
            g = data[:, :, 1] < greed
            b = data[:, :, 2] < blue

        w,h = data.shape[:-1]
        denominator = w*h
        molecular = np.sum([r & g & b])
        self.area_ratio = int(molecular / denominator*100)
        image[x1: y1, x2: y2][r&g&b] = [0,0,255]
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.canvas.pixmap = pixmap
        self.canvas.update()
        self.label_10.setText(str(greed))
        self.label_8.setText(str(red))
        self.label_11.setText(str(blue))
    def about_delete(self):
        self.canvas.shapes = []
        w, h = self.TempNumpy.shape[:2]
        self.stackedWidget.setCurrentIndex(3)
        positive_rectangle = [QtCore.QPoint(self.Z_, self.F_), QtCore.QPoint(25, w)]
        negative_rectangle = [QtCore.QPoint(h-25, self.F_), QtCore.QPoint(h - self.F_, w - self.Z_)]
        self.label_2.setText('Width: 15, Height: 32, vertex: (35, 43)')
        pos_list = [positive_rectangle, negative_rectangle]
        shapes = []
        for i in pos_list:
            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(i)
            shapes.append(i)
            self.canvas.shapes.append(shape)
        self.canvas.update()
        logger.debug("%s正负极检测为左右检测" % self.currentParts.name)
    def up_dow_delete(self):
        self.canvas.shapes = []
        w, h = self.TempNumpy.shape[:2]
        self.stackedWidget.setCurrentIndex(3)
        positive_rectangle = [QtCore.QPoint(self.Z_, self.F_), QtCore.QPoint(h, self.supplement_diff)]
        negative_rectangle = [QtCore.QPoint(self.Z_, w - self.Z_ - self.supplement_diff), QtCore.QPoint(h - self.F_, w - self.Z_)]
        self.label_2.setText('Width: 15, Height: 32, vertex: (35, 43)')
        pos_list = [positive_rectangle, negative_rectangle]
        shapes = []
        for i in pos_list:
            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(i)
            shapes.append(i)
            self.canvas.shapes.append(shape)
        self.canvas.update()
        logger.debug("%s正负极检测为上下检测"%self.currentParts.name)
    def button_color(self):
        index = self.pcb_color_2.currentIndex()
        if index == 5:
            lower = [[35, 60, self.cap_diff] ,[77, 255, 255]]  # 绿色阈值上下界
        elif index == 3:
            lower = [[100, 43, self.cap_diff],[124, 255, 255]]  # 蓝色阈值上下界
        elif index == 2:
            lower = [[0, 43, self.cap_diff],[10, 255, 255]]  # 红色阈值上下界
        elif index == 4:
            lower = [[26, 43, self.cap_diff], [34, 255, 255]]  # 黄色阈值上下界
        elif index == 6:
            lower = [[125, 43, self.cap_diff], [155, 255, 255]]  # 紫色阈值上下界
        elif index == 0:
            lower = [[self.cap_diff, 0, 150],[180, 60, 255]]  # 白色阈值上下界
        elif index == 1:
            lower = [[self.cap_diff, 0, 0],[188, 255, 77]]  # 黑色阈值上下界
        else:
            lower = [[self.cap_diff, 0, 46],[180, 43, 220]]  # 灰色阈值上下界
        self.cap_color_diff = lower
        img_hsv = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(img_hsv, np.array(lower[0]), np.array(lower[1]))
        mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测 #红色
        if cnts1:
            cnt = max(cnts1, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            return x, y, w, h
        else:
            return 0,0,0,0
    def capa_down(self,index):
        if index == 5:
            self.cap_diff = 90 # 绿色阈值上下界
            logger.debug("选择元件颜色绿色")
        elif index == 3:
            self.cap_diff = 46  # 蓝色阈值上下界
            logger.debug("选择元件颜色蓝色")
        elif index == 2:
            self.cap_diff =  0  # 红色阈值上下界
            logger.debug("选择元件颜色红色")
        elif index == 4:
            self.cap_diff = 46 # 黄色阈值上下界
            logger.debug("选择元件颜色黄色")
        elif index == 6:
            self.cap_diff = 46 # 紫色阈值上下界
            logger.debug("选择元件颜色紫色")
        elif index == 0:
            self.cap_diff = 50  # 白色阈值上下界
            logger.debug("选择元件颜色白色")
        elif index == 1:
            self.cap_diff = 47 # 黑色阈值上下界
            logger.debug("选择元件颜色黑色")
        else:
            self.cap_diff = 0  # 灰色阈值上下界
            logger.debug("选择元件颜色灰色")
        self.canvas.shapes = []
        x, y, w, h = self.button_color()
        component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w + x, h + y)]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
    def cap_templ(self):
        x1, y1, x2, y2 = int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())
        self.TempNumpy = self.currentParts.cvColorImage[x1: y1, x2: y2]
        path = self.folder + "/%s.jpg" % self.currentParts.name
        rgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_BGR2RGB)
        qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                              QtGui.QImage.Format_RGB888)
        image_qtdata = QtGui.QPixmap.fromImage(qt_img)
        self.TempQimage = image_qtdata.scaled(self.template_image_2.size(), QtCore.Qt.KeepAspectRatio)
        # 灰度图转换
        hrgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_RGB2GRAY)
        hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                               QtGui.QImage.Format_Indexed8)
        himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
        hQPixmapImage = himage_qtdata.scaled(self.template_image_3.size(), QtCore.Qt.KeepAspectRatio)
        label_point = [x1, y1, x2, y2]
        # 保存数据(相对元器件坐标点，元器件名称，类型，图片路径，相似度, 模板字)
        self.template_image_2.setPixmap(self.TempQimage)
        self.template_image_3.setPixmap(hQPixmapImage)
        cv2.imwrite(path, self.TempNumpy)
        self.po = self.canvas.shapes[0].points
        self.Sigtemplate.emit(self.cap_color_diff, self.currentParts.name, "missing_parts", path, self.cap_type)
        logger.debug("生成模板成功。元件名称：%s"%self.currentParts.name)
    def overall_expansion(self):
        self.canvas.shapes=[]
        x, y, w, h = self.color_match(self.currentParts.cvColorImage)
        w = self.currentParts.cvColorImage.shape[1] if x+w+20 > self.currentParts.cvColorImage.shape[1] else x+w+20
        h = self.currentParts.cvColorImage.shape[0] if y + h + 20 > self.currentParts.cvColorImage.shape[
            0] else y + h + 20
        x = 0 if x - 20 < 0 else x - 20
        y = 0 if y - 20 < 0 else y - 20

        component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w , h )]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        self.cap_type = "overall"
        logger.debug("整体填充元件")
    def on_expansion(self):
        self.canvas.shapes = []
        x, y, w, h = self.color_match(self.currentParts.cvColorImage)
        pos1 = QtCore.QPoint(w + x, h + y)
        y = 0 if y - 20 < 0 else y - 20
        component_rectangle = [QtCore.QPoint(x, y),pos1 ]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        self.cap_type = "on"
        logger.debug("向上填充元件")
    def un_expansion(self):
        self.canvas.shapes = []
        x, y, w, h = self.color_match(self.currentParts.cvColorImage)
        pos = QtCore.QPoint(x, y)
        h = self.currentParts.pixmap.height() if y + h + 20 > self.currentParts.pixmap.height() else y + h + 20
        component_rectangle = [pos,QtCore.QPoint(w + x, h) ]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        self.cap_type = "under"
        logger.debug("向下填充元件")
    def left_expansion(self):
        self.canvas.shapes = []
        x, y, w, h = self.color_match(self.currentParts.cvColorImage)
        pos = QtCore.QPoint(w+x, h + y)
        x = 0 if x - 20 < 0 else x - 20
        component_rectangle = [QtCore.QPoint(x, y),pos]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        self.cap_type = "left"
        logger.debug("向左填充元件")
    def right_expansion(self):
        self.canvas.shapes = []
        x, y, w, h = self.color_match(self.currentParts.cvColorImage)
        print("h",h)
        w = self.currentParts.pixmap.width() if x + w + 20 > self.currentParts.pixmap.width() else x + w + 20
        print("h1", h)
        component_rectangle = [QtCore.QPoint(x, y),QtCore.QPoint(w , h+y ) ]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        self.cap_type = "right"
        logger.debug("向右填充元件")
    def diode_changed(self):
        self.canvas.shapes = []
        self.label.setText(str(self.diode_value))
        x, y, w, h = self.diode_color()
        component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w + x, h + y)]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        logger.debug("创建模板界面，调整颜色阈值为：%s" % self.diode_value)
    def cap_changed(self):
        self.canvas.shapes = []
        x, y, w, h = self.button_color()
        component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w + x, h + y)]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()
        logger.debug("创建模板界面，调整颜色阈值为：%s"%self.cap_value)
    def color_get(self,index):
        if index == 0:
            self.lower = [[35, 60, 90] ,[77, 255, 255]]  # 绿色阈值上下界
        elif index == 1:
            self.lower = [[100, 43, 46],[124, 255, 255]]  # 蓝色阈值上下界
        elif index == 2:
            self.lower = [[0, 43, 46],[10, 255, 255]]  # 红色阈值上下界
        elif index == 3:
            self.lower = [[26, 43, 46], [34, 255, 255]]  # 黄色阈值上下界
        elif index == 4:
            self.lower = [[125, 43, 46], [155, 255, 255]]  # 紫色阈值上下界
        elif index == 5:
            self.lower = [[0, 0, 150],[180, 60, 255]]  # 白色阈值上下界
        elif index == 6:
            self.lower = [[47, 0, 0],[188, 255, 77]]  # 黑色阈值上下界
        elif index == 7:
            self.lower = [[0, 0, 46],[180, 43, 220]]  # 灰色阈值上下界
        img_hsv = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, np.array(self.lower[0]), np.array(self.lower[1]))
        mask = cv2.medianBlur(mask, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        w_h_list = []
        for i in cnts1:  # 遍历所有的轮廓
            x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
            if x != 0:
                w_h_list.append(i)
        if w_h_list:
            cnt = max(w_h_list, key=cv2.contourArea)
            return cnt
        # else:
        #     self.box = QMessageBox(QMessageBox.Warning, "警告框", "未匹配到颜色")
        #     self.box.addButton(self.tr("确定"), QMessageBox.YesRole)
        #     self.box.exec_()
    def black_diode(self):
        img_hsv = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 0, 0])
        upper = np.array([180, self.diode_value, 46])
        shapeMask = cv2.inRange(img_hsv, lower, upper)
        # 在mask中寻找轮廓
        cnts = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if cnts:
            cnt = max(cnts, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
            return x,y,w,h
        else:
            return 0,0,0,0
    def detect_button(self):
        self.canvas.shapes=[]
        pcv_index = self.pcb_color.currentIndex()
        if pcv_index == comp_index:
            cnt = self.color_get(6)  # 黑色阈值上界
        else:
            cnt = self.color_get(comp_index)
        if self.currentParts.part_type == "capacitor":
            x, y, w, h = self.color_match(self.currentParts.cvColorImage)
            component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w, h)]
            self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(w,h,x,y))
        elif self.currentParts.part_type == "diode":
            x,y,w,h = self.black_diode()
            component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(x+w, y+h)]
            self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(w,h,x,y))
        else:
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            self.lower.append([w,h])
            component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(x+w, y+h)]
            self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(w,h,x,y))
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)
        self.canvas.update()

    def z_f_updown(self):
        for i,shape in enumerate(self.canvas.shapes):
            if i ==0:
                if shape.points[0].x() + 10>self.canvas.pixmap.width()-self.supplement_diff:
                    shape.points[0] = QtCore.QPoint(self.canvas.pixmap.width()-self.supplement_diff,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(self.canvas.pixmap.width(), shape.points[1].y())
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() + 10,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() + 10, shape.points[1].y())
            elif i ==1:
                if shape.points[0].x() - 10<=0:
                    shape.points[0] = QtCore.QPoint(0,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(self.supplement_diff, shape.points[1].y())
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() - 10,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() - 10, shape.points[1].y())
        self.canvas.update()

    def z_f_spin(self):
        for i,shape in enumerate(self.canvas.shapes):
            if i ==0:
                if shape.points[1].y() +10>= self.canvas.pixmap.height():
                    shape.points[0] = QtCore.QPoint(shape.points[0].x(), self.canvas.pixmap.height()-self.supplement_diff)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x(), self.canvas.pixmap.height())
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() ,shape.points[0].y() +10)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() , shape.points[1].y()+10)
            elif i ==1:
                if shape.points[1].y() -40<=0:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() ,0)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x(), self.supplement_diff)
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() ,shape.points[0].y() -10)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() , shape.points[1].y() - 10)
        self.canvas.update()

    def f_updown(self):
        for i,shape in enumerate(self.canvas.shapes):
            if i ==0:
                if shape.points[0].x() - 10<=0:
                    shape.points[0] = QtCore.QPoint(0,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(self.supplement_diff, shape.points[1].y())
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x()- 10,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() - 10, shape.points[1].y())
            elif i ==1:
                if shape.points[0].x() + 40>self.canvas.pixmap.height():
                    shape.points[0] = QtCore.QPoint(self.canvas.pixmap.height()-self.supplement_diff,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(self.canvas.pixmap.height(), shape.points[1].y())
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() + 10,shape.points[0].y() )
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() + 10, shape.points[1].y())
        self.canvas.update()

    def f_spin(self):
        for i,shape in enumerate(self.canvas.shapes):
            if i ==0:
                if shape.points[0].y() - 10 <= 0:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x(), 0)
                    shape.points[1] = QtCore.QPoint(shape.points[0].x()+self.supplement_diff, self.supplement_diff)
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x(), shape.points[0].y() - 10)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x(), shape.points[1].y() - 10)

            elif i ==1:
                if shape.points[1].y()+10 >= self.canvas.pixmap.height():
                    shape.points[0] = QtCore.QPoint(shape.points[0].x(), self.canvas.pixmap.height()-self.supplement_diff)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x(), self.canvas.pixmap.height())
                else:
                    shape.points[0] = QtCore.QPoint(shape.points[0].x() ,shape.points[0].y() +10)
                    shape.points[1] = QtCore.QPoint(shape.points[1].x() , shape.points[1].y() + 10)
        self.canvas.update()

    def new_canvas(self,rgbImage):
        self.canvas = Canvas()
        # 缩放因子
        self.canvas.scale = 1
        # 编辑模式
        self.canvas.CREATE = 0

        # self.canvas.shapes.append(i)
        self.scrollBars = {
            Qt.Vertical: self.scrollArea.verticalScrollBar(),
            Qt.Horizontal: self.scrollArea.horizontalScrollBar(),
        }
        image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.canvas.loadPixmap(pixmap)
        self.scrollArea.setWidget(self.canvas)
        self.zoomValue = 100.0  # 缩放尺度，100为原始尺寸
        self.canvas.zoomRequest.connect(self.zoomRequest)  # 缩放事件，按住ctrl+鼠标滚轮后触发
        self.canvas.scrollRequest.connect(self.scrollRequest)  # 滚轮直接滚动：上下sroll； 按住alt+滚轮：左右scroll
        # self.canvas.newShape.connect(self.new_shape)           # shape被拖动或者shape的角点被拖动后，左键释放后触发
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)  # EDIT阶段，鼠标选中的Shape发生变化后触发，CREATE阶段不触发
        self.canvas.testSelected.connect(self.test_show)
        # 测试定义类型
        self.canvas.shape_type = 'pos_neg'



    def extract_color(self):
        x1, y1, x2, y2 = int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())
        pcv_numpy = self.currentParts.cvColorImage[x1: y1, x2: y2]

        rgbImage = cv2.cvtColor(pcv_numpy, cv2.COLOR_BGR2RGB)
        frame = cv2.GaussianBlur(pcv_numpy, (5, 5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        # 图像学膨胀腐蚀
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        # 寻找轮廓并绘制轮廓
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        w,h ,z = frame.shape
        if len(cnts) > 0:
            cnt = max(cnts, key=cv2.contourArea)
            min_rect = cv2.minAreaRect(cnt)
            area_min = min_rect[1][0]*min_rect[1][1]
            percentage = int(area_min/(w*h)*100)
            self.start_interval_5.setText(str(percentage))
        else:
            self.box = QMessageBox(QMessageBox.Warning, "警告框", "未匹配到颜色")
            self.box.addButton(self.tr("确定"), QMessageBox.YesRole)
            self.box.exec_()
            return

        qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                              QtGui.QImage.Format_RGB888)
        image_qtdata = QtGui.QPixmap.fromImage(qt_img)
        QPixmapImage = image_qtdata.scaled(self.template_image.size(), QtCore.Qt.KeepAspectRatio)
        # 灰度图转换
        hrgbImage = cv2.cvtColor(pcv_numpy, cv2.COLOR_RGB2GRAY)
        hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                               QtGui.QImage.Format_Indexed8)
        himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
        hQPixmapImage = himage_qtdata.scaled(self.template_image.size(), QtCore.Qt.KeepAspectRatio)

        label_point = [x1, y1, x2, y2]

        # 保存数据(相对元器件坐标点，元器件名称，类型，图片路径，相似度, 模板字)
        self.template_image_5.setPixmap(QPixmapImage)
        self.template_image_3.setPixmap(hQPixmapImage)
        self.colorSignal.emit(label_point, self.currentParts.name, "wrong_piece", self.color, percentage,self.set_value)

    def type_distinguish(self):
        if self.currentParts.part_type in [ "component","capacitor"]:
            self.type_control(["漏件", "极反", "错件"])
            self.stackedWidget_2.setCurrentIndex(1)
        elif self.currentParts.part_type in ["resistor","slot","ceramics"]:
            self.type_control(["错件"])
            self.NG_value.setCurrentIndex(2)
            self.dete_alg_value.setCurrentIndex(4)
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_2.setCurrentIndex(0)
        elif self.currentParts.part_type == "diode":
            self.type_control(["错件", "极反"])
            self.NG_value.setCurrentIndex(2)
            self.dete_alg_value.setCurrentIndex(4)
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_2.setCurrentIndex(1)

    def special_element(self):
        self.canvas.shapes = []
        component_rectangle = [QtCore.QPoint(35, 20), QtCore.QPoint(90, 100)]
        self.label_2.setText('Width: 55, Height: 70, vertex: (35, 20)')
        shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        shape.points.extend(component_rectangle)
        self.canvas.shapes.append(shape)

        if self.currentParts.erron_pos:
            self.canvas.shapes[0].points = [
                QtCore.QPoint(self.currentParts.leak_pos[2], self.currentParts.leak_pos[0]),
                QtCore.QPoint(self.currentParts.leak_pos[3], self.currentParts.leak_pos[1])]
            pcv_numpy = cv2.imread(self.folder + "/%s.jpg" % self.currentParts.name)
            rgbImage = cv2.cvtColor(pcv_numpy, cv2.COLOR_BGR2RGB)
            qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)
            image_qtdata = QtGui.QPixmap.fromImage(qt_img)
            QPixmapImage = image_qtdata.scaled(self.template_image_4.size(), QtCore.Qt.KeepAspectRatio)
            # 灰度图转换
            hrgbImage = cv2.cvtColor(pcv_numpy, cv2.COLOR_RGB2GRAY)
            hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                                   QtGui.QImage.Format_Indexed8)
            himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
            hQPixmapImage = himage_qtdata.scaled(self.template_image_3.size(), QtCore.Qt.KeepAspectRatio)
            self.template_image_4.setPixmap(QPixmapImage)
            self.template_image_3.setPixmap(hQPixmapImage)
            self.template_image_5.setPixmap(QPixmapImage)
            self.similarValue.setValue(self.currentParts.leak_similar)
    def color_match(self,image_num):
        try:
            self.cap_color_diff[0] = ([self.cap_value, 0, 221])
            self.cap_color_diff[1] = ([180, 30, 255])
        except IndexError:
            self.cap_color_diff.append([self.cap_value, 0, 221])
            self.cap_color_diff.append([180, 30, 255])
        lower_red = np.array(self.cap_color_diff[0])  # 白色阈值下界
        higher_red = np.array(self.cap_color_diff[1])  # 白色阈值上界
        img_hsv = cv2.cvtColor(image_num, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(img_hsv, lower_red, higher_red)  # 可以认为是过滤出红色部分，获得红色的掩膜
        mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        if cnts1:
            cnt = max(cnts1, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            return x, y, w, h
        else:
            return 0,0,0,0
    def diode_color(self):
        if index == 0:
            self.lower = [[35, 60, 90] ,[77, 255, 255]]  # 绿色阈值上下界
            logger.debug("元件颜色为绿色")
        elif index == 1:
            logger.debug("元件颜色为蓝色")
            self.lower = [[100, 43, 46],[124, 255, 255]]  # 蓝色阈值上下界
        elif index == 2:
            logger.debug("元件颜色为红色")
            self.lower = [[0, 43, 46],[10, 255, 255]]  # 红色阈值上下界
        elif index == 3:
            logger.debug("元件颜色为黄色")
            self.lower = [[26, 43, 46], [34, 255, 255]]  # 黄色阈值上下界
        elif index == 4:
            logger.debug("元件颜色为紫色")
            self.lower = [[125, 43, 46], [155, 255, 255]]  # 紫色阈值上下界
        elif index == 5:
            logger.debug("元件颜色为白色")
            self.lower = [[0, 0, 150],[180, 60, 255]]  # 白色阈值上下界
        elif index == 6:
            logger.debug("元件颜色为黑色")
            self.lower = [[0, 0, 0],[180, self.diode_value, 46]]  # 黑色阈值上下界
        elif index == 7:
            logger.debug("元件颜色为灰色")
            self.lower = [[0, 0, 46],[180, 43, 220]]  # 灰色阈值上下界
        img_hsv = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, np.array(self.lower[0]), np.array(self.lower[1]))
        mask = cv2.medianBlur(mask, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        w_h_list = []
        for i in cnts1:  # 遍历所有的轮廓
            x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
            if x != 0:
                w_h_list.append(i)
        if w_h_list:
            cnt = max(w_h_list, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            return x, y, w, h
        else:
            return 0, 0, 0, 0
    def temp(self):
        self.canvas.shapes = []
        if self.currentParts.part_type == "capacitor":
            self.stackedWidget.setCurrentIndex(1)
            x,y,w,h = self.color_match(self.currentParts.cvColorImage)
            component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w+x, h+y)]
            self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(w,h,x,y))
            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(component_rectangle)
            self.canvas.shapes.append(shape)
        # elif self.currentParts.part_type == "slot":
        #     component_rectangle = [QtCore.QPoint(35, 20), QtCore.QPoint(90, 100)]
        #     self.label_2.setText('Width: 55, Height: 70, vertex: (35, 20)')
        #     shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
        #     shape.points.extend(component_rectangle)
        #     self.canvas.shapes.append(shape)
        elif self.currentParts.part_type == "diode":
            x,y,w,h = self.diode_color()
            component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(w+x, h+y)]
            self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(w,h,x,y))
            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(component_rectangle)
            self.canvas.shapes.append(shape)
            self.label.setText(str(self.diode_value))
        elif self.currentParts.part_type in ["ceramics", "resistor","slot"]:
            component_rectangle = [QtCore.QPoint(35, 20), QtCore.QPoint(90, 100)]
            self.label_2.setText('Width: 55, Height: 80, vertex: (35, 20)')
            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(component_rectangle)
            self.canvas.shapes.append(shape)
            if self.currentParts.leak_pos:
                x,y,w,h = self.currentParts.leak_pos
                self.canvas.shapes[0].points = [QtCore.QPoint(x, w), QtCore.QPoint(h, y)]
                self.horizontalSlider.setValue(self.currentParts.erron_pos[0]),
                self.horizontalSlider_2.setValue(self.currentParts.erron_pos[1])
                self.horizontalSlider_3.setValue(self.currentParts.erron_pos[2])
                self.label_10.setText(str(self.currentParts.erron_pos[0]))
                self.label_8.setText(str(self.currentParts.erron_pos[1]))
                self.label_11.setText(str(self.currentParts.erron_pos[2]))
                self.upper_limit.setValue(self.currentParts.erron_pos[3])
                self.checkBox.setChecked(self.currentParts.erron_pos[4])
                self.color_reverse = self.currentParts.erron_pos[4]
                self.color_slider()
                self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(h-x,y-w,x,w))

        else:
            self.stackedWidget.setCurrentIndex(4)
            component_rectangle = [QtCore.QPoint(35, 20), QtCore.QPoint(90, 100)]
            self.label_2.setText('Width: 55, Height: 70, vertex: (35, 20)')
            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(component_rectangle)
            self.canvas.shapes.append(shape)
        path = self.folder + "/%s.jpg" % self.currentParts.name
        if os.path.exists(path):
            logger.debug("加载元件模板图片")
            if self.currentParts.part_type == "capacitor":
                img_hsv = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2HSV)
                mask_red = cv2.inRange(img_hsv, np.array(self.currentParts.leak_pos[0]), np.array(self.currentParts.leak_pos[1]))
                mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
                cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测 #红色
                if cnts1:
                    cnt = max(cnts1, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
                    h = y+h
                    w = x+w
                    if self.currentParts.leak_similar == "overall":
                        logger.debug("元件为整体填充")
                        x = 0 if x - self.supplement_diff  < 0 else x - self.supplement_diff
                        y = 0 if y - self.supplement_diff < 0 else y - self.supplement_diff
                        w = self.currentParts.h if w + self.supplement_diff > self.currentParts.h else w + self.supplement_diff
                        h = self.currentParts.w if h + self.supplement_diff > self.currentParts.w else h + self.supplement_diff
                    elif self.currentParts.leak_similar == "on":
                        logger.debug("元件为向上填充")
                        y = 0 if y - self.supplement_diff < 0 else y - self.supplement_diff
                    elif self.currentParts.leak_similar == "under":
                        logger.debug("元件为向下填充")
                        h = self.currentParts.w if h + self.supplement_diff > self.currentParts.w else h + self.supplement_diff
                    elif self.currentParts.leak_similar == "left":
                        logger.debug("元件为向左填充")
                        x = 0 if x - self.supplement_diff < 0 else x - self.supplement_diff
                    elif self.currentParts.leak_similar == "right":
                        logger.debug("元件为向右填充")
                        w = self.currentParts.h if w + self.supplement_diff > self.currentParts.h else w + self.supplement_diff
                    self.po = self.canvas.shapes[0].points = [ QtCore.QPoint(x, y),QtCore.QPoint(w, h)]
                    self.TempNumpy = self.currentParts.cvColorImage[y:h,x:w]
            elif self.currentParts.part_type in ["diode","slot"]:
                self.pcb_color.setCurrentIndex(int(self.currentParts.leak_similar[1]))
                img_hsv = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(img_hsv, np.array(self.currentParts.leak_pos[0]), np.array(self.currentParts.leak_pos[1]))
                mask = cv2.medianBlur(mask, 7)  # 中值滤波
                cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
                cnt = max(cnts1, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
                self.canvas.shapes[0].points = [QtCore.QPoint(x, y), QtCore.QPoint(x+w, y+h)]
                self.TempNumpy = self.currentParts.cvColorImage[y:y+h, x:x+w]

            else:
                self.TempNumpy = cv2.imread(self.folder + "/%s.jpg" % self.currentParts.name)
                self.canvas.shapes[0].points = [
                    QtCore.QPoint(self.currentParts.leak_pos[2], self.currentParts.leak_pos[0]),
                    QtCore.QPoint(self.currentParts.leak_pos[3], self.currentParts.leak_pos[1])]
                x = self.currentParts.leak_pos[0]
                y = self.currentParts.leak_pos[2]
                w = self.currentParts.leak_pos[3] - self.currentParts.leak_pos[2]
                h = self.currentParts.leak_pos[1] - self.currentParts.leak_pos[0]

            rgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_BGR2RGB)
            qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)
            image_qtdata = QtGui.QPixmap.fromImage(qt_img)
            self.TempQimage = image_qtdata.scaled(self.template_image_2.size(), QtCore.Qt.KeepAspectRatio)
            # 灰度图转换
            hrgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_RGB2GRAY)
            hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                                   QtGui.QImage.Format_Indexed8)
            himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
            hQPixmapImage = himage_qtdata.scaled(self.template_image_3.size(), QtCore.Qt.KeepAspectRatio)
            # self.template_image_5.setPixmap(self.TempQimage)
            self.template_image_2.setPixmap(self.TempQimage)
            self.template_image_3.setPixmap(hQPixmapImage)
            self.template_image_5.setPixmap(self.TempQimage)

            self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w,h,x,y))
        self.canvas.update()
    def find_button(self):
        x, y = int(self.canvas.shapes[0].points[0].x()), int(self.canvas.shapes[0].points[0].y())
        x1, y1 = int(self.canvas.shapes[0].points[1].x()), int(self.canvas.shapes[0].points[1].y())
        if self.cap_type == "overall":
            self.label_33.setFont(QFont("微软雅黑", 8))
            self.label_33.setText("ROI坐标点 (1)x, y %s; \n (2)x1, y1 %s" % ((x, y), (x1, y1)))
        else:
            self.label_20.setFont(QFont("微软雅黑", 8))
            self.label_20.setText("ROI坐标点 (1)x, y %s; \n (2)x1, y1 %s" % ((x, y), (x1, y1)))
    def test_show(self, list_pos):
        width = int(list_pos[1].x() - list_pos[0].x())
        height = int(list_pos[1].y() - list_pos[0].y())
        vertex = (int(list_pos[0].x()), int(list_pos[0].y()))

        self.label_2.setText('Width: %s, Height: %s, vertex: %s' % (width, height, vertex))

    def tabel_clicked(self, index):
        try:
            index = index.row()
        except AttributeError: # 通过NG类型下拉框进入
            index = index
        if index == 0:
            logger.debug("选择漏检编辑")
            rgbImage = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2RGB)
            self.new_canvas(rgbImage)
            if self.currentParts.part_type == "capacitor":
                self.NG_value.setCurrentIndex(0)
                self.dete_alg_value.setCurrentIndex(4)
                self.stackedWidget.setCurrentIndex(5)
            elif self.currentParts.part_type in ["resistor", "slot","diode"]:
                self.NG_value.setCurrentIndex(2)
                self.dete_alg_value.setCurrentIndex(4)
                self.stackedWidget.setCurrentIndex(0)
                self.canvas.shapes = []
            else:
                self.NG_value.setCurrentIndex(index)
                self.dete_alg_value.setCurrentIndex(index)
                self.stackedWidget.setCurrentIndex(4)
            self.temp()
        elif index == 1:
            logger.debug("选择极反编辑")
            self.NG_value.setCurrentIndex(index)
            self.dete_alg_value.setCurrentIndex(index)
            self.stackedWidget.setCurrentIndex(index)
            self.template_image_3.setPixmap(QPixmap(""))
            self.canvas.shapes = []
            if len(self.TempNumpy)>0:
                rgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_BGR2RGB)
                w, h = self.TempNumpy.shape[:2]
                self.new_canvas(rgbImage)
            else:
                self.canvas.loadPixmap("")
                return
            if self.currentParts.part_type == "capacitor":
                self.NG_value.setCurrentIndex(1)
                self.dete_alg_value.setCurrentIndex(1)
                if self.cap_type == "overall":
                    self.stackedWidget.setCurrentIndex(5)
                    positive_rectangle = [QtCore.QPoint(self.Z_, self.F_), QtCore.QPoint(self.supplement_diff, self.supplement_diff)]
                    negative_rectangle = [QtCore.QPoint(h-self.Z_-self.supplement_diff, w-self.F_-self.supplement_diff), QtCore.QPoint(h-self.F_,w-self.Z_)]
                    self.label_2.setText('Width: 20, Height: 20, vertex: (0, 0)')
                else:
                    self.stackedWidget.setCurrentIndex(3)
                    positive_rectangle = [QtCore.QPoint(self.Z_, self.F_), QtCore.QPoint(h, self.supplement_diff)]
                    negative_rectangle = [QtCore.QPoint(self.Z_, w - self.Z_ - self.supplement_diff), QtCore.QPoint(h - self.F_, w - self.Z_)]
                    self.label_2.setText('Width: %s, Height: 20, vertex: (0, 0)'%h)
            elif self.currentParts.part_type in ["slot", "diode"] :
                self.stackedWidget.setCurrentIndex(3)
                positive_rectangle = [QtCore.QPoint(self.Z_, self.F_), QtCore.QPoint(h, self.supplement_diff)]
                negative_rectangle = [QtCore.QPoint(self.Z_, w-self.Z_-self.supplement_diff), QtCore.QPoint( h-self.F_,w-self.Z_)]
                self.label_2.setText('Width: %s, Height: 20, vertex: (0, 0)'% h)
            else:
                self.stackedWidget.setCurrentIndex(3)
                positive_rectangle = [QtCore.QPoint(0, 0), QtCore.QPoint(self.supplement_diff, self.supplement_diff)]
                negative_rectangle = [QtCore.QPoint(h-self.supplement_diff, w-self.supplement_diff), QtCore.QPoint(h, w)]
                self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)'%(h,w,0,0))
            self.canvas.arrow_start = QPointF(50, 59)
            self.canvas.arrow_end = QPointF(70, 59)
            pos_list = [positive_rectangle, negative_rectangle]
            shapes = []
            for i in pos_list:
                shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
                shape.points.extend(i)
                shapes.append(i)
                self.canvas.shapes.append(shape)

            if self.currentParts.Z_F_pos:
                logger.debug("已存在，加载并绘制正负极数据")
                self.canvas.shapes = []
                for i in range(2):
                    x, y = int(self.currentParts.Z_F_pos[i][2]), int(self.currentParts.Z_F_pos[i][0])
                    x1, y1 = int(self.currentParts.Z_F_pos[i][3]), int(self.currentParts.Z_F_pos[i][1])
                    component_rectangle = [QtCore.QPoint(x, y), QtCore.QPoint(x1,y1)]
                    self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))
                    shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
                    shape.points.extend(component_rectangle)
                    self.canvas.shapes.append(shape)
                    if i == 1:
                        if self.canvas.shapes[1][0].x() - self.canvas.shapes[0][1].x() <= 5:
                            self.canvas.arrow_start = QPointF(
                                (self.canvas.shapes[0][1].x() - self.canvas.shapes[0][0].x()) // 2 +
                                self.canvas.shapes[0][0].x(),
                                self.canvas.shapes[0][1].y())
                            self.canvas.arrow_end = QPointF(
                                (self.canvas.shapes[1][1].x() - self.canvas.shapes[1][0].x()) // 2 +
                                self.canvas.shapes[1][0].x(),
                                self.canvas.shapes[1][0].y() - 5, )
                        else:
                            self.canvas.arrow_end = QPointF(x - 5, (y1 - y) // 2 + y)
                    else:
                        self.canvas.arrow_start = QPointF(x1, (y1 - y) // 2 + y)
                difference = int(self.currentParts.Z_gray - self.currentParts.F_gray)
                strT = '<span style=\" color: #ff0000;\">%s</span>' % difference  # 红色
                if self.cap_type == "overall":
                    self.label_37.setText("%s" % (strT))  # 界面显示
                    # grayscale = [int(positive_mean), int(negative_mean), self.g_PN_threshold_value.value() ]
                    # self.g_PN_threshold_value.value = threshold_value
                    if difference > 0:
                        self.label_38.setText("正极")
                    else:
                        self.label_38.setText("负极")
                else:
                    self.label_26.setText("%s" % (strT))  # 界面显示
                    # grayscale = [int(positive_mean), int(negative_mean), self.g_PN_threshold_value.value() ]
                    # self.g_PN_threshold_value.value = threshold_value
                    if difference > 0:
                        self.label_25.setText("正极")
                    else:
                        self.label_25.setText("负极")

                w = self.currentParts.Z_F_pos[0][3] - self.currentParts.Z_F_pos[0][2]
                h = self.currentParts.Z_F_pos[0][1] - self.currentParts.Z_F_pos[0][0]
                self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (
                w, h, self.currentParts.Z_F_pos[0][0], self.currentParts.Z_F_pos[0][2]))

            self.canvas.update()
        elif index == 2:
            logger.debug("选择错件编辑")
            self.NG_value.setCurrentIndex(index)
            self.dete_alg_value.setCurrentIndex(index)
            self.stackedWidget.setCurrentIndex(index)
            self.template_image_3.setPixmap(QPixmap(""))
            self.canvas.shapes = []
            if self.po:
                rgbImage = cv2.cvtColor(self.currentParts.cvColorImage, cv2.COLOR_BGR2RGB)
                self.new_canvas(rgbImage)
                if self.currentParts.part_type == "capacitor":
                    self.worr_angle()
                else:
                    self.wrong_pos = [QtCore.QPoint(0, 0), QtCore.QPoint(self.supplement_diff, self.supplement_diff)]
                    self.label_2.setText('Width: 20, Height: 20, vertex: (0, 0)')
            else:
                self.canvas.loadPixmap("")
                return

            shape = Shape(shape_type="pos_neg", name=self.currentParts.name)
            shape.points.extend(self.wrong_pos)
            self.canvas.shapes.append(shape)

            if self.currentParts.erron_pos:
                logger.debug("已存在，加载并绘制错件数据")
                self.canvas.shapes[0].points = [
                    QtCore.QPoint(int(self.currentParts.erron_pos[2]), int(self.currentParts.erron_pos[0])),
                    QtCore.QPoint(int(self.currentParts.erron_pos[3]), int(self.currentParts.erron_pos[1]))]

                if self.currentParts.part_type == "capacitor":
                    self.rotation_angle = int(self.currentParts.rotation_angle)
                    self.horizontalSlider_5.setValue(self.rotation_angle)
                    # 灰度图转换
                    hrgbImage = cv2.cvtColor(self.worr_image, cv2.COLOR_RGB2GRAY)
                    hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                                           QtGui.QImage.Format_Indexed8)
                    himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
                    hQPixmapImage = himage_qtdata.scaled(self.template_image_3.size(), QtCore.Qt.KeepAspectRatio)
                else:
                    x1, y1, x2, y2 = self.currentParts.erron_pos[0], self.currentParts.erron_pos[1],self.currentParts.erron_pos[2], self.currentParts.erron_pos[3]
                    pcv_numpy = self.TempNumpy[ x1: y1,x2: y2]
                    rgbImage = cv2.cvtColor(pcv_numpy, cv2.COLOR_BGR2RGB)
                    qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                                          QtGui.QImage.Format_RGB888)
                    image_qtdata = QtGui.QPixmap.fromImage(qt_img)
                    QPixmapImage = image_qtdata.scaled(self.template_image_4.size(), QtCore.Qt.KeepAspectRatio)

                    # 灰度图转换
                    hrgbImage = cv2.cvtColor(pcv_numpy, cv2.COLOR_RGB2GRAY)
                    hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                                           QtGui.QImage.Format_Indexed8)
                    himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
                    hQPixmapImage = himage_qtdata.scaled(self.template_image_3.size(), QtCore.Qt.KeepAspectRatio)
                    self.template_image_4.setPixmap(QPixmapImage)
                    self.template_image_5.setPixmap(QPixmapImage)
                self.template_image_3.setPixmap(hQPixmapImage)
                self.start_interval_4.setText(self.currentParts.content)
                w = self.currentParts.erron_pos[3] - self.currentParts.erron_pos[2]
                h = self.currentParts.erron_pos[1] - self.currentParts.erron_pos[0]
                self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (
                w, h, self.currentParts.erron_pos[0], self.currentParts.erron_pos[2]))
        self.canvas.update()
    def worr_angle(self):
        x = self.po[0].x()
        y = self.po[0].y()
        w = self.po[1].x()
        h = self.po[1].y()
        center = ((w-x)//2+x,(h-y)//2+y)
        rotated = imutils.rotate(self.currentParts.cvColorImage, self.rotation_angle,center = center)
        self.worr_image = rotated[y:h, x:w]
        rgbImage = cv2.cvtColor(self.worr_image, cv2.COLOR_BGR2RGB)
        qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                              QtGui.QImage.Format_RGB888)
        image_qtdata = QtGui.QPixmap.fromImage(qt_img)
        QPixmapImage = image_qtdata.scaled(self.template_image_4.size(), QtCore.Qt.KeepAspectRatio)
        self.template_image_4.setPixmap(QPixmapImage)
        self.wrong_pos = [QtCore.QPoint(x, y), QtCore.QPoint(w, h)]
        self.label_2.setText('Width: %s, Height: %s, vertex: (%s, %s)' % (w, h, x, y))

    def type_control(self, data):
        self.tableWidget.setRowCount(len(data))
        for i, ty in enumerate(data):
            item1 = QTableWidgetItem(ty)
            self.tableWidget.setItem(i, 0, item1)
            ng_type = QTableWidgetItem(self.currentParts.name)
            self.tableWidget.setItem(i, 1, ng_type)
            test_results = QTableWidgetItem("PASS")
            self.tableWidget.setItem(i, 2, test_results)

    def zoomRequest(self, delta, pos):
        canvas_width_old = self.canvas.width()
        units = 1.1
        if delta < 0:
            units = 0.9
        self.addZoom(units)

        canvas_width_new = self.canvas.width()
        if canvas_width_old != canvas_width_new:
            canvas_scale_factor = canvas_width_new / canvas_width_old

            x_shift = round(pos.x() * canvas_scale_factor) - pos.x()
            y_shift = round(pos.y() * canvas_scale_factor) - pos.y()

            self.setScroll(
                Qt.Horizontal,
                self.scrollBars[Qt.Horizontal].value() + x_shift,
            )
            self.setScroll(
                Qt.Vertical,
                self.scrollBars[Qt.Vertical].value() + y_shift,
            )

    def addZoom(self, increment=1.1):
        # self.setZoom(self.zoomWidget.value() * increment)
        self.zoomValue = self.zoomValue * increment
        self.paintCanvas()

    def scrollRequest(self, delta, orientation):
        units = - delta * 0.1  # natural scroll
        bar = self.scrollBars[orientation]
        value = bar.value() + bar.singleStep() * units
        self.setScroll(orientation, value)

    def setScroll(self, orientation, value):
        self.scrollBars[orientation].setValue(value)

    def paintCanvas(self):
        assert self.canvas.pixmap is not None, "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomValue
        self.canvas.adjustSize()
        self.canvas.update()

    # React to canvas signals.
    def shapeSelectionChanged(self, selected_shapes):
        for shape in self.canvas.selectedShapes:
            shape.selected = False
            shape.highlightClear()
        # self.labelList.clearSelection()
        self.canvas.selectedShapes = selected_shapes
        for shape in self.canvas.selectedShapes:
            shape.selected = True

    def wrong_template(self):
        self.template_image.setPixmap(QPixmap(""))
        x1, y1, x2, y2 = int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())

        # 灰度图转换
        hrgbImage = cv2.cvtColor(self.worr_image, cv2.COLOR_RGB2GRAY)
        hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                               QtGui.QImage.Format_Indexed8)
        himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
        hQPixmapImage = himage_qtdata.scaled(self.template_image.size(), QtCore.Qt.KeepAspectRatio)
        self.template_image_3.setPixmap(hQPixmapImage)

        label_point = [x1, y1, x2, y2] # 坐标点
        template_content = self.start_interval_4.text() # 模板文字
        if template_content:
            self.Sigtemplate.emit(label_point, self.currentParts.name, "wrong_piece", template_content, str(self.rotation_angle))
        else:
            self.box = QMessageBox(QMessageBox.Warning, "警告框", "请输入模板文字")
            self.box.addButton(self.tr("确定"), QMessageBox.YesRole)
            self.box.exec_()

        logger.debug("生成错件模板成功。元件名称：%s，模板文字%s， 旋转角度%s" % (self.currentParts.name,template_content,self.rotation_angle))
    def generate_template(self):
        x1, y1, x2, y2 = int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())
        self.TempNumpy = self.currentParts.cvColorImage[x1: y1, x2: y2]

        path = self.folder + "/%s.jpg" % self.currentParts.name
        rgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_BGR2RGB)
        qt_img = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                              QtGui.QImage.Format_RGB888)
        image_qtdata = QtGui.QPixmap.fromImage(qt_img)
        self.TempQimage = image_qtdata.scaled(self.template_image_5.size(), QtCore.Qt.KeepAspectRatio)
        # 灰度图转换
        hrgbImage = cv2.cvtColor(self.TempNumpy, cv2.COLOR_RGB2GRAY)
        hqt_img = QtGui.QImage(hrgbImage, hrgbImage.shape[1], hrgbImage.shape[0], hrgbImage.shape[1] * 1,
                               QtGui.QImage.Format_Indexed8)
        himage_qtdata = QtGui.QPixmap.fromImage(hqt_img)
        hQPixmapImage = himage_qtdata.scaled(self.template_image_5.size(), QtCore.Qt.KeepAspectRatio)

        label_point = [x1, y1, x2, y2]
        # 相似度
        similar_value = str(self.similarValue.value())
        template_content = self.start_interval_4.text()
        # 保存数据(相对元器件坐标点，元器件名称，类型，图片路径，相似度, 模板字)
        self.template_image_3.setPixmap(hQPixmapImage)
        self.template_image_5.setPixmap(self.TempQimage)
        cv2.imwrite(path, self.TempNumpy)

        self.Sigtemplate.emit(label_point, self.currentParts.name, "missing_parts", path, similar_value)

        logger.debug("生成模板成功。元件名称：%s" % self.currentParts.name)
    def ngType(self, index):
        if self.currentParts.part_type in ["resistor", "slot"]:
            if index == 2:
                self.dete_alg_value.setCurrentIndex(4)
                self.stackedWidget.setCurrentIndex(0)
            elif index ==1:
                self.dete_alg_value.setCurrentIndex(1)
                self.stackedWidget.setCurrentIndex(1)
        elif self.currentParts.part_type == "capacitor":
            if index == 0:
                self.dete_alg_value.setCurrentIndex(3)
                self.stackedWidget.setCurrentIndex(1)
            elif index == 1:
                self.dete_alg_value.setCurrentIndex(1)
                if self.cap_type == "overall":
                    self.stackedWidget.setCurrentIndex(5)
                else:
                    self.stackedWidget.setCurrentIndex(3)
            else:
                self.stackedWidget.setCurrentIndex(2)
                self.dete_alg_value.setCurrentIndex(2)
        else:
            if index ==0:
                self.stackedWidget.setCurrentIndex(4)
            else:
                self.stackedWidget.setCurrentIndex(index)
            self.stackedWidget.setCurrentIndex(index)
            self.dete_alg_value.setCurrentIndex(index)
        self.tabel_clicked(index)
    def dete_alg(self, index):
        if self.currentParts.part_type in ["resistor", "slot", "capacitor"]:
            if index == 4:
                self.NG_value.setCurrentIndex(2)
                self.stackedWidget.setCurrentIndex(0)
            elif index ==1:
                self.NG_value.setCurrentIndex(1)
                self.stackedWidget.setCurrentIndex(1)
        else:
            if index ==0:
                self.stackedWidget.setCurrentIndex(4)
            else:
                self.stackedWidget.setCurrentIndex(index)
            self.tabWidget.setCurrentIndex(index)
            self.NG_value.setCurrentIndex(index)
    def push_button(self):
        # 正极坐标点
        x1, y1, x2, y2 = int(self.canvas.shapes[0][0].y()), int(self.canvas.shapes[0][1].y()), int(
            self.canvas.shapes[0][0].x()), int(self.canvas.shapes[0][1].x())
        # 负极坐标点
        x3, y3, x4, y4 = int(self.canvas.shapes[1][0].y()), int(self.canvas.shapes[1][1].y()), int(
            self.canvas.shapes[1][0].x()), int(self.canvas.shapes[1][1].x())

        # 正极元器件灰度值
        P_components = self.TempNumpy [x1: y1, x2: y2]

        positive_lwpImg = cv2.cvtColor(P_components, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        positive_mean = int(np.mean(positive_lwpImg))
        # 负极元器件灰度值
        negative_cropped = self.TempNumpy[x3:y3, x4:y4]

        negative_lwpImg = cv2.cvtColor(negative_cropped, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        negative_mean = int(np.mean(negative_lwpImg))
        # self.raw_imange.negative_mean = int(negative_mean)
        difference = positive_mean - negative_mean
        # self.g_difference_value.se
        strT = '<span style=\" color: #ff0000;\">%s</span>' % difference  # 红色
        # 不同界面
        if self.cap_type == "overall":
            self.label_37.setText("%s" % (strT))  # 界面显示
            # grayscale = [int(positive_mean), int(negative_mean), self.g_PN_threshold_value.value() ]
            # self.g_PN_threshold_value.value = threshold_value
            if difference>0:
                self.label_38.setText("正极")
            else:
                self.label_38.setText("负极")
        else:
            self.label_26.setText("%s" % (strT))  # 界面显示
            # grayscale = [int(positive_mean), int(negative_mean), self.g_PN_threshold_value.value() ]
            # self.g_PN_threshold_value.value = threshold_value
            if difference>0:
                self.label_25.setText("正极")
            else:
                self.label_25.setText("负极")
        self.update()
        label_pos = [[x1, y1, x2, y2], [x3, y3, x4, y4]]
        Z_F = [positive_mean,negative_mean]
        # 保存数据 （坐标点，元器件名称，阈值灰度差，实际差, 类型）
        self.extremelyNegative.emit(label_pos, self.currentParts.name, difference, Z_F,
                                    "extremely_negative")
