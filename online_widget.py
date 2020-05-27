import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui


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
        self.captureAction = new_action('./icon/cap-64.png', '抓取图像')
        self.parameterAction = new_action('./icon/gear-50.png', '参数设置')
        self.designAction = new_action('./icon/design-64.png', '程式设计')
        # init toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addActions([self.patternSelectAction, self.startAction, self.stopAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.cameraOpenAction, self.cameraCloseAction, self.videoAction, self.captureAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.parameterAction, self.designAction])
        self.toolbar.setIconSize(QtCore.QSize(32, 32))

        # left center view
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)

        # right top view: TODO
        self.passWidget = QtWidgets.QWidget()

        # right buttom view
        self.videoLabel = QtWidgets.QLabel()
        self.videoLabel.setStyleSheet('background-color: rgb(0, 0, 0);')
        self.videoLabel.setAlignment(QtCore.Qt.AlignCenter)

        # right layout
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.setSpacing(13)
        rightLayout.addWidget(self.passWidget, 1)
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
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = OnlineWidget()
    win.showMaximized()
    sys.exit(app.exec_())

