import os
import sys
sys.path.append('./ui')
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog

import cv2

import utils
from mask import Mask
from shape import Shape
from canvas import Canvas
from pattern import Pattern
from ui.pcb_location import PCBLocationWidget
from ui.pattern_info import PatternInfoWidget
from ui.mask_widget import MaskWidget


new_action = lambda icon, text: QtWidgets.QAction(QtGui.QIcon(icon), text)


class PatternWidget(QtWidgets.QWidget):
    ''' 程式设计界面，主要功能包括：
        1. 程式创建/保存/载入、基本绘图工具、基础元器件模板；
        2. 左边工作区（imageLabel），用于绘制元器件的程式模板；
        3. 右上角程式信息展示区域；
        4. 右下角相机实时预览区域。
    '''
    def __init__(self):
        super().__init__()
        # actions
        self.createAction = new_action('./icon/create-100.png', '新建程式')
        self.saveAction = new_action('./icon/save-64.png', '保存程式')
        self.openAction = new_action('./icon/folder-50.png', '打开程式')

        self.captureAction = new_action('./icon/cap-64.png', '抓取图像')
        self.zoomInAction = new_action('./icon/zoom-in-50.png', '放大')
        self.zoomOutAction = new_action('./icon/zoom-out-50.png', '缩小')
        self.cursorAction = new_action('./icon/cursor-50.png', '选择')
        self.moveAction = new_action('./icon/hand-50.png', '移动')

        self.pcbLocationAction = new_action('./icon/green-flag-50.png', 'PCB定位')
        self.maskAction = new_action('./icon/mask-50.png', 'Mask')

        self.capacitorAction = new_action('./icon/capacitor.png', '电解电容')
        self.resistorAction = new_action('./icon/resistor.png', '色环电阻')
        self.slotAction = new_action('./icon/slot.png', '插槽')
        self.componentAction = new_action('./icon/component.png', '一般元件')

        self.homeAction = new_action('./icon/home-50.png', '检测界面')

        # self.capacitorAction.triggered.connect(self.draw_location)
        self.cursorAction.triggered.connect(self.cursor_action)
        self.pcbLocationAction.triggered.connect(self.pcb_location_action)
        self.maskAction.triggered.connect(self.draw_mask_action)
        self.createAction.triggered.connect(self.create_pattern)
        self.openAction.triggered.connect(self.load_pattern)

        # init toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addActions([self.createAction, self.saveAction, self.openAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions(
            [self.captureAction, self.zoomInAction, self.zoomOutAction, self.cursorAction, self.moveAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.pcbLocationAction, self.maskAction, self.capacitorAction, self.resistorAction,
                                 self.slotAction, self.componentAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.homeAction])
        self.toolbar.setIconSize(QtCore.QSize(32, 32))
        
        # left center view
        self.canvas = Canvas()
        # self.canvas.setStyleSheet('background-color: rgb(0, 0, 0);')

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidget(self.canvas)
        self.scrollArea.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: self.scrollArea.verticalScrollBar(),
            Qt.Horizontal: self.scrollArea.horizontalScrollBar(),
        }

        self.zoomValue = 100.0  # 缩放尺度，100为原始尺寸
        self.canvas.zoomRequest.connect(self.zoomRequest)
        self.canvas.scrollRequest.connect(self.scrollRequest)
        # self.canvas.newShape.connect(self.new_shape)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)

        # TODO:canvas右键弹出菜单内容设定
        actions_1 = [self.zoomInAction, self.zoomOutAction, self.captureAction]
        actions_2 = [self.captureAction]
        utils.addActions(self.canvas.menus[0], actions_1)
        utils.addActions(self.canvas.menus[1], actions_2)

        # right top view: TODO
        # 第一页：程式信息页
        self.patternInfoWidget = PatternInfoWidget()
        # 第二页：定位信息页
        self.locationWidget = PCBLocationWidget()
        self.locationWidget.getPCBSignal.connect(self.get_pcb_action)
        self.locationWidget.getImageSignal.connect(self.get_template_action)
        self.locationWidget.savePCBLocationInfomation.connect(self.save_pcb_base_infomation)
        self.locationWidget.saveTemplateInfomation.connect(self.save_template_information)
        # 第三页：Mask页
        self.maskWidget = MaskWidget()
        self.maskWidget.getMaskSignal.connect(self.get_mask_action)
        self.maskWidget.savePatternSignal.connect(self.save_pattern)

        self.rightTopArea = QtWidgets.QTabWidget()
        self.rightTopArea.addTab(self.patternInfoWidget, '程式信息')
        self.rightTopArea.addTab(self.locationWidget, '定位信息')
        self.rightTopArea.addTab(self.maskWidget, 'Mask信息')
        self.rightTopArea.setCurrentWidget(self.patternInfoWidget)
        self.rightTopArea.tabBarClicked.connect(self.tabel_widget_tabbar_clicked)

        # 软件启动时，未加载程式，此时所有tab都设置为disable
        for idx in range(self.rightTopArea.count()):
            self.rightTopArea.setTabEnabled(idx, False)

        # right buttom view
        self.videoLabel = QtWidgets.QLabel()
        self.videoLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        self.videoLabel.setAlignment(QtCore.Qt.AlignCenter)

        # right layout
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.setSpacing(13)
        rightLayout.addWidget(self.rightTopArea, 1)
        rightLayout.addWidget(self.videoLabel, 1)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(13)
        hlayout.addWidget(self.scrollArea, 2)
        hlayout.addLayout(rightLayout, 1)

        # main layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(13)
        layout.addWidget(self.toolbar)
        layout.addLayout(hlayout)
        self.setLayout(layout)

    def create_pattern(self):
        ''' 选择文件夹，创建程式 '''
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, '请选择一个程式文件夹', './')
        # print(folder)
        if not folder or not os.path.exists(folder):
            QtWidgets.QMessageBox.warning(self, '错误', '请选择一个文件夹路径')
            return
        self.pattern = Pattern(folder=folder)
        self.show_pattern_info()

    def load_pattern(self):
        ''' 选择程式并加载 '''
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, '选择程式文件夹', './')
        if not folder or not os.path.exists(folder):
            QtWidgets.QMessageBox.warning(self, '错误', '请选择正确的程式路径')
            return
        imagefile = os.path.join(folder, 'image.jpg')
        infofile = os.path.join(folder, 'info.json')
        if not os.path.exists(imagefile) or not os.path.exists(infofile):
            QtWidgets.QMessageBox.warning(self, '错误', '未找到程式信息，请选择正确的程式文件夹')
            return
        self.pattern = Pattern.from_folder(folder)
        self.show_pattern_info()

        # 加载CV数据
        cvImage = cv2.imread(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        self.canvas.cvImage = cvImage[y:y+h+1, x:x+w+1, :]

        # 加载pixmap，并显示
        orgPixmap = QtGui.QPixmap(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        rectangle = QtCore.QRect(x, y, w, h)
        pixmap = orgPixmap.copy(rectangle)
        self.canvas.loadPixmap(pixmap)

        shapes = []

        # 模板加载，PCB截图加载
        self.locationWidget.set_pixmap(self.locationWidget.pcbLabel, pixmap)
        for i in [0, 1]:
            if not self.pattern.ax_templates:
                continue
            x, y, w, h = self.pattern.ax_templates[i]
            widget = self.locationWidget.templateLabel_1 if i == 0 else self.locationWidget.templateLabel_2
            rectangle = QtCore.QRect(x, y, w, h)
            pixmap = orgPixmap.copy(rectangle)
            self.locationWidget.set_pixmap(widget, pixmap)

            # load shapes
            shape = Shape(shape_type='location')
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x+w, y+h)
            shape.points.extend([p1, p2])
            shapes.append(shape)

        # 加载Mask
        self.maskWidget.maskList.clear()
        for mask in self.pattern.masks:
            x, y ,w, h = mask.x, mask.y, mask.w, mask.h
            shape = Shape(shape_type='mask')
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x+w, y+h)
            shape.points.extend([p1, p2])
            shapes.append(shape)

            # init mask widget
            mask.load_image(cvImage)
            self.maskWidget.maskList.append(mask)
        
        self.maskWidget.update_listwidget()

        self.canvas.loadShapes(shapes)
        self.canvas.update()

        # enable all tabs
        for idx in range(self.rightTopArea.count()):
            self.rightTopArea.setTabEnabled(idx, True)

    def show_pattern_info(self):
        if not hasattr(self, 'pattern'):
            return
        self.rightTopArea.setTabEnabled(0, True)
        self.rightTopArea.setCurrentWidget(self.patternInfoWidget)
        self.patternInfoWidget.show_pattern_info(self.pattern.folder)

    def pcb_location_action(self):
        ''' PCB定位按钮响应函数 '''
        if not hasattr(self, 'pattern') or not self.pattern.folder:
            QtWidgets.QMessageBox.information(self, '提示', '请先创建或者载入程式')
            return
        if not self.canvas.pixmap:
            # print('not self.canvas.pixmap ')
            QtWidgets.QMessageBox.information(self, '提示', '请先抓取图片')
            return
        self.draw_location()
        self.canvas.update()
        self.rightTopArea.setTabEnabled(1, True)
        self.rightTopArea.setCurrentWidget(self.locationWidget)

    def draw_mask_action(self):
        if not hasattr(self, 'pattern') or not self.pattern.folder:
            QtWidgets.QMessageBox.information(self, '提示', '请先创建或者载入程式')
            return
        if not self.canvas.pixmap:
            # print('not self.canvas.pixmap ')
            QtWidgets.QMessageBox.information(self, '提示', '请先抓取图片')
            return
        self.canvas.setEditing(False)
        self.canvas.createMode = 'mask'
        self.canvas.update()
        self.rightTopArea.setTabEnabled(2, True)
        self.rightTopArea.setCurrentWidget(self.maskWidget)

    def tabel_widget_tabbar_clicked(self, index):
        ''' 右上角tabwidget页面点击 '''
        if index == 1:  # PCB定位页面
            self.pcb_location_action()
            self.locationWidget.update_pixmap_show()
        elif index == 2:  # mask页面
            self.draw_mask_action()
            self.maskWidget.update_pixmap_show()

    def save_pcb_base_infomation(self):
        if not hasattr(self, 'pattern'):
            return
        if not self.pattern.ax_pcbs:
            QtWidgets.QMessageBox.information(self, '提示', '请先获取PCB板')
            return
        x, y, w, h = self.pattern.ax_pcbs
        rectangle = QtCore.QRect(x, y, w, h)
        pixmap = self.canvas.pixmap.copy(rectangle)
        self.canvas.cvImage = self.canvas.cvImage[y:y+h+1, x:x+w+1, :]
        self.canvas.loadPixmap(pixmap)
        self.canvas.update()
        # 保存程式基础信息
        self.pattern.save()

    def save_template_information(self):
        if not hasattr(self, 'pattern'):
            return
        if not self.pattern.ax_pcbs:
            QtWidgets.QMessageBox.information(self, '提示', '请先获取PCB板')
            return
        # if not any(self.pattern.ax_templates):
        if self.locationWidget.template_1 is None and self.locationWidget.template_2 is None:
            QtWidgets.QMessageBox.information(self, '提示', '请先获取模板')
            return
        # 保存程式基础信息
        self.save_pattern()

    def get_roi_image(self):
        ''' 获取模板或者PCB的相应函数。该函数截取用户绘制的区域，并显示在相应的widget中。
            此外，本函数还负责保存截取区域的坐标参数，作为程式的基础信息并保存 '''
        if not self.canvas.pixmap:
            return
        if not hasattr(self, 'pattern'):
            return
        shapeList = self.canvas.modeToShapeList[self.canvas.createMode]
        if not shapeList:
            return
        shape = shapeList[-1]
        if len(shape.points) != 2:
            return
        rectangle = shape.getRectFromLine(*shape.points).toRect()
        # 保存坐标信息
        x, y, w, h = rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height()
        cvImage = self.canvas.cvImage[y:y+h+1, x:x+w+1, :]
        pixmap = self.canvas.pixmap.copy(rectangle)
        return x, y, w, h, cvImage, pixmap

        # if widget == self.locationWidget.pcbLabel:
        #     self.pattern.set_pcb_coordinate(x, y, w, h)
        #     self.pattern.originCVImage = self.canvas.cvImage.copy()  # 设置图片

        # self.sender().set_pixmap(widget, pixmap)

    def get_pcb_action(self):
        ''' 获取选中的PCB板 '''
        x, y, w, h, cvImage, pixmap = self.get_roi_image()
        self.pattern.set_pcb_coordinate(x, y, w, h)
        self.pattern.originCVImage = self.canvas.cvImage.copy()  # 设置图片
        self.locationWidget.set_pixmap(self.locationWidget.pcbLabel, pixmap)

    def get_template_action(self, widget):
        ''' 获取选中的模板 '''
        x, y, w, h, cvImage, pixmap = self.get_roi_image()
        self.locationWidget.set_pixmap(widget, pixmap)

    def get_mask_action(self):
        ''' 获取选中的Mask '''
        x, y, w, h, cvImage, pixmap = self.get_roi_image()
        mask = Mask(x, y, w, h)
        mask.load_image(self.canvas.cvImage)
        self.maskWidget.set_mask(mask)

    def save_pattern(self):
        ''' 保存pattern信息；位置信息均来自canvas里面的shapes '''
        if not hasattr(self, 'pattern'):
            return
        if not self.pattern.ax_pcbs:
            print('error: location pcb first')
            return
        # 1. save template
        self.pattern.ax_templates.clear()
        for shape in self.canvas.locationShapes:
            rect = shape.getRectFromLine(*shape.points).toRect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            self.pattern.ax_templates.append([x, y, w, h])
        # 2. save mask
        self.pattern.masks.clear()
        for shape in self.canvas.maskShapes:
            rect = shape.getRectFromLine(*shape.points).toRect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            mask = Mask(x, y, w, h)
            self.pattern.masks.append(mask)
        # 3. save parts: TODO

        self.pattern.save()

    # React to canvas signals.
    def shapeSelectionChanged(self, selected_shapes):
        self._noSelectionSlot = True
        for shape in self.canvas.selectedShapes:
            shape.selected = False
        # self.labelList.clearSelection()
        self.canvas.selectedShapes = selected_shapes
        for shape in self.canvas.selectedShapes:
            shape.selected = True
            # item = self.labelList.findItemByShape(shape)
            # self.labelList.selectItem(item)
            # self.labelList.scrollToItem(item)
        self._noSelectionSlot = False
        n_selected = len(selected_shapes)
        # self.actions.delete.setEnabled(n_selected)
        # self.actions.copy.setEnabled(n_selected)
        # self.actions.edit.setEnabled(n_selected == 1)

    # def new_shape(self):
    #     # self.canvas.setLastLabel('a', {})
    #     pass

    def cursor_action(self):
        self.canvas.setEditing(True)

    def draw_location(self):
        self.canvas.setEditing(False)
        self.canvas.createMode = 'location'

    def scrollRequest(self, delta, orientation):
        units = - delta * 0.1  # natural scroll
        bar = self.scrollBars[orientation]
        value = bar.value() + bar.singleStep() * units
        self.setScroll(orientation, value)

    def setScroll(self, orientation, value):
        self.scrollBars[orientation].setValue(value)
        # self.scroll_values[orientation][self.filename] = value

    # def setZoom(self, value):
        # self.actions.fitWidth.setChecked(False)
        # self.actions.fitWindow.setChecked(False)
        # self.zoomMode = self.MANUAL_ZOOM
        # self.zoomWidget.setValue(value)
        # self.zoom_values[self.filename] = (self.zoomMode, value)

    def addZoom(self, increment=1.1):
        # self.setZoom(self.zoomWidget.value() * increment)
        self.zoomValue = self.zoomValue * increment
        self.paintCanvas()

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

    def paintCanvas(self):
        assert self.canvas.pixmap is not None, "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomValue
        self.canvas.adjustSize()
        self.canvas.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = PatternWidget()
    win.setWindowTitle('程式制作窗口')
    win.showMaximized()
    sys.exit(app.exec_())