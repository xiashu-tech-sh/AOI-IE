import os
import sys
import time
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from my_label import My_label
from pattern import Pattern
from utils import cv_imread
from PyQt5.QtCore import Qt

class OnlineWidget(QtWidgets.QWidget):
    ''' 在线检测界面, 包含组件：
        1. 工具栏，提供选择程式、启停、相机操作、程式设计入口等操作；
        2. 左边测试结果显示区域（imageLabel），用于显示检测结果；
        3. 右上角信息展示区域，显示当前检测相关信息；
        4. 右下角在线预览区域，实时展示相机画面。
    '''
    def __init__(self):
        super().__init__()
        # init actions
        new_action = lambda icon, text : QtWidgets.QAction(QtGui.QIcon(icon), text)
        self.patternSelectAction = new_action('./icon/folder-50.png', '选择程式')
        self.startAction = new_action('./icon/play-64.png', '开始检测')
        self.stopAction = new_action('./icon/stop-64.png', '停止检测')
        self.cameraOpenAction = new_action('./icon/camera-50.png', '打开相机')
        self.cameraCloseAction = new_action('./icon/camera-50-2.png', '关闭相机')
        self.videoAction = new_action('./icon/video-64.png', '载入视频')
        self.parameterAction = new_action('./icon/gear-50.png', '参数设置')
        self.designAction = new_action('./icon/design-64.png', '程式设计')

        self.patternSelectAction.triggered.connect(self.load_pattern)
        self.parameterAction.triggered.connect(self.match_template)
        self.stopAction.triggered.connect(self.stop)


        # init toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addActions([self.patternSelectAction, self.startAction, self.stopAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.cameraOpenAction, self.cameraCloseAction, self.videoAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.parameterAction, self.designAction])
        self.toolbar.setIconSize(QtCore.QSize(32, 32))

        # left center view
        self.imageLabel = My_label()
        self.imageLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        # self.imageLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        # self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)

        # right top view: TODO
        self.tableWidget =  QtWidgets.QTableWidget()
        # self.tableWidget.setHorizontalHeaderLabels(['PCB版号','子件名称','检测结果'])   # 水平标题，多列
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        _translate = QtCore.QCoreApplication.translate
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Form", "PCB版号"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "子件名称"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "检测结果"))
        # right buttom view
        self.videoLabel = QtWidgets.QLabel()
        self.videoLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        self.videoLabel.setAlignment(QtCore.Qt.AlignCenter)

        # right layout
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.setSpacing(13)
        rightLayout.addWidget(self.tableWidget, 1)

        rightLayout.addWidget(self.videoLabel, 1)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(13)
        hlayout.addWidget(self.imageLabel, 2)
        hlayout.addLayout(rightLayout, 1)

        # main layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(13)
        layout.addWidget(self.toolbar)
        layout.addLayout(hlayout)
        self.setLayout(layout)

        self.pattern = None
        self.isRunning = False
        self.lastCaptureTime = time.time()  # 上一次抓拍时间，防止同一时刻多次抓拍

        self.pos = []
        # 当前PCB个数
        self.ng_recording = []
        self.indexx = 0

        self.ratio = None
        self.gap = None
        self.w_or_h = False
        self.zoom_size = 100
        self.tem_num = None
        self.tem_color = None
        self.star_time = None
    def tem_colo_ver(self,tem):
        for color in ['blue','red','yellow','green','purple']:
            if color == 'blue':
                self.color_lower = np.array([100, 43, 46])
                self.color_upper = np.array([124, 255, 255])
            elif color == 'red':
                self.color_lower = np.array([0, 43, 46])
                self.color_upper = np.array([10, 255, 255])
            elif color == 'yellow':
                self.color_lower = np.array([26, 43, 96])
                self.color_upper = np.array([34, 255, 255])
            elif color == 'purple':
                self.color_lower = np.array([[50, 0, 150]])
                self.color_upper = np.array([180, 60, 255])
            img_hsv = cv2.cvtColor(tem, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(img_hsv, np.array(self.color_lower), np.array(self.color_upper))
            mask = cv2.medianBlur(mask, 7)  # 中值滤波
            cnts, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
            if cnts:
                cnt = max(cnts, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(cnt)
                if color == 'purple':
                    print("x, y, w, h11",x, y, w, h)
                    self.x_ = x
                    return
            # frame = cv2.GaussianBlur(tem, (5, 5), 0)
            # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
            # mask = cv2.erode(mask, None, iterations=2)
            # mask = cv2.GaussianBlur(mask, (3, 3), 0)
            # # 寻找轮廓并绘制轮廓
            # cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            #
            # w, h, z = frame.shape
            # if len(cnts) > 2:
            #     cnt = max(cnts, key=cv2.contourArea)
            #     min_rect = cv2.minAreaRect(cnt)
            #     area_min = min_rect[1][0] * min_rect[1][1]
            #     percentage = int(area_min / (w * h) * 100)
            #     print("percentage",percentage)
            #     self.tem_color = percentage
            #     break


    def load_pattern(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, '请选择一个程式文件夹', './')
        if not folder or not os.path.exists(folder):
            QtWidgets.QMessageBox.warning(self, '错误', '请选择一个文件夹路径')
            return
        self.pattern = Pattern.from_folder(folder=folder)

        # 加载CV数据
        imagefile = os.path.join(folder, 'image.jpg')
        originCVImage = cv_imread(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        self.pcbCVImage = originCVImage[y:y+h, x:x+w, :].copy()
        cv2.imwrite("temp2.jpg",self.pcbCVImage)

        # 模板加载
        self.pattern.templates[0].load_image(self.pcbCVImage)
        self.template = self.pattern.templates[0]
        # template.load_image(self.pcbCVImage)
        # tem_num = cv2.imread("%s/%s.jpg" % (self.pattern.folder, "template"))
        # self.tem_num = cv2.cvtColor(tem_num, cv2.COLOR_RGB2GRAY)
        # self.tem_colo_ver(tem_num)
        self.pos = [self.template.y+y ,self.template.h+self.template.y+y,self.template.x+x,self.template.w+self.template.x+x,]


        component_list = []
        slot_list = []
        capacitor_list = []
        for par in self.pattern.parts:
            if par.part_type == "slot":
                slot_list.append(par)
            elif par.part_type == "component":
                component_list.append(par)
            elif par.part_type =="capacitor":
                capacitor_list.append(par)
        self.slot_thread = SlotThread(slot_list)
        self.slot_thread.ng_signal.connect(self.ng_signal)
        self.slot_thread.start()

        self.capacitor_thread = CapacitorThread(capacitor_list,folder)
        self.capacitor_thread.ng_signal.connect(self.ng_signal)
        self.capacitor_thread.start()

        self.component_thread = ComponentThread(component_list,folder)
        self.component_thread.ng_signal.connect(self.ng_signal)
        self.component_thread.start()
        # self.model_thread.add_task_()

    def ng_signal(self, ng_list):
        self.indexx+=1
        self.ng_recording.extend(ng_list)
        self.tableWidget.clearContents()
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowCount)
        self.tableWidget.setRowCount(len(self.ng_recording))
        for i, ng in enumerate(self.ng_recording):
            for col, text in enumerate(ng):
                if col == 1:
                    for par in self.pattern.parts:
                        if par.name == text:
                            self.pos_conversion(par)
                self.tableWidget.setItem(i, col, QtWidgets.QTableWidgetItem(text))

    def pos_conversion(self,par):
        if self.w_or_h:
            x, y, w, h = par.x*self.ratio, par.y*self.ratio,par.w*self.ratio,par.h*self.ratio
            self.imageLabel.points.append([int(x), int(y), int(w), int(h)])
        else:
            x, y, w, h = par.x*self.ratio, par.y*self.ratio,par.w*self.ratio,par.h*self.ratio
            self.imageLabel.points.append([int(x), int(y), int(w), int(h)])
        self.imageLabel.update()
    def stop(self):
        self.isRunning = False

    def calculate(self,image1, image2):
        hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
        # 计算直方图的重合度
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree

    def match_template(self,cvImage):
        self.imageLabel.points=[]
        ''' 基于形状匹配算法匹配当前帧， 匹配到返回PCB坐标，否则返回None '''
        # if not self.isRunning:
        #     return
        # if not self.pattern.templates:
        #     print("推出")
        #     return
        # 3秒内不能重复检测
        if self.star_time:
            if time.time() - self.star_time < 3:
                print("时间间隔")
                return
        print("self.",self.pos[0],self.pos[1],self.pos[2]+self.template.num_features[2],self.pos[3]+self.template.num_features[2])
        new_temp = cvImage[self.pos[0]:self.pos[1],self.pos[2]-self.template.num_features[2]:self.pos[3]+self.template.num_features[2]]
        img_hsv = cv2.cvtColor(new_temp, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, np.array(self.template.threshold[0]), np.array(self.template.threshold[1]))
        mask = cv2.medianBlur(mask, 7)  # 中值滤波
        cnts, hierarchy, = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        if cnts:
            cnt = max(cnts, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点

            if h < self.template.num_features[3]/2 or w < self.template.num_features[2]/2:
                print("退出")
                return
            #51 30 128 127
            tep = new_temp[y:y+h,x:x+w]
            cv2.imwrite("1.jpg",new_temp)
            cv2.imwrite("0.jpg",tep)

            new_ = cvImage[self.pos[0]:self.pos[1],self.pos[2] :self.pos[3] ]
            cv2.imwrite("new_1.jpg", new_)
            cv2.imwrite("new_0.jpg",new_temp)
            cv2.rectangle(new_temp, (x,y), (x+w,y+h), (0,0,255), 2, 8)

            x_diff = x -self.template.num_features[2]- self.template.num_features[0]
            x, y, w, h = self.pattern.ax_pcbs

            new_pcv = cvImage[y:y + h, x+x_diff:x+x_diff + w].copy()
            # new_pcv = cvImage[y:y + h, x:x + w].copy()
            # cv2.imwrite("new_tep12.jpg", new_pcv)
            # tep = new_pcv[self.pos[0]:self.pos[1],self.pos[2]:self.pos[3]]
            # cv2.waitKey(0)
            cv2.imwrite("new_tep1.jpg", new_pcv)
            # cv2.imwrite("new_.jpg",tep)
        else:
            return


        # print("new_temp",new_temp.shape)
        # print("selg",self.tem_num.shape)
        # hrgb_temp = cv2.cvtColor(new_temp, cv2.COLOR_RGB2GRAY)
        # 模板匹配
        # w, h = self.tem_num.shape[0], self.tem_num.shape[1]
        # result = cv2.matchTemplate(new_temp, self.tem_num, cv2.TM_SQDIFF_NORMED)
        # cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # 颜色匹配
        # print(" self.color_lower, self.color_upper", self.color_lower, self.color_upper)
        # frame = cv2.GaussianBlur(new_temp, (5, 5), 0)
        # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        # mask = cv2.erode(mask, None, iterations=2)
        # mask = cv2.GaussianBlur(mask, (3, 3), 0)
        # # 寻找轮廓并绘制轮廓
        # cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        #
        # w, h, z = frame.shape
        # print("cnts",len(cnts))
        # if len(cnts) > 0:
        #     cnt = max(cnts, key=cv2.contourArea)
        #     min_rect = cv2.minAreaRect(cnt)
        #     area_min = min_rect[1][0] * min_rect[1][1]
        #     percentage = int(area_min / (w * h) * 100)
        #     end_time = time.time()
        #     print(end_time - star_time)
        #     print("self.tem_color",self.tem_color)
        #     print("percentage",percentage)
        #     if percentage < self.tem_color-20:
        #         print("退出")
        #         return
        # else:
        #     return
        # hrgb_temp = 0
        # result = cv2.matchTemplate(hrgb_temp, self.tem_num, cv2.TM_SQDIFF_NORMED)
        # cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # print("min_val, max_val, min_loc, max_loc",min_val, max_val, min_loc, max_loc)
        # x_size, y_size = min_loc[0]-self.zoom_size, min_loc[1]-self.zoom_size
        # cv2.imshow("tem",new_temp)
        # cv2.waitKey(0)
        #
        # end_time = time.time()
        # print(end_time-star_time)
        # x, y, w, h = self.pattern.ax_pcbs
        # new_pcv = cvImage[y+y_size:y+y_size + h, x+x_size:x+x_size + w, :].copy()
        self.imageLabel.height()
        rgbImage = cv2.cvtColor(new_pcv, cv2.COLOR_BGR2RGB)
        qt_image = QtGui.QImage(rgbImage, rgbImage.shape[1], rgbImage.shape[0], rgbImage.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        QPixmapImage = pixmap.scaled(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(QPixmapImage)
        pvc_height, pvc_width, n = new_pcv.shape
        imageheight, imagewidth = self.imageLabel.height(),self.imageLabel.width()
        if imageheight/pvc_height > imagewidth/pvc_width:
            self.w_or_h = True
            self.ratio = imagewidth/pvc_width
            self.gap = (imageheight - pvc_height * (imagewidth/pvc_width) )/2
        else:
            self.w_or_h = False
            self.ratio = imageheight/pvc_height
            self.gap = (imagewidth - pvc_width * (imageheight/pvc_height)  ) /2
        self.slot_thread.pcbImage = new_pcv.copy()
        self.capacitor_thread.pcbImage = new_pcv.copy()
        self.component_thread.pcbImage = new_pcv.copy()
        self.slot_thread.add_task_()
        self.capacitor_thread.add_task_()
        self.component_thread.add_task_()
        self.star_time = time.time()
    def template_matching(self,cu_image,or_image):
        sub_image1 = cv2.split(or_image)
        sub_image2 = cv2.split(cu_image)
        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)
        sub_data = sub_data / 3
        return sub_data

class SlotThread(QtCore.QThread):
    ng_signal = pyqtSignal(list)

    def __init__(self,slot_list):
        super().__init__()
        self.slot_list = slot_list
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.pcbImage = None
        self.current_pcb = 1

    def add_task_(self):
        with QtCore.QMutexLocker(self.mutex):
            # 唤醒线程
            self.taskAdded.wakeOne()
    def calculate(self,image1, image2):
        hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
        # 计算直方图的重合度
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree
    def template_matching(self,cu_image,or_image):
        sub_image1 = cv2.split(or_image)
        sub_image2 = cv2.split(cu_image)
        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)
        sub_data = sub_data / 3
        return sub_data
    def run(self):
        while True:
            with QtCore.QMutexLocker(self.mutex):
                self.taskAdded.wait(self.mutex)
            ng_recording = []
            for par in self.slot_list:
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                for ng_type in par.detection_type:
                    if ng_type == "missing_parts":
                        pos = par.leak_pos
                        temlate_path = par.leak_path
                        or_template = cv2.imread(temlate_path)
                        cu_template = mode[pos[0]:pos[1], pos[2]:pos[3]]
                        sub_data = self.template_matching(cu_template, or_template)
                        if sub_data >0.5 or sub_data==0.0:
                            print("检测漏检OK")
                        else:
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            print("检测漏检NG")
                    elif ng_type == "extremely_negative":
                        hsv = cv2.cvtColor(mode, cv2.COLOR_BGR2HSV)
                        cv2.imwrite("7.jpg", mode)
                        print("par.leak_similar",par.leak_similar)
                        mask = cv2.inRange(hsv, np.array(par.leak_similar[0]), np.array(par.leak_similar[1]))
                        mask = cv2.medianBlur(mask, 7)  # 中值滤波
                        cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
                        pos = par.Z_F_pos
                        w_h_list = []
                        for i in cnts1:  # 遍历所有的轮廓
                            x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
                            if x != 0:
                                w_h_list.append(i)
                        if w_h_list:
                            cnt = max(w_h_list, key=cv2.contourArea)
                        else:
                            print("退出")
                        x, y, w, h = cv2.boundingRect(cnt)
                        new_temp = mode[y:y+h,x:x+w]
                        cv2.imwrite("6.jpg",new_temp)
                        P_components = new_temp[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite("4.jpg",P_components)
                        negative_cropped = new_temp[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite("5.jpg",negative_cropped)
                        positive_lwpImg = cv2.cvtColor(P_components, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative_cropped, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        print("difference",difference)
                        if par.Z_gray - par.F_gray > 0:
                            if difference < 0:
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                print("检测极反OK")
                        elif par.Z_gray - par.F_gray < 0:
                            if difference > 0:
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                print("检测极反OK")
                # w, h, z = frame.shape
                # if len(cnts) > 0:
                #     cnt = max(cnts, key=cv2.contourArea)
                #     min_rect = cv2.minAreaRect(cnt)
                #     area_min = min_rect[1][0] * min_rect[1][1]
                #     percentage = int(area_min / (w * h) * 100)
                #     if par.leak_similar-20 > percentage:
                #         ng = [str(self.current_pcb), par.name, "错件",]
                #         ng_recording.append(ng)
                #     else:
                #         print("检测插槽OK")
                # else:
                #     print("颜色匹配失败")
            self.current_pcb += 1
            self.ng_signal.emit(ng_recording)

class CapacitorThread(QtCore.QThread):
    ng_signal = pyqtSignal(list)

    def __init__(self,capacitor_list,folder):
        super().__init__()
        self.capacitor_list = capacitor_list
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.pcbImage = None
        self.folder = folder
        self.current_pcb = 1
    def add_task_(self):
        with QtCore.QMutexLocker(self.mutex):
            # 唤醒线程
            self.taskAdded.wakeOne()

    def color_match(self, frame):
        lower_red = np.array([0, 0, 221])  # 白色阈值下界
        higher_red = np.array([180, 30, 255])  # 白色阈值上界
        img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(img_hsv, lower_red, higher_red)  # 可以认为是过滤出红色部分，获得红色的掩膜
        mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测 #红色
        if cnts1:
            cnt = max(cnts1, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            x = 0 if x - 20 < 0 else x - 20
            y = 0 if y - 20 < 0 else y - 20
            w = frame.shape[1] if x+w+40 > frame.shape[1] else x+w+40
            h = frame.shape[0] if y + h + 40 > frame.shape[0] else y + h + 40
            return x, y, w, h
        else:
            return 0,0,0,0
    def calculate(self,image1, image2):
        hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
        # 计算直方图的重合度
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree
    def template_matching(self,cu_image,or_image):
        sub_image1 = cv2.split(or_image)
        sub_image2 = cv2.split(cu_image)
        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)
        sub_data = sub_data / 3
        return sub_data
    def run(self):
        while True:
            with QtCore.QMutexLocker(self.mutex):
                self.taskAdded.wait(self.mutex)
            ng_recording = []
            for par in self.capacitor_list:
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                cv2.imwrite("000.jpg",mode)
                for ng_type in par.detection_type:
                    if ng_type == "missing_parts":
                        pos = par.leak_pos
                        temlate_path = par.leak_path
                        or_template = cv2.imread(temlate_path)
                        cu_template = mode[pos[0]:pos[1], pos[2]:pos[3]]
                        cv2.imwrite("0.jpg",cu_template)
                        sub_data = self.template_matching(cu_template, or_template)
                        if sub_data >0.5 //100 or sub_data==0.0:
                            print("检测漏检OK")
                        else:
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            print("检测漏检NG")
                    elif ng_type == "extremely_negative":
                        pos = par.Z_F_pos
                        x,y,w,h = self.color_match(mode)
                        if x == 0 and w == 0:
                            return
                        new_temp = mode[y:y+h+40, x:x+w+40]
                        print("oar",par.name)
                        cv2.imwrite("00.jpg",new_temp)
                        P_components = new_temp[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite("1.jpg",P_components)
                        negative_cropped = new_temp[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite("2.jpg",negative_cropped)
                        positive_lwpImg = cv2.cvtColor(P_components, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative_cropped, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        if par.Z_gray - par.F_gray > 0:
                            if difference < 0:
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                print("检测极反OK")
                        if par.Z_gray - par.F_gray < 0:
                            if difference > 0:
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                print("检测极反OK")
            self.current_pcb += 1
            self.ng_signal.emit(ng_recording)

class ComponentThread(QtCore.QThread):
    ng_signal = pyqtSignal(list)

    def __init__(self,component_list,folder):
        super().__init__()
        self.component_list = component_list
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.pcbImage = None
        self.model = None
        self.current_pcb = 1
        self.folder = folder

    def add_task_(self):
        with QtCore.QMutexLocker(self.mutex):
            # 唤醒线程
            self.taskAdded.wakeOne()
    def calculate(self,image1, image2):
        hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
        # 计算直方图的重合度
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree
    def template_matching(self,cu_image,or_image):
        sub_image1 = cv2.split(or_image)
        sub_image2 = cv2.split(cu_image)
        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)
        sub_data = sub_data / 3
        return sub_data
    def run(self):
        while True:
            with QtCore.QMutexLocker(self.mutex):
                self.taskAdded.wait(self.mutex)
            ng_recording = []
            for par in self.component_list:
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                for detection_type in par.detection_type:
                    if detection_type == "extremely_negative":

                        data = cv2.imread("%s/%s.jpg"%(self.folder,par.name),0)
                        w,h = data.shape[0],data.shape[1]
                        new_mode = cv2.cvtColor(mode, cv2.COLOR_RGB2GRAY)
                        result = cv2.matchTemplate(new_mode, data, cv2.TM_CCORR_NORMED)
                        # cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
                        # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        print("min_val, max_val, min_loc, max_loc",min_val, max_val, min_loc, max_loc)
                        cvtest = mode[min_loc[1]:min_loc[1]+w, min_loc[0]:min_loc[0]+h]
                        cv2.imwrite("18.jpg",data)
                        cv2.imwrite("19.jpg", mode)
                        pos = par.Z_F_pos
                        cv2.imwrite("20.jpg",cvtest)
                        P_components = cvtest[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        negative_cropped = cvtest[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite("21.jpg",P_components)
                        cv2.imwrite("22.jpg",negative_cropped)
                        positive_lwpImg = cv2.cvtColor(P_components, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative_cropped, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        print("self.pcbImage",self.pcbImage.shape)
                        print("par.y:par.y + par.h, par.x:par.x + par.w", par.y, par.y + par.h, par.x,
                              par.x + par.w)
                        print("difference", difference)
                        print("par", par.name)
                        print("min_loc", min_loc)
                        cv2.imwrite("9.jpg", data)
                        cv2.imwrite("10.jpg", mode)
                        cv2.imwrite("11.jpg", cvtest)
                        cv2.imwrite("12.jpg", P_components)
                        cv2.imwrite("13.jpg", negative_cropped)
                        cv2.imwrite("14.jpg", self.pcbImage)
                        if difference < 0:

                            ng = [str(self.current_pcb), par.name, "极反"]
                            ng_recording.append(ng)
                            print("检测极反NG")
                        else:
                            print("检测极反OK")

                    elif detection_type == "missing_parts":
                        pos = par.leak_pos
                        temlate_path = par.leak_path
                        print("temlate_path",temlate_path)
                        or_template = cv2.imread(temlate_path)
                        cu_template = mode[pos[0]:pos[1], pos[2]:pos[3]]
                        # cv2.imwrite("miss.jpg", cu_template)
                        sub_data = self.template_matching(cu_template, or_template)
                        if sub_data >par.leak_similar[0] //100 or sub_data==0.0:
                            print("检测漏检OK")
                        else:
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            print("检测漏检NG")

                    elif detection_type == "wrong_piece":
                        pos = par.erron_pos
                        data = cv2.imread("%s/%s.jpg"%(self.folder,par.name))
                        w,h = data.shape[0],data.shape[1]
                        result = cv2.matchTemplate(mode, data, cv2.TM_SQDIFF_NORMED)
                        cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
                        # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        cvtest = mode[min_loc[0]:min_loc[0]+w,min_loc[1]:min_loc[1]+h]
                        if self.model:
                            image_array = cvtest[pos[0]:pos[1], pos[2]:pos[3]]
                            rows, cols, = image_array.shape[0], image_array.shape[1]
                            angle = cv2.getRotationMatrix2D((cols // 2, rows // 2), par.rotation_angle, 0.5)
                            pcv_numpy = cv2.warpAffine(image_array, angle, (cols*2, rows))
                            cv2.imwrite("rowe.jpg",pcv_numpy)
                            stru = self.model.segmentation(pcv_numpy)
                            print("stru",stru)
                            stru = stru.replace('2', 'Z')
                            data = par.content.replace('2', 'Z')


                            if stru != data:
                                ng = [str(self.current_pcb), par.name, "错件"]
                                ng_recording.append(ng)
                                print("检测错件NG")
                            else:
                                print("检测错件OK")
            self.current_pcb += 1
            self.ng_signal.emit(ng_recording)
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = OnlineWidget()
    win.showMaximized()
    sys.exit(app.exec_())

