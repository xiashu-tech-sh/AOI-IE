# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pcb_location.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(539, 352)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupbox_2 = QtWidgets.QGroupBox(Form)
        self.groupbox_2.setObjectName("groupbox_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupbox_2)
        self.horizontalLayout_3.setContentsMargins(0, 3, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pcbLabel = QtWidgets.QLabel(self.groupbox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pcbLabel.sizePolicy().hasHeightForWidth())
        self.pcbLabel.setSizePolicy(sizePolicy)
        self.pcbLabel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pcbLabel.setText("")
        self.pcbLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.pcbLabel.setObjectName("pcbLabel")
        self.verticalLayout.addWidget(self.pcbLabel)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.savePCBButton = QtWidgets.QPushButton(self.groupbox_2)
        self.savePCBButton.setObjectName("savePCBButton")
        self.horizontalLayout_2.addWidget(self.savePCBButton)
        self.resetPCBButton = QtWidgets.QPushButton(self.groupbox_2)
        self.resetPCBButton.setObjectName("resetPCBButton")
        self.horizontalLayout_2.addWidget(self.resetPCBButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.setStretch(0, 1)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.label_2 = QtWidgets.QLabel(self.groupbox_2)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.groupbox_2)
        self.verticalLayout_2.setStretch(0, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupbox_2.setTitle(_translate("Form", "PCB板区域提取"))
        self.savePCBButton.setText(_translate("Form", "保存"))
        self.resetPCBButton.setText(_translate("Form", "重置"))
        self.label_2.setText(_translate("Form", "提示：\n"
"选择合适标记点，移动选项框到相应位置，点击“提取模板”。"))

