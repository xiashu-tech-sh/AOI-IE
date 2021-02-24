import os
import sys
import cv2
sys.path.append('./ui')
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from utils import cv_imread
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
from ui.part_widget import PartWidget
from ui.pattern_widget_ui import Ui_MainWindow
import logging
new_action = lambda icon, text: QtWidgets.QAction(QtGui.QIcon(icon), text)
logger = logging.getLogger('main.mod.submod')
logger.debug('程式界面')

class PatternWidget(QtWidgets.QMainWindow, Ui_MainWindow):
    ''' 程式设计界面，主要功能包括：
        1. 程式创建/保存/载入、基本绘图工具、基础元器件模板；
        2. 左边工作区（imageLabel），用于绘制元器件的程式模板；
        3. 右上角程式信息展示区域；
        4. 右下角相机实时预览区域。
    '''

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # # pattern
        # self.pattern = None
        # # actions
        # self.createAction = new_action('./icon/create-100.png', '新建程式')
        # self.saveAction = new_action('./icon/save-64.png', '保存程式')
        # self.openAction = new_action('./icon/folder-50.png', '打开程式')
        #
        # self.captureAction = new_action('./icon/cap-64.png', '抓取图像')
        # self.zoomInAction = new_action('./icon/zoom-in-50.png', '放大')
        # self.zoomOutAction = new_action('./icon/zoom-out-50.png', '缩小')
        # self.cursorAction = new_action('./icon/cursor-50.png', '选择')
        # # self.moveAction = new_action('./icon/hand-50.png', '移动')
        #
        # self.pcbLocationAction = new_action('./icon/1_pcb.png', 'PCB选取')
        # self.templateAction = new_action('./icon/green-flag-50.png', '模板定位')
        # self.maskAction = new_action('./icon/mask-50.png', 'Mask')
        # self.diodeAction = new_action('./icon/diode.png', '二极管')
        # self.capacitorAction = new_action('./icon/capacitor.png', '电解电容')
        # self.resistorAction = new_action('./icon/resistor.png', '色环电阻')
        # self.slotAction = new_action('./icon/slot.png', '插槽')
        # self.componentAction = new_action('./icon/component.png', '一般元件')
        #
        # self.homeAction = new_action('./icon/home-50.png', '检测界面')
        #
        self.cursorAction.triggered.connect(self.cursor_action)
        #
        for action in [self.pcbLocationAction, self.templateAction,self.maskAction,
                       self.capacitorAction, self.resistorAction, self.slotAction,
                       self.componentAction,self.diodeAction]:
            action.triggered.connect(self.mode_change_by_action)

        self.createAction.triggered.connect(self.create_pattern)
        self.openAction.triggered.connect(self.load_pattern)
        self.saveAction.triggered.connect(self.save_pattern)
        #
        # # init toolbar
        # self.toolbar = QtWidgets.QToolBar()
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        # self.toolbar.addActions([self.createAction, self.saveAction, self.openAction])
        # self.toolbar.addSeparator()
        # self.toolbar.addActions(
        #     [self.captureAction, self.zoomInAction, self.zoomOutAction, self.cursorAction])
        # self.toolbar.addSeparator()
        # self.toolbar.addActions([self.pcbLocationAction, self.templateAction, self.maskAction,self.capacitorAction,self.resistorAction, self.slotAction, self.diodeAction,self.componentAction])
        # self.toolbar.addSeparator()
        # self.toolbar.addActions([self.homeAction])
        # self.toolbar.setIconSize(QtCore.QSize(32, 32))
        #
        # # left center view
        self.canvas = Canvas()
        self.canvas.setStyleSheet('background-color: rgb(0, 0, 0);')
        self.scrollArea.setWidget(self.canvas)
        self.scrollArea.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: self.scrollArea.verticalScrollBar(),
            Qt.Horizontal: self.scrollArea.horizontalScrollBar(),
        }

        self.zoomValue = 100.0  # 缩放尺度，100为原始尺寸
        self.canvas.zoomRequest.connect(self.zoomRequest)  # 缩放事件，按住ctrl+鼠标滚轮后触发
        self.canvas.scrollRequest.connect(self.scrollRequest)  # 滚轮直接滚动：上下sroll； 按住alt+滚轮：左右scroll
        self.canvas.newShape.connect(self.new_shape)  # shape被拖动或者shape的角点被拖动后，左键释放后触发
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)  # EDIT阶段，鼠标选中的Shape发生变化后触发，CREATE阶段不触发
        self.canvas.deleteShape.connect(self.delete_shape)  # 删除形状,参数：classes, name
        self.canvas.pasteShape.connect(self.paste_shape)  # 复制形态 参数 classes,name
        self.canvas.shapeMoved.connect(self.change_shape_coordinate)
        #
        # # TODO:canvas右键弹出菜单内容设定
        # # actions_1 = [self.zoomInAction, self.zoomOutAction, self.captureAction]
        # # actions_2 = [self.captureAction]
        # # utils.addActions(self.canvas.menus[0], actions_1)
        # # utils.addActions(self.canvas.menus[1], actions_2)
        #
        # # right top view: TODO
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
        self.templateWidget.savePatternSignal.connect(self.save_template_info)
        self.templateWidget.selectedChanged.connect(self.selected_item_changed_from_widget)
        self.templateWidget.parameterChanged.connect(self.set_pattern_dirty)
        # 第四页：Mask页
        self.maskWidget = MaskWidget()
        # self.maskWidget.getMaskSignal.connect(self.get_mask_action)
        self.maskWidget.savePatternSignal.connect(self.save_pattern)
        self.maskWidget.selectedChanged.connect(self.selected_item_changed_from_widget)
        self.maskWidget.parameterChanged.connect(self.set_pattern_dirty)
        # 第五页：Part页，元器件信息
        self.partWidget = PartWidget()
        self.partWidget.savePatternSignal.connect(self.save_pattern)
        self.partWidget.selectedChanged.connect(self.selected_item_changed_from_widget)
        self.partWidget.parameterChanged.connect(self.set_pattern_dirty)
        # # 极反
        # self.partWidget.extremely_negative_emit.connect(self.extremely_negative)
        # # 漏件
        # self.partWidget.wrong_piece_emit.connect(self.wrong_piece)
        # # 颜色
        # self.partWidget.color_emait.connect(self.color_extract)
        #
        # self.rightTopArea = QtWidgets.QTabWidget()
        self.rightTopArea.addTab(self.patternInfoWidget, '程式信息')
        self.rightTopArea.addTab(self.locationWidget, '定位信息')
        self.rightTopArea.addTab(self.templateWidget, '模板信息')
        self.rightTopArea.addTab(self.maskWidget, 'Mask信息')
        self.rightTopArea.addTab(self.partWidget, '元器件信息')
        self.rightTopArea.setCurrentWidget(self.patternInfoWidget)
        self.rightTopArea.tabBarClicked.connect(self.tabel_widget_tabbar_clicked)
        #
        # # 软件启动时，未加载程式，此时所有tab都设置为disable
        for idx in range(self.rightTopArea.count()):
            self.rightTopArea.setTabEnabled(idx, False)
        # # right buttom view
        # self.videoLabel = QtWidgets.QLabel()
        # self.videoLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        # self.videoLabel.setAlignment(QtCore.Qt.AlignCenter)
        # self.rightUnderArea = QtWidgets.QTabWidget()
        # self.rightUnderArea.addTab(self.patternInfoWidget, '视频区域')
        # self.rightUnderArea.addTab(self.locationWidget, '元件区域')
        #
        #
        # # right layout
        # rightLayout = QtWidgets.QVBoxLayout()
        # rightLayout.setSpacing(13)
        # rightLayout.addWidget(self.rightTopArea, 1)
        # rightLayout.addWidget(self.videoLabel, 1)
        #
        # hlayout = QtWidgets.QHBoxLayout()
        # hlayout.setSpacing(13)
        # hlayout.addWidget(self.scrollArea, 2)
        # hlayout.addLayout(rightLayout, 1)
        #
        # # main layout
        # layout = QtWidgets.QVBoxLayout()
        # layout.setSpacing(13)
        # layout.addWidget(self.toolbar)
        # layout.addLayout(hlayout)
        # self.setLayout(layout)
        # self.zoomInAction.triggered.connect(self.zoomIn)
        # self.zoomOutAction.triggered.connect(self.zoonOu)
        # # self.moveAction.triggered.connect(self.mobile)

    def mobile(self):
        self.canvas.zoomOutAction = False
        self.canvas.zoomInAction = False
        self.canvas.mobile = True

    def zoonOu(self):
        self.canvas.mobile = False
        self.canvas.zoomInAction = False
        self.canvas.zoomOutAction = True

    def zoomIn(self):
        self.canvas.mobile = False
        self.canvas.zoomInAction = True
        self.canvas.zoomOutAction = False
    def color_extract(self, label_pos, name, ngtype, path_name, similar_value,set_value):
        for par in self.pattern.parts:
            if par.name == name:
                par.leak_pos = label_pos
                par.leak_path = path_name
                par.leak_similar = similar_value
                if ngtype not in par.detection_type:
                    par.detection_type.append(ngtype)
                self.set_value = set_value
                self.save_pattern()
                break
    # 保存数据(相对元器件坐标点，元器件名称，类型，图片路径，相似度)
    def wrong_piece(self, label_pos, name, ngtype, path_name, similar_value):
        for par in self.pattern.parts:
            if par.name == name:
                if ngtype == "wrong_piece":
                    par.erron_pos = label_pos
                    par.content = path_name
                    par.rotation_angle = similar_value
                    if ngtype not in par.detection_type:
                        par.detection_type.append(ngtype)
                    self.save_pattern()
                    break
                else:
                    par.leak_pos = label_pos
                    par.leak_path = path_name
                    par.leak_similar = similar_value
                    if ngtype not in par.detection_type:
                        par.detection_type.append(ngtype)
                    self.save_pattern()
                    break


    def extremely_negative(self, pos_list, name, threshold_value, difference, ngtype):
        for par in self.pattern.parts:
            if par.name == name:
                par.Z_F_pos = pos_list
                par.Z_F_hold = threshold_value
                par.Z_gray = difference[0]
                par.F_gray = difference[1]
                if ngtype not in par.detection_type:
                    par.detection_type.append(ngtype)
                self.save_pattern()
                break

    def create_pattern(self):
        ''' 选择文件夹，创建程式 '''
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, '请选择一个程式文件夹', './')
        if not folder or not os.path.exists(folder):
            logger.debug('创建程式，选择不是文件夹')
            QtWidgets.QMessageBox.warning(self, '错误', '请选择一个文件夹路径')
            return
        logger.debug('创建程式成功，目录：%s'%folder)
        self.pattern = Pattern(folder=folder)
        self.partWidget.folder = self.pattern.folder
        self.pattern.dirty = False
        self.show_pattern_info()

    def load_pattern(self):
        ''' 选择程式并加载 '''
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, '选择程式文件夹', './')
        if not folder or not os.path.exists(folder):
            logger.debug('打开程式，选择不是文件夹')
            QtWidgets.QMessageBox.warning(self, '错误', '请选择正确的程式路径')
            return
        imagefile = os.path.join(folder, 'image.jpg')
        infofile = os.path.join(folder, 'info.json')
        if not os.path.exists(imagefile) or not os.path.exists(infofile):
            logger.debug('打开程式， 未查获取PCB版图片或Json文件')
            QtWidgets.QMessageBox.warning(self, '错误', '未找到程式信息，请选择正确的程式文件夹')
            return
        logger.debug('打开程式成功，目录：%s' % folder)
        self.pattern = Pattern.from_folder(folder)
        self.show_pattern_info()
        # 加载PCV数据
        originCVImage = cv_imread(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        pcbCVImage = originCVImage[y:y + h, x:x + w, :].copy()
        self.canvas.cvImage = pcbCVImage.copy()
        self.partWidget.cvImane = self.canvas.cvImage
        # 加载pixmap，并显示
        orgPixmap = QtGui.QPixmap(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        rectangle = QtCore.QRect(x, y, w, h)
        pixmap = orgPixmap.copy(rectangle)
        self.canvas.loadPixmap(pixmap)
        logger.debug('加载PCB版图片成功，并显示')
        shapes = []

        # PCB截图加载
        self.locationWidget.set_pixmap(self.locationWidget.pcbLabel, pixmap)

        # 模板加载
        for i, template in enumerate(self.pattern.templates):
            template.load_image(pcbCVImage)
            x, y, w, h = template.x, template.y, template.w, template.h
            # load shapes
            shape = Shape(name=template.name, shape_type='template')
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x + w, y + h)
            # shape.points["template"]
            shape.points.extend([p1, p2])
            shapes.append(shape)
            # init template widget
            self.templateWidget.templateList.append(template)
        logger.debug('绘制模板标注数据成功，并显示')
        # 加载Mask

        self.maskWidget.maskList.clear()
        for mask in self.pattern.masks:
            mask.load_image(pcbCVImage)
            x, y, w, h = mask.x, mask.y, mask.w, mask.h
            shape = Shape(name=mask.name, shape_type='mask')
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x + w, y + h)
            shape.points.extend([p1, p2])
            shapes.append(shape)

            # init mask widget
            self.maskWidget.maskList.append(mask)

        # 加载Part
        self.partWidget.partList.clear()
        for part in self.pattern.parts:
            part.load_image(pcbCVImage)
            x, y, w, h = part.x, part.y, part.w, part.h
            shape = Shape(name=part.name, shape_type='part', part_type=part.part_type)
            p1 = QtCore.QPoint(x, y)
            p2 = QtCore.QPoint(x + w, y + h)
            shape.points.extend([p1, p2])
            shapes.append(shape)
            self.partWidget.partList.append(part)
        logger.debug('绘制part标注数据成功，并显示')
        self.canvas.loadShapes(shapes)
        self.canvas.update()

        # 更新界面显示
        self.partWidget.folder = self.pattern.folder
        self.templateWidget.update_listwidget()
        # self.templateWidget.Pcanvase = self.canvas
        self.maskWidget.update_listwidget()
        self.maskWidget.Pcanvase = self.canvas
        self.partWidget.update_tablewidget()
        self.partWidget.Pcanvase = self.canvas
        # enable all tabs
        for idx in range(self.rightTopArea.count()):
            self.rightTopArea.setTabEnabled(idx, True)

    def new_shape(self, classes='', part_type=''):
        ''' 新增形状，classes为: template,mask,part; 当classes为part类型时，part_type需要指明具体元器件类型'''

        x, y, w, h, cvImage, pixmap = self.get_roi_image()
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
            part = Part(x, y, w, h, name, part_type)
            part.load_image(self.canvas.cvImage)
            self.pattern.parts.append(part)
            self.partWidget.set_part(part)
            self.partWidget.save_current()
        else:
            raise Exception('类型不匹配: ' + classes)
        self.pattern.dirty = True

    def paste_shape(self, classes, name, center_pos):
        if not self.pattern:
            return
        if classes == 'template':
            itemList = self.pattern.templates
            widget = self.templateWidget
            index = [x.name for x in itemList].index(name)
            w, h = itemList[index].w, itemList[index].h
            x = int(center_pos[0] - w // 2)
            y = int(center_pos[1] - h // 2)
            new_part = Template.obj_data(itemList[index], len(itemList), x, y)
            new_part.load_image(self.canvas.cvImage)
            itemList.append(new_part)
            name = classes + '_%s' % (len(itemList))
            nwe_shape = Shape(name=name, shape_type=classes)
        elif classes == 'mask':
            itemList = self.pattern.masks
            widget = self.maskWidget
            index = [x.name for x in itemList].index(name)
            w, h = itemList[index].w, itemList[index].h
            x = int(center_pos[0] - w // 2)
            y = int(center_pos[1] - h // 2)
            new_part = Mask.obj_data(itemList[index], len(itemList), x, y)
            new_part.load_image(self.canvas.cvImage)
            itemList.append(new_part)
            name = classes + '_%s' % (len(itemList))
            nwe_shape = Shape(name=name, shape_type=classes)
        elif classes == 'part':
            itemList = self.pattern.parts
            widget = self.partWidget
            index = [x.name for x in itemList].index(name)
            w, h = itemList[index].w, itemList[index].h
            x = int(center_pos[0] - w // 2)
            y = int(center_pos[1] - h // 2)
            new_part = Part.obj_data(itemList[index], len(itemList), x, y)
            new_part.load_image(self.canvas.cvImage)
            name = classes + '_%s' % (len(itemList)+1)
            if new_part.leak_path:
                path = self.pattern.folder+"/" + name+".jpg"
                x1, y1, x2, y2 = new_part.leak_pos
                num_image = new_part.cvColorImage[x1: y1, x2: y2]
                cv2.imwrite(path, num_image)

            itemList.append(new_part)

            nwe_shape = Shape(name=name, shape_type=classes, part_type=new_part.part_type)
        else:
            raise Exception('类型不匹配')

        x1 = int(center_pos[0] + w // 2)
        y1 = int(center_pos[1] + h // 2)
        # 更新界面
        widget.paste_by_name(new_part)
        nwe_shape.points = [QtCore.QPoint(x, y), QtCore.QPoint(x1, y1)]
        self.canvas.shapes.append(nwe_shape)

    def delete_shape(self, classes='', name=''):
        ''' 删除形状,在canvas中选中shape后，右键点击删除后触发。
            classes为: template,mask,part; name为列表显示的名称 '''
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
            widget = self.partWidget
        else:
            raise Exception('类型不匹配')

        index = [x.name for x in itemList].index(name)
        # pattern中数据删除/模板图片
        itemList.pop(index)
        path = self.partWidget.folder + "/%s.jpg" % name
        if os.path.exists(path):
            os.remove(path)

        # 更新界面
        widget.delete_by_name(name)
        # self.save_pattern()
        self.pattern.dirty = True

    def change_shape_coordinate(self, classes='', name=''):
        ''' 拖动形状导致坐标或者大小变换后触发，更新pattern参数及界面显示 '''
        if not self.pattern:
            return
        # step1: get coordinate
        shape = self.canvas.hShape
        rectangle = shape.getRectFromLine(*shape.points).toRect()
        x, y, w, h = rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height()
        pixmap = self.canvas.pixmap.copy(rectangle)
        # step2: update pattern and widget show
        if classes == 'location':
            logger.debug('修改PCB版图片大小')
            self.pattern.set_pcb_coordinate(x, y, w, h)
            self.locationWidget.set_pixmap(self.locationWidget.pcbLabel, pixmap)
        elif classes == 'template':
            logger.debug('修改模板图片大小，模板名称:%s'% name)
            template = [t for t in self.pattern.templates if t.name == name][0]
            template.coordinates_changed(x, y, w, h, self.pattern.pcbCVImage)
            self.templateWidget.update_pixmap_show()
        elif classes == 'mask':
            mask = [m for m in self.pattern.masks if m.name == name][0]
            mask.coordinates_changed(x, y, w, h, self.pattern.pcbCVImage)
            self.maskWidget.update_pixmap_show(False)
        elif classes == 'part':
            logger.debug('修改part图片大小，元件名称:%s' % name)
            part = [p for p in self.pattern.parts if p.name == name][0]
            part.coordinates_changed(x, y, w, h, self.pattern.pcbCVImage)
            self.partWidget.update_pixmap_show()
        else:
            raise Exception('类型不匹配: ' + classes)

        self.pattern.dirty = True

    def change_shape_parameter(self, classes='', name=''):
        ''' 界面中更改相关参数后触发 '''
        if not self.pattern:
            return
        # step1: get parameter
        # step2: update pattern
        self.pattern.dirty = True

    def seleted_shape_changed_from_canvas(self, shapes):
        if not shapes:
            return
        shape = shapes[0]
        if shape.shape_type == 'template':
            self.templateWidget.set_current_template_by_name(shape.name)
        if shape.shape_type == 'mask':
            self.maskWidget.set_current_mask_by_name(shape.name)
        elif shape.shape_type == 'part':
            self.partWidget.set_current_part_by_name(shape.name)
        else:  # TODO
            pass

    def selected_item_changed_from_widget(self, classes, name):
        ''' 界面中选中某个项，canvas中需要高亮此项 '''
        for shape in self.canvas.shapes:
            if shape.shape_type == classes and shape.name == name:
                if self.canvas.hShape:
                    self.canvas.hShape.selected = False
                    self.canvas.hShape.highlightClear()
                shape.selected = True
                self.shapeSelectionChanged([shape])
                self.canvas.hShape = shape
                self.canvas.update()
                break

    def has_pattern_and_pixmap(self):
        if not self.pattern:
            QtWidgets.QMessageBox.information(self, '提示', '请先创建或者载入程式')
            return False
        if not self.canvas.pixmap:
            QtWidgets.QMessageBox.information(self, '提示', '请先抓取图片')
            return False
        return True

    def show_pattern_info(self):
        if not self.pattern:
            return
        # self.rightTopArea.setTabEnabled(0, True)
        self.rightTopArea.setCurrentWidget(self.patternInfoWidget)
        self.patternInfoWidget.show_pattern_info(self.pattern.folder)

    def tabel_widget_tabbar_clicked(self, index):
        ''' 右上角tabwidget页面点击 '''
        self.canvas.copy_shape = None
        if index == 1:  # PCB定位页面
            logger.debug("查看PCB版界面")
            self.canvas.shape_type = 'location'
            self.locationWidget.update_pixmap_show()
        elif index == 2:  # template页面
            logger.debug("查看模板界面")
            self.canvas.shape_type = 'template'
            self.templateWidget.update_pixmap_show()
            # self.templateWidget.right_click_add()
        elif index == 3:  # mask页面
            logger.debug("查看Mask界面")
            self.canvas.shape_type = 'mask'
            self.maskWidget.update_pixmap_show(True)
            self.maskWidget.right_click_add()
        elif index == 4:  # part页面
            logger.debug("查看part界面")
            self.canvas.shape_type = 'part'
            self.partWidget.update_pixmap_show()
            self.partWidget.right_click_add()
        # 点击页面标签后，进入编辑模式
        self.canvas.setEditing(True)
        self.canvas.update()

    def mode_change_by_action(self):
        ''' 点击绘图Action的响应函数，用于切换绘制模型 '''
        self.canvas.zoomOutAction = False
        self.canvas.zoomInAction = False
        self.canvas.mobile = False
        if not self.has_pattern_and_pixmap():
            return
        action = self.sender()
        if action == self.pcbLocationAction:
            self.canvas.shape_type = 'location'
            self.canvas.part_type = ''
            self.rightTopArea.setTabEnabled(1, True)
            self.rightTopArea.setCurrentWidget(self.locationWidget)
        elif action == self.templateAction:
            logger.debug('选择模板绘制')
            # 仅支持绘制一个模板
            # if len(self.pattern.templates) >= 1:
            #     return
            # else:
            # 保存上次编辑
            if self.pattern.templates:
                self.save_template_info("")
            self.canvas.shape_type = 'template'
            self.canvas.part_type = ''
            self.rightTopArea.setTabEnabled(2, True)
            self.rightTopArea.setCurrentWidget(self.templateWidget)
        elif action == self.maskAction:
            logger.debug('选择电容绘制')
            self.canvas.shape_type = 'mask'
            self.canvas.part_type = ''
            self.rightTopArea.setTabEnabled(3, True)
            self.rightTopArea.setCurrentWidget(self.maskWidget)
        elif action in [self.capacitorAction, self.resistorAction, self.slotAction, self.componentAction,self.diodeAction]:
            self.canvas.shape_type = 'part'
            if action is self.capacitorAction:
                logger.debug('选择电容绘制')
                self.canvas.part_type = 'capacitor'
            elif action is self.resistorAction:
                logger.debug('选择电阻绘制')
                self.canvas.part_type = 'resistor'
            elif action is self.slotAction:
                logger.debug('选择插槽绘制')
                self.canvas.part_type = 'slot'
            elif action is self.componentAction:
                logger.debug('选择一般元件绘制')
                self.canvas.part_type = 'component'
            elif action is self.diodeAction:
                logger.debug('选择二极管绘制')
                self.canvas.part_type = 'diode'
            self.rightTopArea.setTabEnabled(4, True)
            self.rightTopArea.setCurrentWidget(self.partWidget)

        self.canvas.setEditing(False)
        self.canvas.update()

    def set_pattern_dirty(self):
        ''' 在mask_widget、template_widget及part_widget中，通过引用修改了pattern内部相关阈值参数，
            需要发射信号告知当前类pattern信息已经更改，避免用户直接点击退出导致pattern的改变未保存 '''
        self.pattern.dirty = True

    def save_pcb_base_infomation(self):
        if not self.pattern:
            return
        if not self.pattern.ax_pcbs:
            QtWidgets.QMessageBox.information(self, '提示', '请先获取PCB板')
            return
        self.canvas.scale = 0.42
        if self.canvas.shapes:
            x, y, w, h = self.pattern.ax_pcbs
            rectangle = QtCore.QRect(x, y, w, h)
            pixmap = self.canvas.pixmap.copy(rectangle)
            self.canvas.cvImage = self.canvas.cvImage[y:y + h, x:x + w, :].copy()
            self.canvas.loadPixmap(pixmap)
            self.canvas.update()
            # 设置 pcbCVImage
            self.pattern.pcbCVImage = self.pattern.originCVImage[y:y + h, x:x + w, :].copy()
            # 保存程式基础信息
            self.pattern.save()
            self.canvas.shapes = []

    def get_roi_image(self):
        ''' 获取模板或者PCB的相应函数。该函数截取用户绘制的区域，并显示在相应的widget中。
            此外，本函数还负责保存截取区域的坐标参数，作为程式的基础信息并保存 '''
        if not self.canvas.pixmap:
            raise Exception('请先获取图像')
        if not self.pattern:
            raise Exception('请先创建程式')
        # shapeList = self.canvas.modeToShapeList[self.canvas.shape_type]
        shape = self.canvas.shapes[-1]
        if len(shape.points) != 2:
            raise Exception('请先获取一个形状')
        rectangle = shape.getRectFromLine(*shape.points).toRect()
        # 保存坐标信息
        x, y, w, h = rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height()
        cvImage = self.canvas.cvImage[y:y + h, x:x + w, :].copy()
        pixmap = self.canvas.pixmap.copy(rectangle)
        return x, y, w, h, cvImage, pixmap

    def save_pattern(self):
        ''' 保存pattern信息；位置信息均来自canvas里面的shapes '''
        if not self.pattern:
            return
        if not self.pattern.ax_pcbs:
            print('error: location pcb first')
            return
        self.pattern.save()
        self.pattern.dirty = False

    def save_template_info(self,name):
        ''' 模板界面点击保存后触发，保存模型 '''
        ''' 模板界面点击保存后触发，保存模型 '''
        if not self.pattern:
            return
        tempdir = os.path.join(self.pattern.folder, 'template')
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        if name :
            for temp in self.pattern.templates:
                if temp.name == name:
                    temp.threshold = [self.templateWidget.color_lower,self.templateWidget.color_upper]
                    temp.combox_index = self.templateWidget.combox_index
                    break
        else:
            temp = self.pattern.templates[-1]
            temp.threshold = [self.templateWidget.color_lower, self.templateWidget.color_upper]
            temp.combox_index = self.templateWidget.combox_index
        self.save_pattern()
        # for temp in self.pattern.templates:
        #     cv2.imwrite("%s/%s.jpg"%(self.pattern.folder,"template"), temp.cvColorImage)
        #     temp.threshold = [self.templateWidget.color_lower,self.templateWidget.color_upper]
        #     temp.combox_index = self.templateWidget.combox_index
            # if not temp.generate_shape_matching(tempdir):
            #     QtWidgets.QMessageBox.warning(self, '提示', '模板[{}]生成失败，请重新选取'.format(temp.name))

    # React to canvas signals.
    def shapeSelectionChanged(self, selected_shapes):
        for shape in self.canvas.selectedShapes:
            shape.selected = False
            shape.highlightClear()
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
