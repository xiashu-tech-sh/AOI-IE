import os
import sys
import time
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from pattern import Pattern
from utils import cv_imread
from ui.online_widget_ui import Ui_MainWindow
import logging

logger = logging.getLogger('main.mod.submod')
logger.debug('检测界面')


class OnlineWidget(QtWidgets.QMainWindow, Ui_MainWindow):
    ''' 在线检测界面, 包含组件：
        1. 工具栏，提供选择程式、启停、相机操作、程式设计入口等操作；
        2. 左边测试结果显示区域（imageLabel），用于显示检测结果；
        3. 右上角信息展示区域，显示当前检测相关信息；
        4. 右下角在线预览区域，实时展示相机画面。
    '''
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.patternSelectAction.triggered.connect(self.load_pattern)
        self.parameterAction.triggered.connect(self.match_template)
        self.stopAction.triggered.connect(self.stop)
        self.pattern = None
        self.isRunning = False
        self.lastCaptureTime = time.time()  # 上一次抓拍时间，防止同一时刻多次抓拍

        self.pos = []
        # 当前PCB个数
        self.ng_recording = []
        self.indexx = 0
        self.ratio = None
        self.w_or_h = False
        self.star_time = None
        self.slot_ = False

    def load_pattern(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, '请选择一个程式文件夹', './')
        logger.debug('检测程式目录：%s'%folder)
        if not folder or not os.path.exists(folder):
            logger.debug( '文件夹路径错误')
            QtWidgets.QMessageBox.warning(self, '错误', '请选择一个文件夹路径')

            return
        self.pattern = Pattern.from_folder(folder=folder)

        # 加载CV数据
        imagefile = os.path.join(folder, 'image.jpg')
        originCVImage = cv_imread(imagefile)
        x, y, w, h = self.pattern.ax_pcbs
        self.pcbCVImage = originCVImage[y:y+h, x:x+w, :].copy()
        cv2.imwrite("save_image/org_pcb.jpg",self.pcbCVImage)
        logger.debug('初始化PCB数据成功')
        # 模板加载
        self.pattern.templates[0].load_image(self.pcbCVImage)
        self.template = self.pattern.templates[0]
        self.pos = [self.template.y+y ,self.template.h+self.template.y+y,self.template.x+x,self.template.w+self.template.x+x,]
        logger.debug('初始化模板数据成功')


        component_list = []
        slot_list = []
        capacitor_list = []
        diode_list = []
        resistor_list = []
        for par in self.pattern.parts:
            if par.part_type == "slot":
                slot_list.append(par)
            elif par.part_type == "component":
                component_list.append(par)
            elif par.part_type =="capacitor":
                capacitor_list.append(par)
            elif par.part_type == "diode":
                diode_list.append(par)
            elif par.part_type == "resistor":
                resistor_list.append(par)
        # 插槽
        self.slot_thread = SlotThread(slot_list)
        self.slot_thread.ng_signal.connect(self.ng_signal)
        self.slot_thread.start()
        # 电容
        self.capacitor_thread = CapacitorThread(capacitor_list,folder)
        self.capacitor_thread.ng_signal.connect(self.ng_signal)
        self.capacitor_thread.start()
        # 一般元件
        self.component_thread = ComponentThread(component_list,folder)
        self.component_thread.ng_signal.connect(self.ng_signal)
        self.component_thread.start()
        # 二极管
        self.diode_thread = DiodeThread(diode_list,folder)
        self.diode_thread.ng_signal.connect(self.ng_signal)
        self.diode_thread.start()
        # 色环电阻
        self.resistor_thread = ResistorThread(resistor_list)
        self.resistor_thread.ng_signal.connect(self.ng_signal)
        self.resistor_thread.start()
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
        #     logger.debug("当前为停止检测")
        #     return
        if not self.pattern.templates:
            logger.debug("模板为空")
            return
        # 3秒内不能重复检测
        if self.star_time:
            if time.time() - self.star_time < 60:
                logger.debug("两次检测间隔小于3秒")
                return
        new_temp = cvImage[self.pos[0]:self.pos[1],self.pos[2]:cvImage.shape[1]]
        cv2.imwrite("save_image/newtem.jpg",new_temp)
        img_hsv = cv2.cvtColor(new_temp, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, np.array(self.template.threshold[0]), np.array(self.template.threshold[1]))
        mask = cv2.medianBlur(mask, 7)  # 中值滤波
        cnts, hierarchy, = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        if cnts:
            cnt = max(cnts, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            print("x, y, w, h",x, y, w, h)
            # cv2.rectangle(new_temp, (x,y), (x+w,y+h), (0,0,255), 2, 8)
            cv2.imwrite("save_image/newtem1.jpg", new_temp)
            x_diff =self.template.num_features[2]+self.template.num_features[0] - x -w
            print("x_diff",x_diff)
            x, y, w, h = self.pattern.ax_pcbs
            new_pcv = cvImage[y:y + h, x-x_diff:x-x_diff + w].copy()
            cv2.imwrite("save_image/new_pcv1.jpg", new_pcv)
        else:
            logger.debug("模板颜色匹配失败")
            return
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
        self.slot_thread.pcbImage = new_pcv.copy()
        self.capacitor_thread.pcbImage = new_pcv.copy()
        self.component_thread.pcbImage = new_pcv.copy()
        self.diode_thread.pcbImage = new_pcv.copy()
        self.slot_thread.add_task_()
        self.capacitor_thread.add_task_()
        self.diode_thread.add_task_()
        self.star_time = time.time()
class ResistorThread(QtCore.QThread):
    ng_signal = pyqtSignal(list)

    def __init__(self,resistor_list):
        super().__init__()
        self.resistor_list = resistor_list
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.pcbImage = None
        self.current_pcb = 1
        logger.debug('检测色环电阻线程初始化成功，检测个数为：%s'% len(self.resistor_list))

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
            for par in self.resistor_list:
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                path = "save_image/%s/" % par.name
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path+"temp.jpg", mode)
                for ng_type in par.detection_type:
                    if ng_type == "missing_parts":
                        hsv = cv2.cvtColor(mode, cv2.COLOR_BGR2HSV)
                        mask = cv2.inRange(hsv, np.array(par.leak_pos[0]), np.array(par.leak_pos[1]))
                        mask = cv2.medianBlur(mask, 7)  # 中值滤波
                        cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
                        pos = par.Z_F_pos
                        cnt = max(cnts1, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(cnt)
                        new_temp = mode[y:y+h,x:x+w]
                        temlate_path = par.leak_path
                        old_temp = cv2.imread(temlate_path)
                        sub_data = self.template_matching(new_temp,old_temp)
                        if sub_data > 0.7:
                            print("检测漏检OK")
                        else:
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            print("检测漏检NG")
                            continue
                    elif ng_type == "extremely_negative":

                        cv2.imwrite(path+"new_par.jpg",new_temp)
                        P_components = new_temp[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite(path+"new_Z.jpg",P_components)
                        negative_cropped = new_temp[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite(path+"new_F.jpg",negative_cropped)
                        positive_lwpImg = cv2.cvtColor(P_components, cv2.COLOR_BGR2GRAY)
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative_cropped, cv2.COLOR_BGR2GRAY)
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
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

            self.current_pcb += 1
            self.ng_signal.emit(ng_recording)

class SlotThread(QtCore.QThread):
    ng_signal = pyqtSignal(list)

    def __init__(self,slot_list):
        super().__init__()
        self.slot_list = slot_list
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.pcbImage = None
        self.current_pcb = 1
        logger.debug('检测插槽线程初始化成功，检测个数为：%s'% len(self.slot_list))

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
        sub_data = (sub_data / 3)[0]
        return sub_data
    def run(self):
        while True:
            with QtCore.QMutexLocker(self.mutex):
                self.taskAdded.wait(self.mutex)
            ng_recording = []
            for par in self.slot_list:
                logger.debug("插槽当前检测名称：%s"% par.name)
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                path = "save_image/%s/" % par.name
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path+"temp.jpg", mode)
                for ng_type in par.detection_type:
                    if ng_type == "missing_parts":
                        hsv = cv2.cvtColor(mode, cv2.COLOR_BGR2HSV)
                        mask = cv2.inRange(hsv, np.array(par.leak_pos[0]), np.array(par.leak_pos[1]))
                        mask = cv2.medianBlur(mask, 7)  # 中值滤波
                        cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                        pos = par.Z_F_pos
                        if len(par.leak_pos) == 3:
                            w_ = par.leak_pos[2][0]-5
                            w__ = par.leak_pos[2][0] + 5
                            h_ = par.leak_pos[2][1]-5
                            h__ = par.leak_pos[2][1]+5
                            for i in cnts1:  # 遍历所有的轮廓
                                x, y, w, h = cv2.boundingRect(i)
                                if w_ < w< w__ and h_ < h<h__:
                                    self.slot_ = True
                                    new_temp = mode[y:y + h, x:x + w]
                                    break
                            if self.slot_:
                                logger.debug("%s检测漏件OK" % par.name)
                                continue
                                self.slot_ = False
                            else:
                                logger.debug("%s检测漏件NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "漏检"]
                                ng_recording.append(ng)
                                continue
                        else:
                            cnt = max(cnts1, key=cv2.contourArea)
                            x, y, w, h = cv2.boundingRect(cnt)
                        new_temp = mode[y:y+h,x:x+w]
                        temlate_path = par.leak_path
                        old_temp = cv2.imread(temlate_path)
                        sub_data = self.template_matching(new_temp,old_temp)
                        logger.debug("%s检测漏件相似度为：%s"%(par.name,sub_data))
                        if sub_data > 0.5:
                            logger.debug("%s检测漏件OK" % par.name)
                        else:
                            logger.debug("%s检测漏件NG" % par.name)
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            continue
                    elif ng_type == "extremely_negative":
                        cv2.imwrite(path+"new_par.jpg",new_temp)
                        positive = new_temp[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite(path+"new_Z.jpg",positive)
                        negative = new_temp[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite(path+"new_F.jpg",negative)
                        positive_lwpImg = cv2.cvtColor(positive, cv2.COLOR_BGR2GRAY)
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative, cv2.COLOR_BGR2GRAY)
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        logger.debug("%s正极灰度值：%s，负极灰度值：%s" % (par.name,positive_mean,negative_mean))
                        logger.debug("%s标注正极灰度值：%s，标注负极灰度值：%s" % (par.name, par.Z_gray, par.F_gray))
                        logger.debug("%s,标注正负极灰度差：%s，当前正负极灰度值：%s" % (par.name, (par.Z_gray - par.F_gray), difference))
                        if par.Z_gray - par.F_gray > 0:
                            if difference < 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)
                        elif par.Z_gray - par.F_gray < 0:
                            if difference > 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)

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
        logger.debug('检测电容线程初始化成功，检测个数为：%s' % len(self.capacitor_list))

    def add_task_(self):
        with QtCore.QMutexLocker(self.mutex):
            self.taskAdded.wakeOne()

    def color_match(self, mode, par):
        img_hsv = cv2.cvtColor(mode, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(img_hsv, np.array(par.leak_pos[0]), np.array(par.leak_pos[1]))
        mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        mode_w, mode_h = mode.shape[:2]
        if cnts1:
            cnt = max(cnts1, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
            h = y + h
            w = x + w
            if par.leak_similar == "overall":
                x = 0 if x - 20 < 0 else x - 20
                y = 0 if y - 20 < 0 else y - 20
                w = mode_h if w + 20 > mode_h else w + 20
                h = mode_w if h + 20 > mode_w else h + 20
            elif par.leak_similar == "on":
                y = 0 if y - 20 < 0 else y - 20
            elif par.leak_similar == "under":
                h = mode_w if h + 20 > mode_w else h + 20
            elif par.leak_similar == "left":
                x = 0 if x - 20 < 0 else x - 20
            elif par.leak_similar == "right":
                w = mode_h if w + 20 > mode_h else w + 20
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
                logger.debug("电容当前检测名称：%s" % par.name)
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                path = "save_image/%s/" % par.name
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path+"temp.jpg",mode)
                for ng_type in par.detection_type:
                    if ng_type == "missing_parts":
                        temlate_path = par.leak_path
                        or_template = cv2.imread(temlate_path)
                        x,y,w,h = self.color_match(mode,par)
                        new_temp = mode[y:h, x:w]
                        cv2.imwrite(path + "new_tep.jpg", new_temp)
                        sub_data = self.template_matching(new_temp, or_template)
                        logger.debug("%s, 检测漏件相似度为：%s"%(par.name,sub_data))
                        if sub_data > 0.5:
                            logger.debug("%s, 检测漏件OK" % par.name)
                        else:
                            logger.debug("%s, 检测漏件NG" % par.name)
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            continue
                    elif ng_type == "extremely_negative":
                        pos = par.Z_F_pos
                        positive = new_temp[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite(path + "new_Z.jpg", positive)
                        negative = new_temp[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite(path + "new_F.jpg", positive)
                        positive_lwpImg = cv2.cvtColor(positive, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        logger.debug("%s正极灰度值：%s，负极灰度值：%s" % (par.name,positive_mean,negative_mean))
                        logger.debug("%s标注正极灰度值：%s，标注负极灰度值：%s" % (par.name, par.Z_gray, par.F_gray))
                        logger.debug("%s,标注正负极灰度差：%s，当前正负极灰度值：%s" % (par.name, (par.Z_gray - par.F_gray), difference))
                        if par.Z_gray - par.F_gray > 0:
                            if difference < 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)
                        elif par.Z_gray - par.F_gray < 0:
                            if difference > 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)
                    elif ng_type == "wrong_piece":
                        if self.model:
                            pos = par.erron_pos
                            _temp = new_temp[pos[0]:pos[1], pos[2]:pos[3]]
                            cv2.imwrite(path + "erron.jpg", positive)
                            rows, cols, = _temp.shape[0], _temp.shape[1]
                            angle = cv2.getRotationMatrix2D((cols // 2, rows // 2), int(par.rotation_angle), 0.5)
                            pcv_numpy = cv2.warpAffine(_temp, angle, (cols*2, rows))
                            cv2.imwrite(path + "od_erron.jpg", pcv_numpy)
                            stru = self.model.segmentation(pcv_numpy)
                            stru = stru.replace('2', 'Z')
                            data = par.content.replace('2', 'Z')
                            logger.debug("%s,检测错件值为：%s，原始值为：%s" % (par.name,stru,par.content))
                            if stru != data:
                                logger.debug("%s,检测错件为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "错件"]
                                ng_recording.append(ng)
                                print("检测错件NG")
                            else:
                                logger.debug("%s,检测错件为OK" % par.name)
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
        logger.debug('检测一般元件线程初始化成功，检测个数为：%s' % len(self.component_list))

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
                path = "save_image/%s/" % par.name
                if not os.path.exists(path):
                    os.makedirs(path)
                for detection_type in par.detection_type:
                    logger.debug("一般元件当前检测名称：%s" % par.name)
                    if detection_type == "missing_parts":
                        pos = par.leak_pos
                        temlate_path = par.leak_path
                        or_template = cv2.imread(temlate_path)
                        cu_template = mode[pos[0]:pos[1], pos[2]:pos[3]]
                        sub_data = self.template_matching(cu_template, or_template)
                        if sub_data >par.leak_similar[0] //100:
                            logger.debug("%s,检测漏件为OK" % par.name)
                        else:
                            logger.debug("%s,检测极反为NG" % par.name)
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            continue
                    elif detection_type == "extremely_negative":
                        data = cv2.imread("%s/%s.jpg"%(self.folder,par.name),0)
                        w,h = data.shape[0],data.shape[1]
                        new_mode = cv2.cvtColor(mode, cv2.COLOR_RGB2GRAY)
                        result = cv2.matchTemplate(new_mode, data, cv2.TM_CCORR_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        cvtest = mode[min_loc[1]:min_loc[1]+w, min_loc[0]:min_loc[0]+h]
                        pos = par.Z_F_pos
                        pos = par.Z_F_pos
                        positive = cvtest[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite(path + "new_Z.jpg", positive)
                        negative = cvtest[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite(path + "new_F.jpg", positive)
                        positive_lwpImg = cv2.cvtColor(positive, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        if par.Z_gray - par.F_gray > 0:
                            if difference < 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)
                        elif par.Z_gray - par.F_gray < 0:
                            if difference > 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)

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
                            angle = cv2.getRotationMatrix2D((cols // 2, rows // 2), int(par.rotation_angle), 0.5)
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


class DiodeThread(QtCore.QThread):
    ng_signal = pyqtSignal(list)

    def __init__(self,diode_list,folder):
        super().__init__()
        self.diode_list = diode_list
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.pcbImage = None
        self.folder = folder
        self.current_pcb = 1
        logger.debug('检测二极管线程初始化成功，检测个数为：%s' % len(self.diode_list))

    def add_task_(self):
        with QtCore.QMutexLocker(self.mutex):
            self.taskAdded.wakeOne()

    def color_match(self, mode, par):
        img_hsv = cv2.cvtColor(mode, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(img_hsv, np.array(par.leak_pos[0]), np.array(par.leak_pos[1]))
        mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
        cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        mode_w, mode_h = mode.shape[:2]
        if cnts1:
            cnt = max(cnts1, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
            h = y + h
            w = x + w
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
            for par in self.diode_list:
                logger.debug("二极管当前检测名称：%s" % par.name)
                mode = self.pcbImage[par.y:par.y + par.h, par.x:par.x + par.w]
                path = "save_image/%s/" % par.name
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path+"temp.jpg",mode)
                for ng_type in par.detection_type:
                    if ng_type == "missing_parts":
                        temlate_path = par.leak_path
                        or_template = cv2.imread(temlate_path)
                        x,y,w,h = self.color_match(mode,par)
                        new_temp = mode[y:h, x:w]
                        cv2.imwrite(path + "new_tep.jpg", new_temp)
                        sub_data = self.template_matching(new_temp, or_template)
                        logger.debug("%s, 检测漏件相似度为：%s"%(par.name,sub_data))
                        if sub_data > 0.7:
                            logger.debug("%s, 检测漏件OK" % par.name)
                        else:
                            logger.debug("%s, 检测漏件NG" % par.name)
                            ng = [str(self.current_pcb), par.name, "漏检"]
                            ng_recording.append(ng)
                            continue
                    elif ng_type == "extremely_negative":
                        pos = par.Z_F_pos
                        positive = new_temp[pos[0][0]:pos[0][1], pos[0][2]:pos[0][3]]
                        cv2.imwrite(path + "new_Z.jpg", positive)
                        negative = new_temp[pos[1][0]:pos[1][1], pos[1][2]:pos[1][3]]
                        cv2.imwrite(path + "new_F.jpg", negative)
                        positive_lwpImg = cv2.cvtColor(positive, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        positive_mean = np.mean(positive_lwpImg)
                        negative_lwpImg = cv2.cvtColor(negative, cv2.COLOR_BGR2GRAY)  # 转为灰度图
                        negative_mean = np.mean(negative_lwpImg)
                        difference = int(positive_mean) - int(negative_mean)
                        logger.debug("%s正极灰度值：%s，负极灰度值：%s" % (par.name,positive_mean,negative_mean))
                        logger.debug("%s标注正极灰度值：%s，标注负极灰度值：%s" % (par.name, par.Z_gray, par.F_gray))
                        logger.debug("%s,标注正负极灰度差：%s，当前正负极灰度值：%s" % (par.name, (par.Z_gray - par.F_gray), difference))
                        if par.Z_gray - par.F_gray > 0:
                            if difference < 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)
                        elif par.Z_gray - par.F_gray < 0:
                            if difference > 0:
                                logger.debug("%s,检测极反为NG" % par.name)
                                ng = [str(self.current_pcb), par.name, "极反"]
                                ng_recording.append(ng)
                            else:
                                logger.debug("%s,检测极反为OK" % par.name)

            self.current_pcb += 1
            self.ng_signal.emit(ng_recording)
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = OnlineWidget()
    win.showMaximized()
    sys.exit(app.exec_())

