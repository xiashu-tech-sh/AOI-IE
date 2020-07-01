import os
import sys
sys.path.append('./MvImport')
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QMutex
from PyQt5.QtWidgets import QMessageBox

from board import Board
from online_widget import OnlineWidget
from pattern_widget import PatternWidget

# from MvImport.MvCameraControl_class import *
from camera import CameraObj, CameraError, CameraThread, VideoSource


SOURCE_CAMERA = 0
SOURCE_VIDEO = 1

class MainWin(QtWidgets.QMainWindow):
    ''' 主界面。centerWidget由一个QStackWidget构成，QStackWidget添加了以下两个界面：
            1. onile_widget.py文件中的OnlineWidget界面，默认显示；
            2. pattern_widget.py文件中的PatternWidget界面，程式制作界面；
        以上两个界面通过各自界面的工具栏最右方按钮进行切换。
    '''


    def __init__(self):

        super().__init__()
        self.setWindowIcon(QtGui.QIcon('./icon/xiashu.png'))
        self.setWindowTitle('全自动光学检测系统 - 夏数科技')
        self.board = Board()
        self.onlineWidget = OnlineWidget()
        self.patternWidget = PatternWidget()

        self.stackWidget = QtWidgets.QStackedWidget()
        self.stackWidget.addWidget(self.onlineWidget)
        self.stackWidget.addWidget(self.patternWidget)

        self.setCentralWidget(self.stackWidget)

        # switch between onlineWidget and patternWidget
        self.onlineWidget.designAction.triggered.connect(lambda: self.stackWidget.setCurrentWidget(self.patternWidget))
        self.patternWidget.homeAction.triggered.connect(lambda: self.stackWidget.setCurrentWidget(self.onlineWidget))
        self.QPixmapImage = None
        # 相机初始化
        self.cam = CameraObj()
        try:
            self.cam.connect()
        except CameraError as e:
            self.error_messagebox(str(e))
        self.cameraThread = CameraThread(self.cam)
        self.cameraThread.newImageSignal.connect(self.show_image)
        # 选择程式
        self.onlineWidget.patternSelectAction.triggered.connect(self.pattern_select_action)
        # 开始检测
        # 停止检测
        # 打开相机
        self.onlineWidget.cameraOpenAction.triggered.connect(self.camera_open_action)
        # 关闭相机
        self.onlineWidget.cameraCloseAction.triggered.connect(self.camera_close_action)
        # 载入视频
        self.source = SOURCE_CAMERA
        self.onlineWidget.videoAction.triggered.connect(self.set_video_source)
        # 参数设置
        # 程式设计

        # 新建程式
        self.patternWidget.createAction.triggered.connect(self.choose_directory)
        # 保存程式
        # 打开程式
        # 抓取图像
        self.patternWidget.captureAction.triggered.connect(self.load_image_to_canvas)
        # 放大
        # 缩小
        # 选择
        # 移动
        # PCB 定位
        # self.patternWidget.
        # Mask
        self.patternWidget.maskAction.triggered.connect(self.mask_action)
        # 电解电容
        # 色环电阻
        # 插槽
        # 一般元件
    def choose_directory(self, path):
        # self.board.dir_path = path
        pass

    def set_video_source(self):
        # filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, '本地视频文件', '')
        filename = '../JT/test.mp4'
        if not filename or not os.path.exists(filename):
            return
        self.video = VideoSource(filename)
        self.video.newImageSignal.connect(self.show_image)
        self.source = SOURCE_VIDEO

    def load_image_to_canvas(self):
        ''' 点击[抓取图像]按钮后触发抓图，并显示 '''
        if self.source == SOURCE_CAMERA:
            source = self.cameraThread
        else:
            source = self.video

        if not source.isRunning():
            return
        pixmap = source.get_pixmap()
        if not pixmap:
            return
        self.patternWidget.canvas.cvImage = source.cvImage.copy()
        self.patternWidget.canvas.loadPixmap(pixmap)
        self.patternWidget.canvas.update()

    def show_image(self):
        if self.source == SOURCE_CAMERA:
            pixmap = self.cameraThread.get_pixmap()
        else:
            pixmap = self.video.get_pixmap()
        # print('mainwindow got an image')
        if not pixmap:
            return
        # 判断当前界面是哪个界面
        if self.stackWidget.currentWidget() == self.onlineWidget:
            pixmap = pixmap.scaled(self.onlineWidget.videoLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.onlineWidget.videoLabel.setPixmap(pixmap)
        elif self.stackWidget.currentWidget() == self.patternWidget:
            pixmap = pixmap.scaled(self.patternWidget.videoLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.patternWidget.videoLabel.setPixmap(pixmap)

    def mask_action(self, maskBool):
        # self.patternWidget.imageWidget.mask_action(maskBool)
        pass

    def camera_close_action(self, CameraBool):
        if self.cameraThread.isRunning():
            self.cameraThread.exit_thread()

    def camera_open_action(self, CameraBool):
        if not self.cameraThread.isRunning():
            self.cameraThread.start()
        self.source = SOURCE_CAMERA
    
    def pattern_select_action(self, path):
        # self.board.dir_path = path
        pass

    # 错误提示
    def error_messagebox(self, information):
        self.box = QMessageBox(QMessageBox.Warning, "警告框", information)
        self.box.addButton(self.tr("确定"), QMessageBox.YesRole)
        self.box.exec_()

    def closeEvent(self, event):
        self.cameraThread.exit_thread()
        self.cameraThread.wait(1000)
        self.cam.release()
        event.accept()


if __name__ == '__main__':
    # import subprocess
    # proc = subprocess.Popen(["pgrep", "-f", __file__], stdout=subprocess.PIPE)
    # std = proc.communicate()
    # if len(std[0].decode().split()) > 1:
    #     exit('Already running')

    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.showMaximized()
    sys.exit(app.exec_())