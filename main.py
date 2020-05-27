import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from online_widget import OnlineWidget
from pattern_widget import PatternWidget


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

        self.onlineWidget = OnlineWidget()
        self.patternWidget = PatternWidget()

        self.stackWidget = QtWidgets.QStackedWidget()
        self.stackWidget.addWidget(self.onlineWidget)
        self.stackWidget.addWidget(self.patternWidget)

        self.setCentralWidget(self.stackWidget)

        # switch between onlineWidget and patternWidget
        self.onlineWidget.designAction.triggered.connect(lambda : self.stackWidget.setCurrentWidget(self.patternWidget))
        self.patternWidget.homeAction.triggered.connect(lambda : self.stackWidget.setCurrentWidget(self.onlineWidget))


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