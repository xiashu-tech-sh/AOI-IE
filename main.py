import os
import sys

from camera import VideoSource

sys.path.append('./MvImport')
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from board import Board
from online_widget import OnlineWidget
from pattern_widget import PatternWidget
from MvImport.MvCameraControl_class import *
import cv2
import torch
SOURCE_CAMERA = 0
SOURCE_VIDEO = 1
from ModelLoad import model_add
import logging.config

logging.config.fileConfig('logs/logging.conf')
logger = logging.getLogger('main')

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

        self.Timer = QTimer()
        self.Timer.timeout.connect(self.camera_configuration)

        # 打开相机
        self.onlineWidget.cameraOpenAction.triggered.connect(lambda: self.Timer.start(100))
        # 相机状态
        self.CameraStatus = False
        self.payloadSize = None
        self.bufCache = None
        # self.detection_camera()
        # 关闭相机
        self.onlineWidget.cameraCloseAction.triggered.connect(self.camera_close_action)
        # 载入视频
        self.source = SOURCE_CAMERA
        self.onlineWidget.videoAction.triggered.connect(self.set_video_source)

        # 抓取图像
        self.patternWidget.captureAction.triggered.connect(self.load_image_to_canvas)
        # 开始检测
        self.onlineWidget.startAction.triggered.connect(self.run_detect)
        self.onlineWidget.stopAction.triggered.connect(self.stop_detect)
        self.isRunning = False
        self.cuda = torch.cuda.is_available()
        self.num_array = None
    def stop_detect(self):
        self.isRunning = False
    def run_detect(self):
        if self.onlineWidget.pattern is None:
            return
        if self.CameraStatus:
            self.isRunning = True
        # 模型加载
        self.onlineWidget.component_thread.model = model_add(self.cuda)
    def close_camera_view(self):
        self.Timer.stop()
        self.error_message("相机已关闭")
        self.obtain_camera = False
        self.exampleCamera.MV_CC_StopGrabbing()
    def detection_camera(self):
        ''' 获取当前连接设备信息 '''
        device_list = MV_CC_DEVICE_INFO_LIST()
        # GigE 设备 或者 USB 设备
        equipment_type = MV_GIGE_DEVICE | MV_USB_DEVICE
        # 枚举设备 | en:Enum device
        ret = MvCamera.MV_CC_EnumDevices(equipment_type, device_list)
        if ret != 0:
            self.error_message("枚举设备失败")
            self.Timer.stop()
            return
        # 获取设备个数
        if device_list.nDeviceNum != 1:
            self.error_message("未检测到相机设备，请检查")
            self.Timer.stop()
            return
        # 获取相机设备信息
        mvcc_dev_info = cast(device_list.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
        # 如果是 GigE 设备
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            # 获取当前设备名称
            str_mode_name = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                str_mode_name = str_mode_name + chr(per)
            # 获取当前设备 IP
            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
        # 如果是 USB 设备
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            # 获取当前设备名称
            str_mode_name = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                str_mode_name = str_mode_name + chr(per)
            # 获取用户序列号
            str_serial_number = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                str_serial_number = str_serial_number + chr(per)
        # 实例化相机
        self.exampleCamera = MvCamera()
        logger.debug('初始化相机成功')
        # 创建设备句柄
        ret = self.exampleCamera.MV_CC_CreateHandle(mvcc_dev_info)
        if ret != 0:
            # 销毁句柄
            self.exampleCamera.MV_CC_DestroyHandle()
            self.error_message("句柄销毁")
            self.Timer.stop()
            return
        # 打开设备
        ret = self.exampleCamera.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            self.error_message("设备打开失败")
            self.Timer.stop()
            return
        # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            packet_size = self.exampleCamera.MV_CC_GetOptimalPacketSize()
            if int(packet_size) > 0:
                ret = self.exampleCamera.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
                if ret != 0:
                    self.error_message("设置数据包大小失败")
                    self.Timer.stop()
                    return
            else:
                self.error_message("获取网络最佳包大小失败")
                self.Timer.stop()
                return
        # 获取采集数据帧率
        st_bool = c_bool(False)
        ret = self.exampleCamera.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(st_bool))
        if ret != 0:
            self.error_message("获取采集帧率启用失败")
            self.Timer.stop()
            return
        # 修改采集帧率
        ret = self.exampleCamera.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", 30)
        # 获取有效载荷大小
        st_param = MVCC_INTVALUE()
        memset(byref(st_param), 0, sizeof(MVCC_INTVALUE))

        ret = self.exampleCamera.MV_CC_GetIntValue("PayloadSize", st_param)
        if ret != 0:
            self.error_message("获取有效载荷大小失败失败")
            self.Timer.stop()
            return
        # 有效负载大小
        self.payloadSize = st_param.nCurValue
        self.bufCache = (c_ubyte * self.payloadSize)()
        # 设置曝光
        ret = self.exampleCamera.MV_CC_SetFloatValue("ExposureTime", 3000.00)
        # ch:设置触发模式为off | en:Set trigger mode as off
        ret = self.exampleCamera.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            self.error_message("设置触发模式失败")
            self.Timer.stop()
            return
        self.CameraStatus = True
        # self.Timer.start(100)
        return
    def camera_configuration(self):
        if self.CameraStatus is False:
            self.detection_camera()
            if self.CameraStatus is False:
                return
        self.obtain_camera = True
        """  获取图片 setPixmap 格式  """
        st_frame_info = MV_FRAME_OUT_INFO_EX()
        st_frame_info.fExposureTime = 2.0
        ret = self.exampleCamera.MV_CC_GetOneFrameTimeout(byref(self.bufCache), self.payloadSize, st_frame_info, 1000)
        if ret == 0:
            # 获取到图像的时间开始节点获取到图像的时间开始节点
            self.st_frame_info = st_frame_info
            img_buff = (c_ubyte * (self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048))()
            stParam = MV_SAVE_IMAGE_PARAM_EX()
            stParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
            stParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
            stParam.nDataLen = self.st_frame_info.nFrameLen

            stParam.pData = cast(self.bufCache, POINTER(c_ubyte))

        else:
            ret = self.exampleCamera.MV_CC_StartGrabbing()
            return

        # 转换像素结构体赋值
        stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
        memset(byref(stConvertParam), 0, sizeof(stConvertParam))
        stConvertParam.nWidth = self.st_frame_info.nWidth
        stConvertParam.nHeight = self.st_frame_info.nHeight
        stConvertParam.pSrcData = self.bufCache
        stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
        stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType

        nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
        stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
        stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
        stConvertParam.nDstBufferSize = nConvertSize
        ret = self.exampleCamera.MV_CC_ConvertPixelType(stConvertParam)
        cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
        self.num_array = self.Color_numpy(img_buff, self.st_frame_info.nWidth, self.st_frame_info.nHeight)
        num_array = cv2.cvtColor(self.num_array, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(num_array[:], num_array.shape[1], num_array.shape[0], num_array.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        self.image_qtdata = QtGui.QPixmap.fromImage(image)
        online_image = self.image_qtdata.scaled(self.onlineWidget.videoLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.onlineWidget.videoLabel.setPixmap(online_image)
        patter_image = self.image_qtdata.scaled(self.patternWidget.videoLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.patternWidget.videoLabel.setPixmap(patter_image)
        if self.isRunning:
            self.onlineWidget.match_template(self.num_array)
            # self.isRunning = False

    def Color_numpy(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=int(nWidth*nHeight*3), dtype=np.uint8, offset=0)
        data_r = data_[0:nWidth*nHeight*3:3]
        data_g = data_[1:nWidth*nHeight*3:3]
        data_b = data_[2:nWidth*nHeight*3:3]

        data_r_arr = data_r.reshape(nHeight, nWidth)
        data_g_arr = data_g.reshape(nHeight, nWidth)
        data_b_arr = data_b.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 3],"uint8")

        numArray[:, :, 2] = data_r_arr
        numArray[:, :, 1] = data_g_arr
        numArray[:, :, 0] = data_b_arr
        return numArray

    def set_video_source(self):
        # filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, '本地视频文件', '')
        # filename = '../JT/test.mp4'
        filename = './p/Video_20200722114533302.avi'
        if not filename or not os.path.exists(filename):
            return
        self.video = VideoSource(filename)
        self.video.newImageSignal.connect(self.show_image)
        self.source = SOURCE_VIDEO

    def load_image_to_canvas(self):
        ''' 点击[抓取图像]按钮后触发抓图，并显示 '''
        # if self.source == SOURCE_CAMERA:
        #     source = self.cameraThread
        # else:
        #     source = self.video
        # if self.CameraStatus is False:
        #     return
        # if self.num_array is None:
        #     return
        # pixmap = source.get_pixmap()
        # if not pixmap:
        #     return

        self.patternWidget.canvas.cvImage = self.num_array
        self.patternWidget.canvas.loadPixmap(self.image_qtdata)
        self.patternWidget.canvas.update()

    def show_image(self):
        if self.source == SOURCE_CAMERA:
            pixmap = self.cameraThread.get_pixmap()
        else:
            pixmap = self.video.get_pixmap()
        if not pixmap:
            return
        # 判断当前界面是哪个界面
        if self.stackWidget.currentWidget() == self.onlineWidget:
            pixmap = pixmap.scaled(self.onlineWidget.videoLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.onlineWidget.videoLabel.setPixmap(pixmap)
        elif self.stackWidget.currentWidget() == self.patternWidget:
            pixmap = pixmap.scaled(self.patternWidget.videoLabel.size(), QtCore.Qt.KeepAspectRatio)
            self.patternWidget.videoLabel.setPixmap(pixmap)

        # # 判断是否在线检测
        # if self.onlineWidget.isRunning:
        #     if self.source == SOURCE_CAMERA:
        #         cvImage = self.cameraThread.get_cvimage()
        #     else:
        cvImage = self.video.get_cvimage()
        self.onlineWidget.match_template(cvImage)

    def camera_close_action(self, CameraBool):
        self.Timer.stop()
        self.error_message("相机已关闭")
        self.exampleCamera.MV_CC_StopGrabbing()

    def camera_open_action(self, CameraBool):
        if not self.cameraThread.isRunning():
            self.cameraThread.start()
        self.source = SOURCE_CAMERA
    
    def pattern_select_action(self, path):
        # self.board.dir_path = path
        pass

    # 错误提示
    def error_message(self, information):
        self.box = QMessageBox(QMessageBox.Warning, "警告框", information)
        self.box.addButton(self.tr("确定"), QMessageBox.YesRole)
        self.box.exec_()

    def closeEvent(self, event):
        # if self.patternWidget.pattern and self.patternWidget.pattern.dirty:
        #     QtWidgets.QMessageBox.warning(self, '警告', '程式未保存，确定要退出吗？')
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