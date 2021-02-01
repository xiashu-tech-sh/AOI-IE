''' 相机接口类 '''
import os
import sys
sys.path.append('./MvImport')
import numpy as np
from MvImport.MvCameraControl_class import *
from ctypes import *
from PyQt5 import QtCore, QtGui
import cv2
# import imageio


class CameraError(Exception):
    def __init__(self,  *args, **kwargs):
        super().__init__( *args, **kwargs)


class CameraObj:
    def __init__(self):
        self.cam = None
        self.ip = ''
        self.strModeName = ''
        self.strSerialNumber = ''
        self.payloadSize = 0
        self.bufCache = 0
        self.st_frame_info = None
        self.isOpen = False

    def connect(self):
        ''' 连接相机，开始取流 '''
        deviceList = MV_CC_DEVICE_INFO_LIST()
        # GigE 设备 或者 USB 设备
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        # 枚举设备 | en:Enum device
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            raise CameraError("枚举相机设备失败")
        # 获取设备个数
        if deviceList.nDeviceNum < 1:
            raise CameraError("未获取到相机")

        # 获取相机设备信息
        mvcc_dev_info = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
        # 如果是 GigE 设备
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            # 获取当前设备名称
            self.strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                self.strModeName += chr(per)
            # 获取当前设备 IP
            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            self.ip = "%d.%d.%d.%d" % (nip1, nip2, nip3, nip4)
        # 如果是 USB 设备
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            # 获取当前设备名称
            self.strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                self.strModeName += chr(per)
            # 获取用户序列号
            self.strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                self.strSerialNumber += chr(per)
        # 实例化相机
        self.cam = MvCamera()
        # 创建设备句柄
        ret = self.cam.MV_CC_CreateHandle(mvcc_dev_info)
        if ret != 0:
            # 销毁句柄
            self.cam.MV_CC_DestroyHandle()
            raise CameraError('创建相机设备句柄失败')
        # 打开设备
        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            self.cam.MV_CC_DestroyHandle()
            raise CameraError('打开相机失败')
        # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                if ret != 0:
                    raise CameraError('设置相机数据包大小失败')
            else:
                raise CameraError('获取相机网络最佳包大小失败')
        # 获取采集数据帧率
        # stBool = POINTER(c_bool)()
        # POINTER
        # stBool = ctypes.c_bool()
        # ret = self.cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(stBool))
        # if ret != 0:
            # raise CameraError('获取相机采集帧率启用失败')
        # 获取有效载荷大小
        stParam = MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

        ret = self.cam.MV_CC_GetIntValue("PayloadSize", stParam)
        if ret != 0:
            raise CameraError('获取相机有效载荷大小失败')
        # 有效负载大小
        self.payloadSize = stParam.nCurValue
        self.bufCache = (c_ubyte * self.payloadSize)()

        # ch:设置触发模式为off | en:Set trigger mode as off
        ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            raise CameraError('相机设置触发模式失败')
        
        self.isOpen = True
        self.cam.MV_CC_StartGrabbing()

    def get_rgb_image(self):
        if not self.cam:
            return
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        while True:
            ret = self.cam.MV_CC_GetOneFrameTimeout(byref(self.bufCache), self.payloadSize, stFrameInfo, 1000)
            if ret == 0:
                break
        # 获取到图像的时间开始节点获取到图像的时间开始节点
        self.st_frame_info = stFrameInfo
        img_buff = (c_ubyte * (self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048)*3)()
        stParam = MV_SAVE_IMAGE_PARAM_EX()
        stParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
        stParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
        stParam.nDataLen = self.st_frame_info.nFrameLen
        stParam.pData = cast(self.bufCache, POINTER(c_ubyte))

        # 转换像素结构体赋值
        stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
        memset(byref(stConvertParam), 0, sizeof(stConvertParam))
        stConvertParam.nWidth = self.st_frame_info.nWidth
        stConvertParam.nHeight = self.st_frame_info.nHeight
        stConvertParam.pSrcData = self.bufCache
        stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
        stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType
        data = True
        # Mono8直接显示
        if data:
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
            ret = self.cam.MV_CC_ConvertPixelType(stConvertParam)

            memmove(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
            numArray = self.mono_numpy(img_buff, self.st_frame_info.nWidth,self.st_frame_info.nHeight)

        # 如果是彩色且非RGB则转为RGB后显示
        elif data is True:
            nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
            stConvertParam.enDstPixelType = PixelType_Gvsp_BGR8_Packed
            stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
            stConvertParam.nDstBufferSize = nConvertSize
            ret = self.cam.MV_CC_ConvertPixelType(stConvertParam)

            memmove(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
            numArray = self.color_numpy(img_buff, self.st_frame_info.nWidth, self.st_frame_info.nHeight)

        else:
            raise CameraError('采集格式错误')
        del img_buff
        return numArray

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

    def release(self):
        ''' 释放相机资源 '''
        self.isOpen = False
        if self.cam is None:
            return
        # ch:停止取流 | en:Stop grab image
        ret = self.cam.MV_CC_StopGrabbing()
        if ret != 0:
            print ("stop grabbing fail! ret[0x%x]" % ret)

        # ch:关闭设备 | Close device
        ret = self.cam.MV_CC_CloseDevice()
        if ret != 0:
            print ("close deivce fail! ret[0x%x]" % ret)

        # ch:销毁句柄 | Destroy handle
        ret = self.cam.MV_CC_DestroyHandle()
        if ret != 0:
            print ("destroy handle fail! ret[0x%x]" % ret)


class CameraThread(QtCore.QThread):

    newImageSignal = QtCore.pyqtSignal()

    def __init__(self, cam):
        super(CameraThread, self).__init__()
        self.cam = cam
        self.cvImage = None
        self.pixmap = None
        self.exitThread = False
        self.mutex = QtCore.QMutex()

    def get_pixmap(self):
        lock = QtCore.QMutexLocker(self.mutex)
        return self.pixmap

    def get_cvimage(self):
        lock = QtCore.QMutexLocker(self.mutex)
        return self.cvImage

    def exit_thread(self):
        self.exitThread = True

    def run(self):
        if not self.cam or not self.cam.isOpen:
            self.exitThread = False
            print('camera thread exit')
            return
        print('camera thread is runing')
        while True:
            if self.exitThread:
                break
            numArray = self.cam.get_rgb_image()
            # print('got an image')
            image = QtGui.QImage(numArray, numArray.shape[1], numArray.shape[0], numArray.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)
            
            self.mutex.lock()
            self.pixmap = QtGui.QPixmap.fromImage(image)
            self.cvImage = numArray[:,:,::-1]
            self.mutex.unlock()
            self.newImageSignal.emit()
        print('camera thread exit')
        self.exitThread = False


class VideoSource(QtCore.QObject):
    ''' 视频源，一般用作调试用，从本地视频加载数据模拟产线检测 '''

    newImageSignal = QtCore.pyqtSignal()

    def __init__(self, videofile=''):
        super().__init__()
        self.cvImage = None
        self.pixmap = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.capture)
        if videofile:
            self.load_video(videofile)

    def load_video(self, videofile):
        if not os.path.exists(videofile):
            return

        self.videofile = videofile

        # use cv2
        # self.cap = cv2.VideoCapture(self.videofile)
        # self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        # self.nframes = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # use imageio
        self.cap = imageio.get_reader(videofile)
        meta = self.cap.get_meta_data()
        self.fps = meta['fps']
        self.nframes = meta['nframes']

        print(self.info())
        if self.fps < 1:
            print('fps error')
            return
        
        self.currentFrame = 0
        self.tick = 1000 // self.fps
        self.timer.setInterval(self.tick)
        self.timer.start()

    def capture(self):
        # ret, frame = self.cap.read()
        frame = self.cap.get_data(self.currentFrame)
        self.cvImage = frame[:,:,::-1]
        numArray = frame.copy()  # BGR to RGB
        image = QtGui.QImage(numArray[:], numArray.shape[1], numArray.shape[0], numArray.shape[1] * 3, QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.newImageSignal.emit()
        self.currentFrame += 1
        # 循环播放
        # if self.currentFrame == self.nframes:
        #     self.currentFrame = 0

    def isRunning(self):
        ''' 为了跟相机线程类(QThread)接口保持一致 '''
        return self.timer.isActive()

    def get_pixmap(self):
        return self.pixmap

    def get_cvimage(self):
        return self.cvImage

    def info(self):
        if not hasattr(self, 'cap'):
            return ''
        text = 'fps: {}\n'.format(self.fps)
        text += 'frame all: {}'.format(self.nframes)
        return text


if __name__ == '__main__':
    cam = CameraObj()
    # try:
    cam.connect()
    # except CameraError as e:
    #     print(str(e))

    print(cam.payloadSize)
    
    import cv2
    img = cam.get_rgb_image()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(img.shape)
    print(img.dtype)
    # img = img[:,:,::-1]
    # cv2.imshow('img', cv2.resize(img, (1000, 600)))
    cv2.imshow('img', cv2.resize(img, (480, 360)))
    key = cv2.waitKey(0)
    cam.release()


    # test video source
    # from PyQt5 import QtWidgets
    # app = QtWidgets.QApplication(sys.argv)
    # videosorce = VideoSource('../JT/test.mp4')
    # sys.exit(app.exec_())

    
    # read mp4 file
    strPath = '../JT/test.mp4'
    if (os.path.exists(strPath) == False):
        print('file not exist')
    # use imageio to read video file
    # videoReader = imageio.get_reader(strPath)
    FrameNum = videoReader.get_length()
    print('frame num = ', FrameNum)
    for i in range(0, FrameNum):
        img1 = videoReader.get_data(i)
        print(type(img1))
        print(type(img1))
        # grayImg = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        # print '%5d'%i, grayImg.shape
        break


    pass