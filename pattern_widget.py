import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui


class PatternWidget(QtWidgets.QWidget):
    ''' 程式设计界面，主要功能包括：
        1. 程式创建/保存/载入、基本绘图工具、基础元器件模板；
        2. 左边工作区（imageLabel），用于绘制元器件的程式模板；
        3. 右上角程式信息展示区域；
        4. 右下角相机实时预览区域。
    '''
    def __init__(self):
        super().__init__()
        new_action = lambda icon, text : QtWidgets.QAction(QtGui.QIcon(icon), text)
        # actions
        self.createAction = new_action('./icon/create-100.png', '新建程式')
        self.saveAction = new_action('./icon/save-64.png', '保存程式')
        self.openAction = new_action('./icon/folder-50.png', '打开程式')

        self.zoomInAction = new_action('./icon/zoom-in-50.png', '放大')
        self.zoomOutAction = new_action('./icon/zoom-out-50.png', '缩小')
        self.cursorAction = new_action('./icon/cursor-50.png', '选择')
        self.moveAction = new_action('./icon/hand-50.png', '移动')

        self.pcbLocationAction = new_action('./icon/green-flag-50.png', 'PCB定位')
        self.maskAction = new_action('./icon/mask-50.png', 'Mask')

        self.capacitorAction = new_action('./icon/capacitor.png', '电解电容')
        self.resistorAction = new_action('./icon/resistor.png', '色环电阻')
        self.slotAction = new_action('./icon/slot.png', '插槽')
        self.componentAction = new_action('./icon/component.png', '一般元件')

        self.homeAction = new_action('./icon/home-50.png', '检测界面')

        # init toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addActions([self.createAction, self.saveAction, self.openAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.zoomInAction, self.zoomOutAction, self.cursorAction, self.moveAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.pcbLocationAction, self.maskAction, self.capacitorAction, self.resistorAction,
                                 self.slotAction, self.componentAction])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.homeAction])
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
    win = PatternWidget()
    win.setWindowTitle('程式制作窗口')
    win.showMaximized()
    sys.exit(app.exec_())