import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QMutex
from PyQt5.QtWidgets import QMessageBox

from board import Board
from online_widget import OnlineWidget
from pattern_widget import PatternWidget
from MvImport.MvCameraControl_class import *


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
        # 检测相机是否存在
        self.detection_camera()
        # 选择程式
        self.onlineWidget.PatternSelectAction.connect(self.pattern_select_action)
        # 开始检测
        # 停止检测
        # 打开相机
        self.onlineWidget.CameraOpenAction.connect(self.camera_open_action)
        # 关闭相机
        self.onlineWidget.CameraCloseAction.connect(self.camera_close_action)
        # 载入视频
        # 参数设置
        # 程式设计

        # 新建程式
        self.patternWidget.CreateAction.connect(self.choose_directory)
        # 保存程式
        # 打开程式
        # 抓取图像
        self.patternWidget.CaptureAction.connect(self.get_image)
        # 放大
        # 缩小
        # 选择
        # 移动
        # PCB 定位
        # Mask
        self.patternWidget.MaskAction.connect(self.mask_action)
        # 电解电容
        # 色环电阻
        # 插槽
        # 一般元件
    def choose_directory(self,path):
        self.board.dir_path = path

    def get_image(self, getBool):
        if self.board.cameraStatus:
            # 获取当前一帧图片并显示
            self.thread.ThreadQmut.lock()
            self.patternWidget.imageWidget.load_pixmap(self.thread.image_data.scaled(self.patternWidget.imageWidget.size(), QtCore.Qt.KeepAspectRatio))
            self.patternWidget.imageWidget.update()
            self.thread.ThreadQmut.unlock()
        else:
            self.error_message("相机未打开")

    def mask_action(self,maskBool):
        self.patternWidget.imageWidget.mask_action(maskBool)

    def camera_close_action(self,CameraBool):
        self.thread.stop()
        self.board.cameraStatus = False
    def camera_open_action(self, CameraBool):
        if self.board.cameraStatus:
            # 开启线程取流数据
            ret = self.exampleCamera.MV_CC_StartGrabbing()
            self.thread = Runthread(self.exampleCamera, self.bufCache, self.payloadSize,self.onlineWidget.videoLabel,self.patternWidget.videoLabel)  # 创建线程
            self.thread.start()  # 开始线程
        else:
            self.detection_camera()
            if self.board.cameraStatus:
                # 开启线程取流数据
                ret = self.exampleCamera.MV_CC_StartGrabbing()
                self.thread = Runthread(self.exampleCamera, self.bufCache, self.payloadSize,self.onlineWidget.videoLabel,self.patternWidget.videoLabel)  # 创建线程
                self.thread.start()  # 开始线程
    def pattern_select_action(self, path):
        self.board.dir_path = path

    def detection_camera(self):
        ''' 获取当前连接设备信息 '''
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        # GigE 设备 或者 USB 设备
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        # 枚举设备 | en:Enum device
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, self.deviceList)
        if ret != 0:
            self.error_message("枚举设备失败")
            return
        # 获取设备个数
        if self.deviceList.nDeviceNum != 1:
            self.error_message("未检测到相机设备，请检查")
            return

        # 获取相机设备信息
        mvcc_dev_info = cast(self.deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
        # 如果是 GigE 设备
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            # 获取当前设备名称
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                strModeName = strModeName + chr(per)
            # 获取当前设备 IP
            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
        # 如果是 USB 设备
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            # 获取当前设备名称
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            # 获取用户序列号
            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
        # 实例化相机
        self.exampleCamera = MvCamera()
        # 创建设备句柄
        ret = self.exampleCamera.MV_CC_CreateHandle(mvcc_dev_info)
        if ret != 0:
            # 销毁句柄
            self.exampleCamera.MV_CC_DestroyHandle()
            self.error_message("句柄销毁")
            return
        # 打开设备
        ret = self.exampleCamera.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            self.error_message("设备打开失败")
            return
        # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = self.exampleCamera.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.exampleCamera.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                if ret != 0:
                    self.error_message("设置数据包大小失败")
                    return
            else:
                self.error_message("获取网络最佳包大小失败")
                return
        # 获取采集数据帧率
        stBool = c_bool(False)
        ret = self.exampleCamera.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(stBool))
        if ret != 0:
            self.error_message("获取采集帧率启用失败")
            return
        # 获取有效载荷大小
        stParam = MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

        ret = self.exampleCamera.MV_CC_GetIntValue("PayloadSize", stParam)
        if ret != 0:
            self.error_message("获取有效载荷大小失败失败")
            return
        # 有效负载大小
        self.payloadSize = stParam.nCurValue
        self.bufCache = (c_ubyte * self.payloadSize)()

        # ch:设置触发模式为off | en:Set trigger mode as off
        ret = self.exampleCamera.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            self.error_message("设置触发模式失败")
            return
        self.board.cameraStatus = True
        return

    # 错误提示
    def error_message(self, information):
        self.box = QMessageBox(QMessageBox.Warning, "警告框", information)
        self.box.addButton(self.tr("确定"), QMessageBox.YesRole)
        self.box.exec_()

class Runthread(QtCore.QThread):
    """
    子线程采集数据
    """
    _signal = pyqtSignal(str)

    def __init__(self, exampleCamera, bufCache, payloadSize,onlineVideoLabel,patternVideoLabel):
        super(Runthread, self).__init__()

        self.exampleCamera = exampleCamera
        self.bufCache = bufCache
        self.payloadSize = payloadSize
        self.onlineVideoLabel = onlineVideoLabel
        self.patternVideoLabel = patternVideoLabel
        self.image_data = None
        # 创建线程锁
        self.ThreadQmut = QMutex()

    def get_pixmap(self):
        """  获取图片 setPixmap 格式  """
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        while True:
            ret = self.exampleCamera.MV_CC_GetOneFrameTimeout(byref(self.bufCache), self.payloadSize, stFrameInfo, 1000)
            if ret == 0:
                # 获取到图像的时间开始节点获取到图像的时间开始节点
                self.st_frame_info = stFrameInfo
                img_buff = (c_ubyte * (self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048))()
                stParam = MV_SAVE_IMAGE_PARAM_EX()
                stParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
                stParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
                stParam.nDataLen = self.st_frame_info.nFrameLen
                stParam.pData = cast(self.bufCache, POINTER(c_ubyte))

            else:
                continue

            # 转换像素结构体赋值
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = self.st_frame_info.nWidth
            stConvertParam.nHeight = self.st_frame_info.nHeight
            stConvertParam.pSrcData = self.bufCache
            stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
            stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType

            # Mono8直接显示
            if PixelType_Gvsp_Mono8 == self.st_frame_info.enPixelType:
                numArray = self.mono_numpy(self.bufCache, self.st_frame_info.nWidth, self.st_frame_info.nHeight)
            # RGB直接显示
            elif PixelType_Gvsp_RGB8_Packed == self.st_frame_info.enPixelType:

                numArray = self.color_numpy(self.bufCache, self.st_frame_info.nWidth,self.st_frame_info.nHeight)

            # 如果是黑白且非Mono8则转为Mono8
            elif True == self.is_mono_data(self.st_frame_info.enPixelType):

                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight
                stConvertParam.enDstPixelType = PixelType_Gvsp_Mono8
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                ret = self.exampleCamera.MV_CC_ConvertPixelType(stConvertParam)

                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = self.mono_numpy(img_buff, self.st_frame_info.nWidth,self.st_frame_info.nHeight)

            # 如果是彩色且非RGB则转为RGB后显示
            elif True == self.is_color_data(self.st_frame_info.enPixelType):
                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                ret = self.exampleCamera.MV_CC_ConvertPixelType(stConvertParam)

                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = self.color_numpy(img_buff,self.st_frame_info.nWidth,self.st_frame_info.nHeight)

            image = QtGui.QImage(numArray[:], numArray.shape[1], numArray.shape[0], numArray.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)
            self.ThreadQmut.lock()
            self.image_data = QtGui.QPixmap.fromImage(image)
            self.ThreadQmut.unlock()
            self.QPixmapImage = self.image_data.scaled(self.onlineVideoLabel.size(), QtCore.Qt.KeepAspectRatio)

            self.onlineVideoLabel.setPixmap(self.QPixmapImage)
            self.patternVideoLabel.setPixmap(self.QPixmapImage)
    def is_mono_data(self, enGvspPixelType):
        # 判断数据像素格式
        if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
                or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
                or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
            return True
        else:
            return False

    def is_color_data(self, enGvspPixelType):
        # 判断数据像素格式
        if PixelType_Gvsp_BayerGR8 == enGvspPixelType or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
                or PixelType_Gvsp_BayerGB8 == enGvspPixelType or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
                or PixelType_Gvsp_BayerGR10 == enGvspPixelType or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
                or PixelType_Gvsp_BayerGB10 == enGvspPixelType or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
                or PixelType_Gvsp_BayerGR12 == enGvspPixelType or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
                or PixelType_Gvsp_BayerGB12 == enGvspPixelType or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
                or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG12_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
                or PixelType_Gvsp_YUV422_Packed == enGvspPixelType or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:
            return True
        else:
            return False

    def mono_numpy(self, data, nWidth, nHeight):
        data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
        data_mono_arr = data_.reshape(nHeight, nWidth)
        num_array = np.zeros([nHeight, nWidth, 1], "uint8")
        num_array[:, :, 0] = data_mono_arr
        return num_array

    def color_numpy(self, data, nWidth, nHeight):
        data_ = np.frombuffer(data, count=int(nWidth * nHeight * 3), dtype=np.uint8, offset=0)
        data_r = data_[0:nWidth * nHeight * 3:3]
        data_g = data_[1:nWidth * nHeight * 3:3]
        data_b = data_[2:nWidth * nHeight * 3:3]

        data_r_arr = data_r.reshape(nHeight, nWidth)
        data_g_arr = data_g.reshape(nHeight, nWidth)
        data_b_arr = data_b.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 3], "uint8")

        numArray[:, :, 2] = data_r_arr
        numArray[:, :, 1] = data_g_arr
        numArray[:, :, 0] = data_b_arr
        return numArray

    def run(self):
        self.get_pixmap()
        print("执行")
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