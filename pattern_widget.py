import os
import sys
sys.path.append('./ui')
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog

import cv2

import utils
from template import Template
from mask import Mask
from part import Part
from shape import Shape
from canvas import Canvas
from pattern import Pattern
from ui.pattern_info import PatternInfoWidget
from ui.pcb_location import PCBLocationWidget
from ui.template_widget import TemplateWidget
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

        self.pcbLocationAction = new_action('./icon/green-flag-50.png', 'PCB选取')
        self.templateAction = new_action('./icon/green-flag-50.png', '模板定位')
        self.maskAction = new_action('./icon/mask-50.png', 'Mask')

        self.capacitorAction = new_action('./icon/capacitor.png', '电解电容')
        self.resistorAction = new_action('./icon/resistor.png', '色环电阻')
        self.slotAction = new_action('./icon/slot.png', '插槽')
        self.componentAction = new_action('./icon/component.png', '一般元件')

        self.homeAction = new_action('./icon/home-50.png', '检测界面')

        self.cursorAction.triggered.connect(self.cursor_action)
        self.pcbLocationAction.triggered.connect(self.mode_change_by_action)
        self.templateAction.triggered.connect(self.mode_change_by_action)
        self.maskAction.triggered.connect(self.mode_change_by_action)
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
        self.toolbar.addActions([self.pcbLocationAction, self.templateAction, self.maskAction, self.capacitorAction, 
                                 self.resistorAction, self.slotAction, self.componentAction])
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
        self.canvas.newShape.connect(self.new_shape)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.deleteShape.connect(self.delete_shape)


        # TODO:canvas右键弹出菜单内容设定
        # actions_1 = [self.zoomInAction, self.zoomOutAction, self.captureAction]
        # actions_2 = [self.captureAction]
        # utils.addActions(self.canvas.menus[0], actions_1)
        # utils.addActions(self.canvas.menus[1], actions_2)

        # right top view: TODO
        # 第一页：程式信息页
        self.patternInfoWidget = PatternInfoWidget()
        # 第二页：定位信息页
        self.locationWidget = PCBLocationWidget()
        # self.locationWidget.getPCBSignal.connect(self.get_pcb_action)
        # self.locationWidget.getImageSignal.connect(self.get_template_action)
        self.locationWidget.savePCBLocationInfomation.connect(self.save_pcb_base_infomation)
        # self.locationWidget.saveTemplateInfomation.connect(self.save_template_information)
        # 第三页：模板定位页
        self.templateWidget = TemplateWidget()
        # self.templateWidget.newTemplateShape.connect(self.new_shape)
        self.templateWidget.savePatternSignal.connect(self.save_pattern)
        self.templateWidget.selectedChanged.connect(self.selected_item_changed_from_widget)
        # 第四页：Mask页
        self.maskWidget = MaskWidget()
        # self.maskWidget.getMaskSignal.connect(self.get_mask_action)
        self.maskWidget.savePatternSignal.connect(self.save_pattern)
        self.maskWidget.selectedChanged.connect(self.selected_item_changed_from_widget)

        self.rightTopArea = QtWidgets.QTabWidget()
        self.rightTopArea.addTab(self.patternInfoWidget, '程式信息')
        self.rightTopArea.addTab(self.locationWidget, '定位信息')
        self.rightTopArea.addTab(self.templateWidget, '模板信息')
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
        self.canvas.cvImage = cvImage[y:y+h, x:x+w, :].copy()

        # 加载pixmap，并显示
        orgPixmap = QtGui.QPixmap(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        rectangle = QtCore.QRect(x, y, w, h)
        pixmap = orgPixmap.copy(rectangle)
        self.canvas.loadPixmap(pixmap)

        shapes = []

        # PCB截图加载
        self.locationWidget.set_pixmap(self.locationWidget.pcbLabel, pixmap)
        
        # 模板加载
        for i, template in enumerate(self.pattern.templates):
            template.load_image(cvImage)
            x, y, w, h = template.x, template.y, template.w, template.h

            # load shapes
            shape = Shape(name=template.name, shape_type='template')
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x+w, y+h)
            shape.points.extend([p1, p2])
            shapes.append(shape)

            # init template widget
            self.templateWidget.templateList.append(template)


        # 加载Mask
        self.maskWidget.maskList.clear()
        for mask in self.pattern.masks:
            mask.load_image(cvImage)
            x, y ,w, h = mask.x, mask.y, mask.w, mask.h

            shape = Shape(name=mask.name, shape_type='mask')
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x+w, y+h)
            shape.points.extend([p1, p2])
            shapes.append(shape)

            # init mask widget
            self.maskWidget.maskList.append(mask)
        
        self.canvas.loadShapes(shapes)
        self.canvas.update()

        # 更新界面显示
        self.templateWidget.update_listwidget()
        self.maskWidget.update_listwidget()


        # enable all tabs
        for idx in range(self.rightTopArea.count()):
            self.rightTopArea.setTabEnabled(idx, True)

    def new_shape(self, classes=''):
        ''' 新增形状，classes为: template,mask,part; name为列表显示的名称'''
        # type2class = {'template': Template, 'mask': Mask, 'part': Part}
        try:
            x, y, w, h, cvImage, pixmap = self.get_roi_image()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '警告', str(e))
            return
        
        # 获取唯一的name
        name = self.pattern.new_name(classes)
        # 更新canvas中对应shape的name
        self.canvas.shapes[-1].name = name
        # canvas变为编辑模式
        self.canvas.setEditing(True)

        if classes == 'location':
            self.pattern.set_pcb_coordinate(x, y, w, h)
            self.pattern.originCVImage = self.canvas.cvImage.copy()  # 设置图片
            self.locationWidget.set_pixmap(self.locationWidget.pcbLabel, pixmap)
        elif classes == 'template':
            template = Template(x, y, w, h, name)
            template.load_image(self.canvas.cvImage)
            self.pattern.templates.append(template)
            # 更新界面数据
            self.templateWidget.set_template(template)
            self.templateWidget.save_current()
        elif classes == 'mask':
            mask = Mask(x, y, w, h, name)
            mask.load_image(self.canvas.cvImage)
            self.pattern.masks.append(mask)
            self.maskWidget.set_mask(mask)
            self.maskWidget.save_current()
        elif classes == 'part':
            part = Part(x, y, w, h, name)
            part.load_image(self.canvas, cvImage)
            self.pattern.parts.append(part)
            # 更新界面数据，TODO
        else:
            raise Exception('类型不匹配: ' + classes)

    def delete_shape(self, classes='', name=''):
        ''' 删除形状,classes为: template,mask,part; name为列表显示的名称 '''
        if not self.pattern:
            return

        if classes == 'template':
            itemList = self.pattern.templates
            widget = self.templateWidget
        elif classes == 'mask':
            itemList = self.pattern.masks
            widget = self.maskWidget
        elif classes == 'part':
            itemList = self.pattern.parts
            # widget = self.partWidget
        else:
            raise Exception('类型不匹配')

        index = [x.name for x in itemList].index(name)
        # pattern中数据删除
        itemList.pop(index)
        # 更新界面
        widget.delete_by_name(name)

    def change_shape_coordinate(self, classes='', name=''):
        ''' 拖动形状导致坐标或者大小变换后触发，更新pattern参数及界面显示 '''
        if not self.pattern:
            return
        # step1: get coordinate
        # step2: update pattern
        # step3: update widget by name

    def change_shape_parameter(self, classes='', name=''):
        ''' 界面中更改相关参数后触发 '''
        if not self.pattern:
            return
        # step1: get parameter
        # step2: update pattern

    def seleted_shape_changed_from_canvas(self, shapes):
        if not shapes:
            return
        shape = shapes[0]
        if shape.shape_type == 'template':
            self.templateWidget.set_current_template_by_name(shape.name)
        elif shape.shape_type == 'mask':
            self.maskWidget.set_current_mask_by_name(shape.name)
        else:  # TODO
            pass

    def selected_item_changed_from_widget(self, classes, name):
        ''' 界面中选中某个项，canvas中需要高亮此项 '''
        for shape in self.canvas.shapes:
            if shape.shape_type == classes and shape.name == name:
                # print('seleted: ', name)
                if self.canvas.hShape:
                    self.canvas.hShape.selected = False
                    self.canvas.hShape.highlightClear()
                shape.selected = True
                self.canvas.hShape = shape
                self.canvas.update()
                break

    def has_pattern_and_pixmap(self):
        if not hasattr(self, 'pattern') or not self.pattern.folder:
            QtWidgets.QMessageBox.information(self, '提示', '请先创建或者载入程式')
            return False
        if not self.canvas.pixmap:
            QtWidgets.QMessageBox.information(self, '提示', '请先抓取图片')
            return False
        return True

    def show_pattern_info(self):
        if not hasattr(self, 'pattern'):
            return
        self.rightTopArea.setTabEnabled(0, True)
        self.rightTopArea.setCurrentWidget(self.patternInfoWidget)
        self.patternInfoWidget.show_pattern_info(self.pattern.folder)

    def tabel_widget_tabbar_clicked(self, index):
        ''' 右上角tabwidget页面点击 '''
        if index == 1:  # PCB定位页面
            self.canvas.createMode = 'location'
            self.locationWidget.update_pixmap_show()
        elif index == 2:  # template页面
            self.canvas.createMode = 'template'
            self.templateWidget.update_pixmap_show()
        elif index == 3:  # mask页面
            self.canvas.createMode = 'mask'
            self.maskWidget.update_pixmap_show()
        # 点击页面标签后，进入编辑模式
        self.canvas.setEditing(True)
        self.canvas.update()

    def mode_change_by_action(self):
        if not self.has_pattern_and_pixmap():
            return
        action = self.sender()
        if action == self.pcbLocationAction:
            self.canvas.createMode = 'location'
            self.rightTopArea.setTabEnabled(1, True)
            self.rightTopArea.setCurrentWidget(self.locationWidget)
        elif action == self.templateAction:
            self.canvas.createMode = 'template'
            self.rightTopArea.setTabEnabled(2, True)
            self.rightTopArea.setCurrentWidget(self.templateWidget)
        elif action == self.maskAction:
            self.canvas.createMode = 'mask'
            self.rightTopArea.setTabEnabled(3, True)
            self.rightTopArea.setCurrentWidget(self.maskWidget)
        
        self.canvas.setEditing(False)
        self.canvas.update()

    def save_pcb_base_infomation(self):
        if not hasattr(self, 'pattern'):
            return
        if not self.pattern.ax_pcbs:
            QtWidgets.QMessageBox.information(self, '提示', '请先获取PCB板')
            return
        x, y, w, h = self.pattern.ax_pcbs
        rectangle = QtCore.QRect(x, y, w, h)
        pixmap = self.canvas.pixmap.copy(rectangle)
        self.canvas.cvImage = self.canvas.cvImage[y:y+h, x:x+w, :].copy()
        self.canvas.loadPixmap(pixmap)
        self.canvas.update()
        # 保存程式基础信息
        self.pattern.save()

    def get_roi_image(self):
        ''' 获取模板或者PCB的相应函数。该函数截取用户绘制的区域，并显示在相应的widget中。
            此外，本函数还负责保存截取区域的坐标参数，作为程式的基础信息并保存 '''
        if not self.canvas.pixmap:
            raise Exception('请先获取图像')
        if not hasattr(self, 'pattern'):
            raise Exception('请先创建程式')
        # shapeList = self.canvas.modeToShapeList[self.canvas.createMode]
        shape = self.canvas.shapes[-1]
        if len(shape.points) != 2:
            raise Exception('请先获取一个形状')
        rectangle = shape.getRectFromLine(*shape.points).toRect()
        # 保存坐标信息
        x, y, w, h = rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height()
        cvImage = self.canvas.cvImage[y:y+h, x:x+w, :].copy()
        pixmap = self.canvas.pixmap.copy(rectangle)
        return x, y, w, h, cvImage, pixmap

    def save_pattern(self):
        ''' 保存pattern信息；位置信息均来自canvas里面的shapes '''
        if not hasattr(self, 'pattern'):
            return
        if not self.pattern.ax_pcbs:
            print('error: location pcb first')
            return
        self.pattern.save()

    # React to canvas signals.
    def shapeSelectionChanged(self, selected_shapes):
        for shape in self.canvas.selectedShapes:
            shape.selected = False
        # self.labelList.clearSelection()
        self.canvas.selectedShapes = selected_shapes
        for shape in self.canvas.selectedShapes:
            shape.selected = True
        # 更新tabwidget中的显示
        self.seleted_shape_changed_from_canvas(selected_shapes)

    def cursor_action(self):
        self.canvas.setEditing(True)

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