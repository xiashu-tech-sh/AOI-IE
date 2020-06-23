# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pattern_info.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(665, 365)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(-1, 20, -1, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.patternEdit = QtWidgets.QLineEdit(Form)
        self.patternEdit.setObjectName("patternEdit")
        self.gridLayout.addWidget(self.patternEdit, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.snEdit = QtWidgets.QLineEdit(Form)
        self.snEdit.setObjectName("snEdit")
        self.gridLayout.addWidget(self.snEdit, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.createdTimeEdit = QtWidgets.QDateTimeEdit(Form)
        self.createdTimeEdit.setObjectName("createdTimeEdit")
        self.gridLayout.addWidget(self.createdTimeEdit, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.editedTimeEdit = QtWidgets.QDateTimeEdit(Form)
        self.editedTimeEdit.setObjectName("editedTimeEdit")
        self.gridLayout.addWidget(self.editedTimeEdit, 3, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(148, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 211, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Pattern"))
        self.label_4.setText(_translate("Form", "SN"))
        self.label_2.setText(_translate("Form", "Created:"))
        self.label_3.setText(_translate("Form", "Edited:"))

