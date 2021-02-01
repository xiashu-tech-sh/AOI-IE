import datetime
import time
import cv2
import os
import numpy as np
import serial
from PyQt5.QtWidgets import (QMainWindow, qApp,
                             QApplication, QToolButton,
                             QLabel, QFileDialog, QComboBox, QVBoxLayout, QDialog, QHBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import QTimer, pyqtSignal, QSettings
from qtpy import QtGui, QtCore
from main_ui import Ui_MainWindow
from MvImport.MvCameraControl_class import *
import tensorflow as tf
import location_api as api
import classes_api


class Detector:
    def __init__(self, location_file='', classes_file='', location_inputsize=200, classes_inputsize=256,
                 use_cuda=False):
        self.location_file = location_file
        self.classes_file = classes_file
        self.location_inputsize = location_inputsize
        self.classes_inputsize = classes_inputsize
        self.use_cuda = use_cuda
        if location_file:
            self.load_location_model(location_file)
        if classes_file:
            self.load_classes_model(classes_file)

    def load_location_model(self, location_file):
        self.location_file = location_file
        self.location_model = api.load_model(self.location_file, self.use_cuda)

    def load_classes_model(self, classes_file):
        self.classes_file = classes_file
        self.classes_model = classes_api.load_model(self.classes_file, self.use_cuda)

    def inference(self, cvImage):
        x, y, z = api.inference(self.location_model, cvImage, self.location_inputsize, self.use_cuda)
        cutImage = api.cut_image_by_circle(cvImage, x, y, z)
        return classes_api.inference(self.classes_model, cutImage, self.classes_inputsize, self.use_cuda)


class Identification(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Identification, self).__init__()
        self.setupUi(self)
        self.previewLabel.setScaledContents(False)
        self.captureLabel.setScaledContents(False)
        # 图片过鉴定模型线程
        self.model_thread = ModelThread()
        self.model_thread.model_signal.connect(self.intercept)
        self.model_thread.start()
        # 模型
        self.model = None
        self.location_model_path = '../model/D20200827.pth'
        self.classes_model_path = '../model/0918.pth'
        self.location_inputsize = 200
        self.classes_inputsize = 256
        self.theshold = 0.5
        self.use_cuda = False
        # 读取配置文件
        self.settings = QSettings("HKEY_CURRENT_USER\\Software\\lm", QSettings.NativeFormat)
        self.set_open_file()
        self.Timer = QTimer()
        self.Timer.timeout.connect(self.camera_configuration)
        # 串口通信
        self.ser = None
        # 连接单片机
        # self.connect_mac()
        # 相机状态，模型
        self.CameraStatus = False
        self.payloadSize = None
        self.bufCache = None
        # 检测相机是否存在
        self.detection_camera()
        # 获取当前日期
        self.now_time = datetime.datetime.now().strftime('%Y-%m-%d')

        # 记录采集总数，公鸡，母鸡数量
        self.CollectionTotal = 0
        self.CollectionHend = 0
        self.CollectionCock = 0

        # 记录鉴定总数，公鸡，母鸡数量
        self.IdentifyTotal = 0
        self.IdentifyHend = 0
        self.IdentifyCock = 0

        # 记录验证总数，公鸡，母鸡数量
        self.VerifiTotal = 0
        self.VerifiHend = 0
        self.VerifiCock = 0

        # 截取图片数据
        self.img_num = None
        self.features()

        # 定义单片机变量，防止回收
        self.machine_thread = None
        self.child_window = None

        self.obtain_camera = False
        # 初始化选中状态
        self.offlineAction.setChecked(True)

    def set_open_file(self):
        # 获取模型路径
        self.model = self.settings.value("model")
        if self.model:
            try:
                self.modelLineEdit_2.setText(self.model)
                self.VModelPath.setText(self.model)
                self.model_thread.model = Detector(location_file=self.location_model_path, classes_file=self.model,
                                                   location_inputsize=self.location_inputsize,
                                                   classes_inputsize=self.classes_inputsize, use_cuda=self.use_cuda)
            except:
                self.error_message("模型加载失败")
                return
        # 获取公鸡阈值
        cocktvalue = self.settings.value("cocktvalue")  # 读取指定键所对应的值
        if cocktvalue:
            self.IPCThreshold.setText(cocktvalue)
        # 获取母鸡阈值
        hentvalue = self.settings.value("hentvalue")  # 读取指定键所对应的值
        if hentvalue:
            self.IPHThreshold.setText(hentvalue)
        # 获取人工通道阈值
        peoplevalue = self.settings.value("peoplevalue")
        if peoplevalue:
            self.maleLineEdit_2.setText(peoplevalue)

    def connect_mac(self):
        portx = "COM6"
        bps = 9600
        timex = 0.05
        # 打开串口，并得到串口对象
        self.ser = serial.Serial(portx, bps, timeout=timex)
        self.machine_thread = MachineThread(self.ser)
        # result = self.ser.write("O(00,03,1)E".encode("gbk"))
        # result = self.ser.write("O(00,04,1)E".encode("gbk"))

        self.machine_thread.start()
        self.machine_thread.machine_signal.connect(self.thread_sig)

    def thread_sig(self, signal):
        if not signal:
            return
        if self.obtain_camera is False:
            self.error_message("请打开相机")
            return
        st_frame_info = MV_FRAME_OUT_INFO_EX()

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
            return

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
            num_array = self.mono_numpy(self.bufCache, self.st_frame_info.nWidth, self.st_frame_info.nHeight)
            self.img_num = cv2.cvtColor(num_array, cv2.COLOR_GRAY2BGR)

        image = QtGui.QImage(self.img_num[:], self.img_num.shape[1], self.img_num.shape[0], self.img_num.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        image_data = QtGui.QPixmap.fromImage(image)

        scree_image = image_data.scaled(self.captureLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.captureLabel.setPixmap(scree_image)
        # self.update()
        self.model_thread.image_array = self.img_num
        # 采集模式
        if self.AuthenticationMode.currentIndex() == 0:
            self.intercept(None)
        # 鉴定模式
        elif self.AuthenticationMode.currentIndex() == 1:
            if len(self.modelLineEdit_2.text()) ==  0:
                self.error_message("请选择模型")
            self.model_thread.add_task_()
        else:
            if len(self.modelLineEdit_2.text()) == 0:
                self.error_message("请选择模型")
                return
            self.model_thread.add_task_()

    def open_close(self):
        if self.OpenCloss.text() == "关闭":
            self.OpenCloss.setText("打开")
            self.OpenCloss.setStyleSheet("background-color:rgb(0, 255, 0);")
            # 高亮
            self.maleLineEdit_2.setEnabled(True)
            # 可编辑
            self.maleLineEdit_2.setReadOnly(False)
            self.IPCThreshold.setEnabled(False)
            self.IPCThreshold.setReadOnly(True)
            self.IPHThreshold.setEnabled(False)
            self.IPHThreshold.setReadOnly(True)
        else:
            self.OpenCloss.setText("关闭")
            self.OpenCloss.setStyleSheet("background-color:rgb(255, 0, 0);")
            # 高亮
            self.maleLineEdit_2.setEnabled(False)
            # 可编辑
            self.maleLineEdit_2.setReadOnly(True)
            self.IPCThreshold.setEnabled(True)
            self.IPCThreshold.setReadOnly(False)
            self.IPHThreshold.setEnabled(True)
            self.IPHThreshold.setReadOnly(False)

    def detection_camera(self):
        ''' 获取当前连接设备信息 '''
        device_list = MV_CC_DEVICE_INFO_LIST()
        # GigE 设备 或者 USB 设备
        equipment_type = MV_GIGE_DEVICE | MV_USB_DEVICE
        # 枚举设备 | en:Enum device
        ret = MvCamera.MV_CC_EnumDevices(equipment_type, device_list)
        if ret != 0:
            self.error_message("枚举设备失败")
            return
        # 获取设备个数
        if device_list.nDeviceNum != 1:
            self.error_message("未检测到相机设备，请检查")
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
            packet_size = self.exampleCamera.MV_CC_GetOptimalPacketSize()
            if int(packet_size) > 0:
                ret = self.exampleCamera.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
                if ret != 0:
                    self.error_message("设置数据包大小失败")
                    return
            else:
                self.error_message("获取网络最佳包大小失败")
                return
        # 获取采集数据帧率
        st_bool = c_bool(False)
        ret = self.exampleCamera.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(st_bool))
        if ret != 0:
            self.error_message("获取采集帧率启用失败")
            return
        # 修改采集帧率
        ret = self.exampleCamera.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", 30)
        # 获取有效载荷大小
        st_param = MVCC_INTVALUE()
        memset(byref(st_param), 0, sizeof(MVCC_INTVALUE))

        ret = self.exampleCamera.MV_CC_GetIntValue("PayloadSize", st_param)
        if ret != 0:
            self.error_message("获取有效载荷大小失败失败")
            return
        # 有效负载大小
        self.payloadSize = st_param.nCurValue
        self.bufCache = (c_ubyte * self.payloadSize)()
        # 设置曝光
        ret = self.exampleCamera.MV_CC_SetFloatValue("ExposureTime", 5000.00)
        # ch:设置触发模式为off | en:Set trigger mode as off
        ret = self.exampleCamera.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            self.error_message("设置触发模式失败")
            return
        self.CameraStatus = True
        self.Timer.start(100)
        return

    def error_message(self, information):
        # 错误提示
        box = QMessageBox(QMessageBox.Warning, "警告框", information)
        box.addButton(self.tr("确定"), QMessageBox.YesRole)
        box.exec_()

    def features(self):
        # 打开相机
        self.cameraOpenAction.triggered.connect(lambda: self.Timer.start(100))
        # 选择模型
        self.modelAction.triggered.connect(self.open_file)
        # 关闭相机
        self.cameraCloseAction.triggered.connect(self.close_camera_view)
        # 采集模式， 高量配置，参数配置
        self.offlineAction.triggered.connect(self.acquisition_mode_plot)
        self.offlineAction.triggered.connect(self.window_connection)
        # 初始化显示采集性别
        self.CollectText.setText(self.CGenderValue.currentText())
        # # 处理人工打开关闭按钮
        self.OpenCloss.clicked.connect(self.open_close)
        # # 鉴定模式， 高量配置，参数配置
        self.onlineAction.triggered.connect(self.identification_mode_plot)
        #
        # Tab框控制菜单栏高量
        self.AuthenticationMode.currentChanged['int'].connect(self.tabfun)
        # # 退出程序
        self.exitProgram.triggered.connect(self.quit_cam)
        self.exitProgram.triggered.connect(qApp.quit)
        # # 修改颜色gb 文本显示内容
        self.CGenderValue.currentIndexChanged.connect(lambda: self.color(self.CGenderValue.currentIndex()))
        # # 关机
        self.closeComputer.triggered.connect(self.close_computer)

    def gender_test(self):
        self.TotalValues_3.setText(self.GenderValue.currentText())

    def quit_cam(self):
        try:
            self.Timer.stop()
        except:
            pass
        try:
            self.exampleCamera.MV_CC_StopGrabbing()
        except:
            pass
        try:
            self.model_thread.stop()
        except:
            pass

    def close_computer(self):
        self.thread_sig("1")


        # try:
        #     self.Timer.stop()
        # except:
        #     pass
        # try:
        #     self.exampleCamera.MV_CC_StopGrabbing()
        # except:
        #     pass
        # try:
        #     self.model_thread.stop()
        # except:
        #     pass
        # os.system("shutdown -s -t 2")

    def tabfun(self, index):
        if index == 0:
            # self.TotalValues_2.setText("")
            # self.TotalValues_3.setText(self.GenderValue.currentText())
            self.onlineAction.setCheckable(True)
            self.onlineAction.setChecked(False)  # 初始化时设置为选中或者不选择
            self.offlineAction.setCheckable(True)
            self.offlineAction.setChecked(True)  # 初始化时设置为选中或者不选择
            # result = self.ser.write("O(00,02,0)E".encode("gbk"))
            # result = self.ser.write("O(00,01,0)E".encode("gbk"))

        elif index == 1:
            # self.captureLabel.setPixmap(QPixmap(""))
            self.onlineAction.setCheckable(True)
            self.onlineAction.setChecked(True)  # 初始化时设置为选中或者不选择
            self.offlineAction.setCheckable(True)
            self.offlineAction.setChecked(False)  # 初始化时设置为选中或者不选择
        else:
            # self.captureLabel.setPixmap(QPixmap(""))
            # self.TotalValues_2.setText("")
            # self.TotalValues_3.setText(self.GenderValue.currentText())
            self.onlineAction.setCheckable(True)
            self.onlineAction.setChecked(False)  # 初始化时设置为选中或者不选择
            self.offlineAction.setCheckable(True)
            self.offlineAction.setChecked(False)  # 初始化时设置为选中或者不选择
            # result = self.ser.write("O(00,02,0)E".encode("gbk"))
            # result = self.ser.write("O(00,01,0)E".encode("gbk"))

    def color(self, index):
        if index == 1:
            self.CGenderValue.setStyleSheet("background-color: rgb(0,255,255);")
        if index == 0:
            self.CGenderValue.setStyleSheet("background-color: rgb(255,85,255);")
        self.CollectText.setText(self.CGenderValue.currentText())

    def identification_mode_plot(self):
        # self.TotalValues_3.setText(self.GenderValue.currentText())
        self.onlineAction.setCheckable(True)
        self.onlineAction.setChecked(True)  # 初始化时设置为选中或者不选择
        self.offlineAction.setCheckable(True)
        self.offlineAction.setChecked(False)  # 初始化时设置为选中或者不选择
        self.AuthenticationMode.setCurrentIndex(1)

    def acquisition_mode_plot(self):
        # result = self.ser.write("O(00,02,0)E".encode("gbk"))
        # result = self.ser.write("O(00,01,0)E".encode("gbk"))
        self.onlineAction.setCheckable(True)
        self.onlineAction.setChecked(False)  # 初始化时设置为选中或者不选择
        self.offlineAction.setCheckable(True)
        self.offlineAction.setChecked(True)  # 初始化时设置为选中或者不选择
        self.AuthenticationMode.setCurrentIndex(0)

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
        # Mono8直接显示
        if PixelType_Gvsp_Mono8 == self.st_frame_info.enPixelType:
            num_array = self.mono_numpy(self.bufCache, self.st_frame_info.nWidth, self.st_frame_info.nHeight)
            num_array = cv2.cvtColor(num_array, cv2.COLOR_GRAY2BGR)

        image = QtGui.QImage(num_array[:], num_array.shape[1], num_array.shape[0], num_array.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        image_qtdata = QtGui.QPixmap.fromImage(image)

        self.QPixmapImage = image_qtdata.scaled(self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(self.QPixmapImage)

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
        num_array = np.zeros([nHeight, nWidth, 3], "uint8")

        num_array[:, :, 2] = data_r_arr
        num_array[:, :, 1] = data_g_arr
        num_array[:, :, 0] = data_b_arr
        return num_array

    def intercept(self, pred_val):
        # conde = self.tabWidget.tabText(self.tabWidget.currentIndex())
        if self.CameraStatus is False:
            self.error_message("请打开相机设备")
            return
        # 采集模式
        if self.AuthenticationMode.currentIndex() == 0:
            PathFile = self.image_save(0,self.CGenderValue.currentText())
            num_ = time.strftime("%H%M%S", time.localtime(time.time()))
            if self.CGenderValue.currentIndex() == 0:
                # 公鸡数量
                self.CollectionCock += 1
                self.CCockValue.setText(str(self.CollectionCock))
            else:
                # 母鸡数量
                self.CollectionHend += 1
                self.femaleLineEdit_3.setText(str(self.CollectionHend))
            self.CollectionTotal+=1
            self.CTotalValue.setText(str(self.CollectionTotal))
            # 根据日期，模式，种类，性别存放图片
            cv2.imencode('.jpg', self.img_num)[1].tofile(
                PathFile + '/%s_%s.jpg' % (self.now_time, str(num_)))
        # 鉴定模式
        elif self.AuthenticationMode.currentIndex() == 1:
            # self.TotalValues_3.setText("")
            self.settings.setValue("cocktvalue", self.IPCThreshold.text())
            self.settings.setValue("hentvalue", self.IPHThreshold.text())
            self.settings.setValue("peoplevalue", self.maleLineEdit_2.text())

            if len(self.modelLineEdit_2.text()) == 0:
                self.error_message("请选择模型")
                return

            if self.OpenCloss.text() == "关闭":
                # 公鸡数量
                if pred_val >= float(self.IPCThreshold.text()):
                    self.IdentifyCock += 1
                    self.ICockValue.setText(str(self.IdentifyCock))
                    # self.GenderValue.setCurrentIndex(0)
                    self.IdentificationValue.setText("公")
                    # result = self.ser.write("O(00,02,0)E".encode("gbk"))
                    self.light(1)

                # 母鸡数量
                else:
                    self.IdentifyHend += 1
                    self.CTotalValue_4.setText(str(self.IdentifyHend))
                    # self.GenderValue.setCurrentIndex(1)
                    self.IdentificationValue.setText("母")
                    # result = self.ser.write("O(00,01,0)E".encode("gbk"))
                    self.light(2)
                self.IdentifyTotal+=1
                self.ITotalValue.setText(str(self.IdentifyTotal))
            else:
                # 公鸡数量
                if pred_val >= float(self.maleLineEdit_2.text()):
                    self.IdentifyCock += 1
                    self.ICockValue.setText(str(self.IdentifyCock))
                    # self.GenderValue.setCurrentIndex(0)
                    self.IdentificationValue.setText("公")
                    # result = self.ser.write("O(00,02,0)E".encode("gbk"))
                    self.light(1)
                # 母鸡数量
                else:
                    self.IdentifyHend += 1
                    self.CTotalValue_4.setText(str(self.IdentifyHend))
                    # self.GenderValue.setCurrentIndex(1)
                    self.IdentificationValue.setText("母")
                    # result = self.ser.write("O(00,01,0)E".encode("gbk"))
                    self.light(2)
                self.IdentifyTotal+=1
                self.ITotalValue.setText(str(self.IdentifyTotal))
            path_file = self.image_save(1, self.IdentificationValue.text())
            num_ = time.strftime("%H%M%S", time.localtime(time.time()))
            cv2.imencode('.jpg', self.img_num)[1].tofile(
                path_file + '/%s_%s.jpg' % (self.now_time, str(num_)))
        # 验证模式
        elif self.AuthenticationMode.currentIndex() == 2:

            if len(self.VModelPath.text()) == 0:
                self.error_message("请选择模型")
                return
            if self.VGenderValue.currentIndex() == 0:
                gender ="cock"
            else:
                gender = "hen"
            # 公鸡数量
            if pred_val >= float(self.VThreshold_1.text()):
                self.VerifiCock += 1
                self.VTotalValue.setText(str(self.VerifiCock))
                # self.GenderValue.setCurrentIndex(0)
                self.VIResultText.setText("公")
                # result = self.ser.write("O(00,02,0)E".encode("gbk"))
                self.light(1)

            # 母鸡数量
            else:
                self.VerifiHend += 1
                self.VTotalValue_2.setText(str(self.VerifiHend))
                # self.GenderValue.setCurrentIndex(1)
                self.VIResultText.setText("母")
                # result = self.ser.write("O(00,01,0)E".encode("gbk"))
                self.light(2)
            self.VerifiTotal += 1
            self.VTotalNum.setText(str(self.VerifiTotal))
            V_path = self.image_save(2, self.VIResultText.text())
            num_ = time.strftime("%H%M%S", time.localtime(time.time()))
            cv2.imencode('.jpg', self.img_num)[1].tofile(
                V_path + '/%s_%s_%s.jpg' % (self.now_time, str(num_),gender))

    def light(self, value):
        result = self.ser.write(("O(00,0%s,0)E" % value).encode("gbk"))
        time.sleep(0.1)
        result = self.ser.write(("O(00,0%s,1)E" % value).encode("gbk"))

    def open_file(self):
        model = QFileDialog.getOpenFileName(self, '选择文件', '', '*.pth')
        if len(model[0]) != 0:
            try:
                self.settings.setValue("model", model[0])
                self.modelLineEdit_2.setText(model[0])
                self.VModelPath.setText(model[0])

                self.model_thread.model = Detector(self.location_model_path, self.classes_model_path,
                                                   location_inputsize=self.location_inputsize,
                                                   classes_inputsize=self.classes_inputsize, use_cuda=self.use_cuda)
            except:
                self.error_message("模型加载失败")
                return

    # 连接子窗口
    def window_connection(self):
        # 实例化子窗口
        self.child_window = CollectionConfiguration(self)
        # 父窗口直接赋值子窗口
        list_kind = [self.CChickenValue.itemText(i) for i in range(self.CChickenValue.count())]
        list_gender = [self.CGenderValue.itemText(i) for i in range(self.CGenderValue.count())]
        self.child_window.Category.addItems(list_kind)
        self.child_window.Gender.addItems(list_gender)
        # 连接子窗口自定义消息和主窗口槽函数
        self.child_window.dialogSignel.connect(self.slot_emit)
        self.child_window.exec_()

    def slot_emit(self, flag, st_list):
        if flag == 0:  # 点击确定
            self.CChickenValue.setCurrentIndex(st_list[0])
            self.CGenderValue.setCurrentIndex(st_list[1])
            if st_list[1] == 1:
                self.CGenderValue.setStyleSheet("background-color: rgb(0,255,255);")
            elif st_list[1] == 0:
                self.CGenderValue.setStyleSheet("background-color: rgb(255,85,255);")
        else:  # 点击取消
            pass

    def close_camera_view(self):
        self.Timer.stop()
        self.error_message("相机已关闭")
        self.obtain_camera = False
        self.exampleCamera.MV_CC_StopGrabbing()

    # def OpenModelFilePlot(self):
    #     self.OpenModelFile.setCheckable(False)
    #     self.OpenModelFile.setChecked(True)  # 初始化时设置为选中或者不选择
    #
    # def ModelTwoPlot(self):
    #     self.ModelTwo.setCheckable(False)
    #     self.ModelTwo.setChecked(True)  # 初始化时设置为选中或者不选择
    #
    # def OpenCameraPlot(self):
    #     self.OpenCamera.setCheckable(True)
    #     self.OpenCamera.setChecked(True)  # 初始化时设置为选中或者不选择
    #
    # def CloseCameraPlot(self):
    #     self.CloseCamera.setCheckable(False)
    #     self.CloseCamera.setChecked(True)  # 初始化时设置为选中或者不选择
    #     self.OpenCamera.setChecked(False)

    # 创建文件夹
    def image_save(self, value, gender):
        # 创建日期文件夹
        filestr = ''
        file_name_list = ["D:/data" + '/' + self.AuthenticationMode.tabText(value), self.now_time, self.CChickenValue.currentText(),
                          gender]
        for name in file_name_list:
            filestr += name + "/"
            if not os.path.exists(filestr):
                os.makedirs(filestr)
        return filestr


class MachineThread(QtCore.QThread):
    """ 开启线程获取单片机信号 """
    machine_signal = pyqtSignal(str)

    def __init__(self, ser):
        super(MachineThread, self).__init__()
        self.sere = ser

    def run(self):
        while True:
            str_ser = self.sere.readline().decode("gbk")
            if len(str_ser):
                if str_ser[7] == "1":
                    time.sleep(0.2)
                    self.machine_signal.emit("1")

                    time.sleep(0.8)


# 采集模式配置框
class CollectionConfiguration(QDialog, Ui_MainWindow):
    # 自定义消息
    dialogSignel = pyqtSignal(int, list)

    def __init__(self, parent=None):
        super(CollectionConfiguration, self).__init__(parent)
        # 获取下拉框所有选项
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        wlayout = QVBoxLayout()

        layout = QVBoxLayout(self)
        self.resize(381, 297)
        self.label = QLabel(self)
        self.setWindowTitle("采集配置")
        self.Category = QComboBox()
        self.Category.setFont(font)

        self.Category.setObjectName("patternComboBox")
        self.label.setText("请选择小鸡鸡种：")
        self.label.setFont(font)

        layout.addWidget(self.label)
        layout.addWidget(self.Category)

        self.label1 = QLabel(self)
        self.label1.setText("请选择小鸡性别：")
        self.label1.setFont(font)

        self.Gender = QComboBox()
        self.Gender.setFont(font)

        layout.addWidget(self.label1)
        layout.addWidget(self.Gender)

        ConfirmButtons = QToolButton()
        ConfirmButtons.setText("确认")
        ConfirmButtons.setFixedSize(70, 40)
        CancelButtons = QToolButton()
        CancelButtons.setText("取消")
        CancelButtons.setFixedSize(70, 40)

        hlayout = QHBoxLayout()
        hlayout.addWidget(ConfirmButtons)
        hlayout.addWidget(CancelButtons)

        ConfirmButtons.clicked.connect(self.confirmation_signal)  # 点击ok
        CancelButtons.clicked.connect(self.cancel_signal)  # 点击cancel

        hwg = QWidget()
        vwg = QWidget()
        hwg.setLayout(hlayout)
        vwg.setLayout(layout)
        wlayout.addWidget(vwg)
        wlayout.addWidget(hwg)

        self.setLayout(wlayout)

    def confirmation_signal(self):  # 点击ok是发送内置信号
        for index, value in enumerate([self.Category.itemText(i) for i in range(self.Category.count())]):
            if value == self.Category.currentText():
                category = index
        self.dialogSignel.emit(0, [category, self.Gender.currentIndex()])
        self.accept()

    def cancel_signal(self):  # 点击cancel时，发送自定义信号
        self.dialogSignel.emit(1, ["清空"])
        self.reject()


class ModelThread(QtCore.QThread):
    model_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.exitThread = False
        self.mutex = QtCore.QMutex()
        self.taskAdded = QtCore.QWaitCondition()
        self.image_array = None
        self.model = None
        self.graph = tf.get_default_graph()
        # 创建黑白底图 array 数组
        self.array_bw = self.black_white()

    def black_white(self):
        array_ = np.zeros((2048, 2448, 3), np.uint8)
        img = cv2.circle(array_, (1275, 1296), 530, (255, 255, 255), -1)
        return img

    def add_task_(self):
        with QtCore.QMutexLocker(self.mutex):
            # 唤醒线程
            self.taskAdded.wakeOne()

    def error_message(self, information):
        # 错误提示
        box = QMessageBox(QMessageBox.Warning, "警告框", information)
        box.addButton(self.tr("确定"), QMessageBox.YesRole)
        box.exec_()

    def run(self):
        while True:
            with QtCore.QMutexLocker(self.mutex):
                self.taskAdded.wait(self.mutex)
            # self.image_array[self.array_bw == 0] = 255
            # cv2.imwrite("2.jpg", self.image_array)
            # img = cv2.resize(self.image_array, (200, 300))
            # img = np.array(img).astype('float32') / 255
            # img = np.reshape(img, [1, 250, 250, 3])
            with self.graph.as_default():
                pred_val = self.model.inference(self.image_array)
            self.model_signal.emit(pred_val)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Identification()
    form.showMaximized()
    sys.exit(app.exec_())
