# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form_edit(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1139, 818)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.horizontalLayout.addWidget(self.tableWidget)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tag = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.tag.setFont(font)
        self.tag.setObjectName("tag")
        self.gridLayout_2.addWidget(self.tag, 1, 0, 1, 1)
        self.NG_type = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.NG_type.setFont(font)
        self.NG_type.setObjectName("NG_type")
        self.gridLayout_2.addWidget(self.NG_type, 3, 0, 1, 1)
        self.pushButton_16 = QtWidgets.QPushButton(Form)
        self.pushButton_16.setObjectName("pushButton_16")
        self.gridLayout_2.addWidget(self.pushButton_16, 5, 0, 1, 1)
        self.module_type = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.module_type.setFont(font)
        self.module_type.setObjectName("module_type")
        self.gridLayout_2.addWidget(self.module_type, 2, 0, 1, 1)
        self.dete_alg_value = QtWidgets.QComboBox(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.dete_alg_value.setFont(font)
        self.dete_alg_value.setObjectName("dete_alg_value")
        self.dete_alg_value.addItem("")
        self.dete_alg_value.addItem("")
        self.dete_alg_value.addItem("")
        self.dete_alg_value.addItem("")
        self.dete_alg_value.addItem("")
        self.gridLayout_2.addWidget(self.dete_alg_value, 4, 1, 1, 1)
        self.detection_algorithm = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.detection_algorithm.setFont(font)
        self.detection_algorithm.setObjectName("detection_algorithm")
        self.gridLayout_2.addWidget(self.detection_algorithm, 4, 0, 1, 1)
        self.NG_value = QtWidgets.QComboBox(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.NG_value.setFont(font)
        self.NG_value.setObjectName("NG_value")
        self.NG_value.addItem("")
        self.NG_value.addItem("")
        self.NG_value.addItem("")
        self.gridLayout_2.addWidget(self.NG_value, 3, 1, 1, 1)
        self.label_19 = QtWidgets.QLabel(Form)
        self.label_19.setText("")
        self.label_19.setObjectName("label_19")
        self.gridLayout_2.addWidget(self.label_19, 0, 0, 1, 1)
        self.type_name = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.type_name.setFont(font)
        self.type_name.setText("")
        self.type_name.setObjectName("type_name")
        self.gridLayout_2.addWidget(self.type_name, 2, 1, 1, 1)
        self.part_no = QtWidgets.QLineEdit(Form)
        self.part_no.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.part_no.setFont(font)
        self.part_no.setText("")
        self.part_no.setReadOnly(False)
        self.part_no.setObjectName("part_no")
        self.gridLayout_2.addWidget(self.part_no, 1, 1, 1, 1)
        self.gridLayout_2.setRowMinimumHeight(0, 10)
        self.gridLayout_2.setRowStretch(0, 10)
        self.gridLayout_2.setRowStretch(1, 1)
        self.gridLayout_2.setRowStretch(2, 1)
        self.gridLayout_2.setRowStretch(3, 1)
        self.gridLayout_2.setRowStretch(4, 1)
        self.gridLayout_2.setRowStretch(5, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.stackedWidget_2 = QtWidgets.QStackedWidget(Form)
        self.stackedWidget_2.setObjectName("stackedWidget_2")
        self.page_9 = QtWidgets.QWidget()
        self.page_9.setObjectName("page_9")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.page_9)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label = QtWidgets.QLabel(self.page_9)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.page_9)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 2, 0, 1, 1)
        self.horizontalSlider_3 = QtWidgets.QSlider(self.page_9)
        self.horizontalSlider_3.setMaximum(255)
        self.horizontalSlider_3.setPageStep(1)
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.gridLayout_4.addWidget(self.horizontalSlider_3, 2, 1, 1, 1)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.page_9)
        self.horizontalSlider_2.setMaximum(255)
        self.horizontalSlider_2.setPageStep(1)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.gridLayout_4.addWidget(self.horizontalSlider_2, 1, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.page_9)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.page_9)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.page_9)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 2, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.page_9)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 1, 2, 1, 1)
        self.horizontalSlider = QtWidgets.QSlider(self.page_9)
        self.horizontalSlider.setMaximum(255)
        self.horizontalSlider.setPageStep(1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.gridLayout_4.addWidget(self.horizontalSlider, 0, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.page_9)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_4.addWidget(self.checkBox, 3, 0, 1, 3)
        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 9)
        self.gridLayout_4.setColumnStretch(2, 1)
        self.horizontalLayout_13.addLayout(self.gridLayout_4)
        self.stackedWidget_2.addWidget(self.page_9)
        self.page_10 = QtWidgets.QWidget()
        self.page_10.setObjectName("page_10")
        self.stackedWidget_2.addWidget(self.page_10)
        self.verticalLayout_2.addWidget(self.stackedWidget_2)
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.page)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_3 = QtWidgets.QPushButton(self.page)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_5.addWidget(self.pushButton_3, 1, 3, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.page)
        self.label_43.setObjectName("label_43")
        self.gridLayout_5.addWidget(self.label_43, 2, 2, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.page)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_5.addWidget(self.pushButton_5, 2, 3, 1, 1)
        self.upper_limit = QtWidgets.QSpinBox(self.page)
        self.upper_limit.setProperty("value", 15)
        self.upper_limit.setObjectName("upper_limit")
        self.gridLayout_5.addWidget(self.upper_limit, 0, 1, 1, 1)
        self.lower_limit = QtWidgets.QSpinBox(self.page)
        self.lower_limit.setMaximum(100)
        self.lower_limit.setProperty("value", 100)
        self.lower_limit.setObjectName("lower_limit")
        self.gridLayout_5.addWidget(self.lower_limit, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.page)
        self.label_6.setObjectName("label_6")
        self.gridLayout_5.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_32 = QtWidgets.QLabel(self.page)
        self.label_32.setObjectName("label_32")
        self.gridLayout_5.addWidget(self.label_32, 0, 2, 1, 1)
        self.label_41 = QtWidgets.QLabel(self.page)
        self.label_41.setObjectName("label_41")
        self.gridLayout_5.addWidget(self.label_41, 2, 0, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.page)
        self.label_31.setObjectName("label_31")
        self.gridLayout_5.addWidget(self.label_31, 1, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.page)
        self.label_7.setObjectName("label_7")
        self.gridLayout_5.addWidget(self.label_7, 1, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.measurements = QtWidgets.QLabel(self.page)
        self.measurements.setStyleSheet("color: rgb(255, 0, 0);")
        self.measurements.setText("")
        self.measurements.setObjectName("measurements")
        self.horizontalLayout_12.addWidget(self.measurements)
        self.horizontalLayout_12.setStretch(0, 2)
        self.horizontalLayout_12.setStretch(1, 1)
        self.gridLayout_5.addLayout(self.horizontalLayout_12, 2, 1, 1, 1)
        self.gridLayout_5.setColumnStretch(0, 1)
        self.gridLayout_5.setColumnStretch(1, 1)
        self.gridLayout_5.setColumnStretch(3, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_5)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.page_2)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 4, 0, 1, 2)
        self.label_29 = QtWidgets.QLabel(self.page_2)
        self.label_29.setText("")
        self.label_29.setObjectName("label_29")
        self.gridLayout.addWidget(self.label_29, 5, 0, 1, 2)
        self.aboutButton = QtWidgets.QPushButton(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.aboutButton.setFont(font)
        self.aboutButton.setObjectName("aboutButton")
        self.gridLayout.addWidget(self.aboutButton, 2, 1, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout.addWidget(self.pushButton_6, 1, 0, 1, 1)
        self.updown = QtWidgets.QPushButton(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.updown.setFont(font)
        self.updown.setObjectName("updown")
        self.gridLayout.addWidget(self.updown, 2, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 6, 0, 1, 2)
        self.pushButton_7 = QtWidgets.QPushButton(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout.addWidget(self.pushButton_7, 1, 1, 1, 1)
        self.label_30 = QtWidgets.QLabel(self.page_2)
        self.label_30.setText("")
        self.label_30.setObjectName("label_30")
        self.gridLayout.addWidget(self.label_30, 3, 0, 1, 2)
        self.gridLayout.setRowStretch(0, 2)
        self.horizontalLayout_9.addLayout(self.gridLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.n_x_threshold_7 = QtWidgets.QLabel(self.page_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.n_x_threshold_7.setFont(font)
        self.n_x_threshold_7.setObjectName("n_x_threshold_7")
        self.horizontalLayout_2.addWidget(self.n_x_threshold_7)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.template_image_2 = QtWidgets.QLabel(self.page_2)
        self.template_image_2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.template_image_2.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.template_image_2.setText("")
        self.template_image_2.setAlignment(QtCore.Qt.AlignCenter)
        self.template_image_2.setObjectName("template_image_2")
        self.verticalLayout.addWidget(self.template_image_2)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 9)
        self.horizontalLayout_9.addLayout(self.verticalLayout)
        self.horizontalLayout_9.setStretch(0, 1)
        self.horizontalLayout_9.setStretch(1, 1)
        self.horizontalLayout_11.addLayout(self.horizontalLayout_9)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.page_3)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem1, 5, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.page_3)
        self.label_13.setText("")
        self.label_13.setObjectName("label_13")
        self.gridLayout_6.addWidget(self.label_13, 4, 0, 1, 2)
        self.pushButton_4 = QtWidgets.QPushButton(self.page_3)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_6.addWidget(self.pushButton_4, 5, 1, 1, 1)
        self.start_interval_4 = QtWidgets.QLineEdit(self.page_3)
        self.start_interval_4.setObjectName("start_interval_4")
        self.gridLayout_6.addWidget(self.start_interval_4, 1, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.page_3)
        self.label_9.setText("")
        self.label_9.setObjectName("label_9")
        self.gridLayout_6.addWidget(self.label_9, 0, 0, 1, 2)
        self.n_x_threshold_6 = QtWidgets.QLabel(self.page_3)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.n_x_threshold_6.setFont(font)
        self.n_x_threshold_6.setObjectName("n_x_threshold_6")
        self.gridLayout_6.addWidget(self.n_x_threshold_6, 1, 0, 1, 1)
        self.horizontalSlider_5 = QtWidgets.QSlider(self.page_3)
        self.horizontalSlider_5.setMaximum(360)
        self.horizontalSlider_5.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_5.setObjectName("horizontalSlider_5")
        self.gridLayout_6.addWidget(self.horizontalSlider_5, 2, 1, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.page_3)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_6.addWidget(self.label_18, 2, 0, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout_6)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.n_x_threshold_5 = QtWidgets.QLabel(self.page_3)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.n_x_threshold_5.setFont(font)
        self.n_x_threshold_5.setObjectName("n_x_threshold_5")
        self.verticalLayout_9.addWidget(self.n_x_threshold_5)
        self.template_image_4 = QtWidgets.QLabel(self.page_3)
        self.template_image_4.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.template_image_4.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.template_image_4.setText("")
        self.template_image_4.setAlignment(QtCore.Qt.AlignCenter)
        self.template_image_4.setObjectName("template_image_4")
        self.verticalLayout_9.addWidget(self.template_image_4)
        self.verticalLayout_9.setStretch(0, 1)
        self.verticalLayout_9.setStretch(1, 9)
        self.horizontalLayout_4.addLayout(self.verticalLayout_9)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 1)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_4)
        self.stackedWidget.addWidget(self.page_3)
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setObjectName("page_5")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.page_5)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_20 = QtWidgets.QLabel(self.page_5)
        self.label_20.setText("")
        self.label_20.setObjectName("label_20")
        self.gridLayout_7.addWidget(self.label_20, 4, 0, 1, 2)
        self.pushButton_10 = QtWidgets.QPushButton(self.page_5)
        self.pushButton_10.setObjectName("pushButton_10")
        self.gridLayout_7.addWidget(self.pushButton_10, 1, 1, 1, 1)
        self.pushButton_8 = QtWidgets.QPushButton(self.page_5)
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout_7.addWidget(self.pushButton_8, 1, 0, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.page_5)
        self.label_21.setText("")
        self.label_21.setObjectName("label_21")
        self.gridLayout_7.addWidget(self.label_21, 0, 0, 1, 2)
        self.pushButton_11 = QtWidgets.QPushButton(self.page_5)
        self.pushButton_11.setObjectName("pushButton_11")
        self.gridLayout_7.addWidget(self.pushButton_11, 2, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.page_5)
        self.label_12.setObjectName("label_12")
        self.gridLayout_7.addWidget(self.label_12, 5, 0, 1, 1)
        self.pushButton_15 = QtWidgets.QPushButton(self.page_5)
        self.pushButton_15.setObjectName("pushButton_15")
        self.gridLayout_7.addWidget(self.pushButton_15, 5, 1, 1, 1)
        self.gridLayout_7.setRowStretch(0, 2)
        self.gridLayout_7.setRowStretch(4, 1)
        self.horizontalLayout_7.addLayout(self.gridLayout_7)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_27 = QtWidgets.QLabel(self.page_5)
        self.label_27.setText("")
        self.label_27.setObjectName("label_27")
        self.gridLayout_8.addWidget(self.label_27, 0, 0, 1, 2)
        self.label_24 = QtWidgets.QLabel(self.page_5)
        self.label_24.setObjectName("label_24")
        self.gridLayout_8.addWidget(self.label_24, 3, 0, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.page_5)
        self.label_28.setText("")
        self.label_28.setObjectName("label_28")
        self.gridLayout_8.addWidget(self.label_28, 4, 0, 1, 2)
        self.label_22 = QtWidgets.QLabel(self.page_5)
        self.label_22.setObjectName("label_22")
        self.gridLayout_8.addWidget(self.label_22, 1, 0, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.page_5)
        self.label_26.setText("")
        self.label_26.setObjectName("label_26")
        self.gridLayout_8.addWidget(self.label_26, 2, 1, 1, 1)
        self.g_PN_threshold_value_2 = QtWidgets.QDoubleSpinBox(self.page_5)
        self.g_PN_threshold_value_2.setDecimals(0)
        self.g_PN_threshold_value_2.setMinimum(-100.0)
        self.g_PN_threshold_value_2.setMaximum(100.0)
        self.g_PN_threshold_value_2.setSingleStep(1.0)
        # self.g_PN_threshold_value_2.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.g_PN_threshold_value_2.setProperty("value", 20.0)
        self.g_PN_threshold_value_2.setObjectName("g_PN_threshold_value_2")
        self.gridLayout_8.addWidget(self.g_PN_threshold_value_2, 1, 1, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.page_5)
        self.label_23.setObjectName("label_23")
        self.gridLayout_8.addWidget(self.label_23, 2, 0, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.page_5)
        self.label_25.setText("")
        self.label_25.setObjectName("label_25")
        self.gridLayout_8.addWidget(self.label_25, 3, 1, 1, 1)
        self.gridLayout_8.setRowStretch(0, 2)
        self.gridLayout_8.setRowStretch(4, 1)
        self.horizontalLayout_7.addLayout(self.gridLayout_8)
        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 1)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_7)
        self.stackedWidget.addWidget(self.page_5)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.page_4)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.n_x_threshold_2 = QtWidgets.QLabel(self.page_4)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.n_x_threshold_2.setFont(font)
        self.n_x_threshold_2.setObjectName("n_x_threshold_2")
        self.gridLayout_3.addWidget(self.n_x_threshold_2, 1, 0, 1, 1)
        self.pushButton_19 = QtWidgets.QPushButton(self.page_4)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.pushButton_19.setFont(font)
        self.pushButton_19.setObjectName("pushButton_19")
        self.gridLayout_3.addWidget(self.pushButton_19, 3, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.page_4)
        self.label_14.setText("")
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 0, 0, 1, 3)
        self.label_15 = QtWidgets.QLabel(self.page_4)
        self.label_15.setText("")
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 2, 0, 1, 3)
        self.min_unit_2 = QtWidgets.QLabel(self.page_4)
        self.min_unit_2.setObjectName("min_unit_2")
        self.gridLayout_3.addWidget(self.min_unit_2, 1, 2, 1, 1)
        self.similarValue = QtWidgets.QDoubleSpinBox(self.page_4)
        self.similarValue.setDecimals(1)
        self.similarValue.setMinimum(0.0)
        self.similarValue.setMaximum(100.0)
        self.similarValue.setSingleStep(1.0)
        # self.similarValue.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.similarValue.setProperty("value", 50.0)
        self.similarValue.setObjectName("similarValue")
        self.gridLayout_3.addWidget(self.similarValue, 1, 1, 1, 1)
        self.horizontalLayout_6.addLayout(self.gridLayout_3)
        self.verticalLayout_19 = QtWidgets.QVBoxLayout()
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.n_x_threshold_10 = QtWidgets.QLabel(self.page_4)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.n_x_threshold_10.setFont(font)
        self.n_x_threshold_10.setObjectName("n_x_threshold_10")
        self.verticalLayout_19.addWidget(self.n_x_threshold_10)
        self.template_image_5 = QtWidgets.QLabel(self.page_4)
        self.template_image_5.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.template_image_5.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.template_image_5.setText("")
        self.template_image_5.setAlignment(QtCore.Qt.AlignCenter)
        self.template_image_5.setObjectName("template_image_5")
        self.verticalLayout_19.addWidget(self.template_image_5)
        self.verticalLayout_19.setStretch(0, 1)
        self.verticalLayout_19.setStretch(1, 9)
        self.horizontalLayout_6.addLayout(self.verticalLayout_19)
        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 1)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_6)
        self.stackedWidget.addWidget(self.page_4)
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setObjectName("page_6")
        self.horizontalLayout_25 = QtWidgets.QHBoxLayout(self.page_6)
        self.horizontalLayout_25.setObjectName("horizontalLayout_25")
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.gridLayout_12 = QtWidgets.QGridLayout()
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.pushButton_22 = QtWidgets.QPushButton(self.page_6)
        self.pushButton_22.setObjectName("pushButton_22")
        self.gridLayout_12.addWidget(self.pushButton_22, 6, 1, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.page_6)
        self.label_33.setText("")
        self.label_33.setObjectName("label_33")
        self.gridLayout_12.addWidget(self.label_33, 5, 0, 1, 2)
        self.pushButton_14 = QtWidgets.QPushButton(self.page_6)
        self.pushButton_14.setObjectName("pushButton_14")
        self.gridLayout_12.addWidget(self.pushButton_14, 1, 1, 1, 1)
        self.label_34 = QtWidgets.QLabel(self.page_6)
        self.label_34.setObjectName("label_34")
        self.gridLayout_12.addWidget(self.label_34, 6, 0, 1, 1)
        self.pushButton_13 = QtWidgets.QPushButton(self.page_6)
        self.pushButton_13.setObjectName("pushButton_13")
        self.gridLayout_12.addWidget(self.pushButton_13, 2, 0, 1, 1)
        self.pushButton_21 = QtWidgets.QPushButton(self.page_6)
        self.pushButton_21.setObjectName("pushButton_21")
        self.gridLayout_12.addWidget(self.pushButton_21, 3, 0, 1, 1)
        self.pushButton_12 = QtWidgets.QPushButton(self.page_6)
        self.pushButton_12.setObjectName("pushButton_12")
        self.gridLayout_12.addWidget(self.pushButton_12, 2, 1, 1, 1)
        self.pushButton_9 = QtWidgets.QPushButton(self.page_6)
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout_12.addWidget(self.pushButton_9, 1, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.page_6)
        self.label_17.setText("")
        self.label_17.setObjectName("label_17")
        self.gridLayout_12.addWidget(self.label_17, 0, 0, 1, 2)
        self.gridLayout_12.setRowStretch(0, 2)
        self.gridLayout_12.setRowStretch(5, 1)
        self.horizontalLayout_24.addLayout(self.gridLayout_12)
        self.gridLayout_13 = QtWidgets.QGridLayout()
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.g_result_3 = QtWidgets.QLabel(self.page_6)
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(10)
        self.g_result_3.setFont(font)
        self.g_result_3.setObjectName("g_result_3")
        self.gridLayout_13.addWidget(self.g_result_3, 3, 0, 1, 1)
        self.label_39 = QtWidgets.QLabel(self.page_6)
        self.label_39.setText("")
        self.label_39.setObjectName("label_39")
        self.gridLayout_13.addWidget(self.label_39, 0, 0, 1, 2)
        self.label_36 = QtWidgets.QLabel(self.page_6)
        self.label_36.setObjectName("label_36")
        self.gridLayout_13.addWidget(self.label_36, 2, 0, 1, 1)
        self.label_37 = QtWidgets.QLabel(self.page_6)
        self.label_37.setText("")
        self.label_37.setObjectName("label_37")
        self.gridLayout_13.addWidget(self.label_37, 2, 1, 1, 1)
        self.g_PN_threshold_value_3 = QtWidgets.QDoubleSpinBox(self.page_6)
        self.g_PN_threshold_value_3.setDecimals(0)
        self.g_PN_threshold_value_3.setMinimum(-100.0)
        self.g_PN_threshold_value_3.setMaximum(100.0)
        self.g_PN_threshold_value_3.setSingleStep(1.0)
        # self.g_PN_threshold_value_3.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.g_PN_threshold_value_3.setProperty("value", 20.0)
        self.g_PN_threshold_value_3.setObjectName("g_PN_threshold_value_3")
        self.gridLayout_13.addWidget(self.g_PN_threshold_value_3, 1, 1, 1, 1)
        self.label_38 = QtWidgets.QLabel(self.page_6)
        self.label_38.setText("")
        self.label_38.setObjectName("label_38")
        self.gridLayout_13.addWidget(self.label_38, 3, 1, 1, 1)
        self.label_35 = QtWidgets.QLabel(self.page_6)
        self.label_35.setObjectName("label_35")
        self.gridLayout_13.addWidget(self.label_35, 1, 0, 1, 1)
        self.label_40 = QtWidgets.QLabel(self.page_6)
        self.label_40.setText("")
        self.label_40.setObjectName("label_40")
        self.gridLayout_13.addWidget(self.label_40, 4, 0, 1, 1)
        self.gridLayout_13.setRowStretch(0, 2)
        self.gridLayout_13.setRowStretch(4, 2)
        self.horizontalLayout_24.addLayout(self.gridLayout_13)
        self.horizontalLayout_24.setStretch(0, 1)
        self.horizontalLayout_24.setStretch(1, 1)
        self.horizontalLayout_25.addLayout(self.horizontalLayout_24)
        self.stackedWidget.addWidget(self.page_6)
        self.verticalLayout_2.addWidget(self.stackedWidget)
        self.horizontalLayout_14.addLayout(self.verticalLayout_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 481, 364))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_4.addWidget(self.scrollArea)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.template_image_3 = QtWidgets.QLabel(Form)
        self.template_image_3.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.template_image_3.setToolTip("")
        self.template_image_3.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.template_image_3.setText("")
        self.template_image_3.setAlignment(QtCore.Qt.AlignCenter)
        self.template_image_3.setObjectName("template_image_3")
        self.verticalLayout_4.addWidget(self.template_image_3)
        self.verticalLayout_4.setStretch(0, 8)
        self.verticalLayout_4.setStretch(1, 1)
        self.verticalLayout_4.setStretch(2, 8)
        self.horizontalLayout_14.addLayout(self.verticalLayout_4)
        self.horizontalLayout_14.setStretch(0, 9)
        self.horizontalLayout_14.setStretch(1, 7)
        self.horizontalLayout_15.addLayout(self.horizontalLayout_14)

        self.retranslateUi(Form)
        self.stackedWidget_2.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Form", "NG类型"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "子件名称"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "检测结果"))
        self.tag.setText(_translate("Form", "料号："))
        self.NG_type.setText(_translate("Form", "NG类型："))
        self.pushButton_16.setText(_translate("Form", "保存"))
        self.module_type.setText(_translate("Form", "子件类型："))
        self.dete_alg_value.setItemText(0, _translate("Form", "模板匹配"))
        self.dete_alg_value.setItemText(1, _translate("Form", "灰度差"))
        self.dete_alg_value.setItemText(2, _translate("Form", "OCR识别"))
        self.dete_alg_value.setItemText(3, _translate("Form", "颜色匹配"))
        self.dete_alg_value.setItemText(4, _translate("Form", "颜色提取"))
        self.detection_algorithm.setText(_translate("Form", "检测算法："))
        self.NG_value.setItemText(0, _translate("Form", "漏件"))
        self.NG_value.setItemText(1, _translate("Form", "极反"))
        self.NG_value.setItemText(2, _translate("Form", "错件"))
        self.label.setText(_translate("Form", "Greed:"))
        self.label_4.setText(_translate("Form", "Blue"))
        self.label_8.setText(_translate("Form", "0"))
        self.label_3.setText(_translate("Form", "Red:"))
        self.label_11.setText(_translate("Form", "0"))
        self.label_10.setText(_translate("Form", "0"))
        self.checkBox.setText(_translate("Form", "反转"))
        self.pushButton_3.setText(_translate("Form", "保存参数"))
        self.label_43.setText(_translate("Form", "%"))
        self.pushButton_5.setText(_translate("Form", "检测"))
        self.label_6.setText(_translate("Form", "颜色比例下限制："))
        self.label_32.setText(_translate("Form", "%"))
        self.label_41.setText(_translate("Form", "测量值："))
        self.label_31.setText(_translate("Form", "%"))
        self.label_7.setText(_translate("Form", "颜色比例上限制："))
        self.pushButton_2.setText(_translate("Form", "整体填充"))
        self.aboutButton.setText(_translate("Form", "向右填充"))
        self.pushButton_6.setText(_translate("Form", "向上填充"))
        self.updown.setText(_translate("Form", "向左填充"))
        self.pushButton.setText(_translate("Form", "生成模板"))
        self.pushButton_7.setText(_translate("Form", "向下填充"))
        self.n_x_threshold_7.setText(_translate("Form", "模板图像"))
        self.pushButton_4.setText(_translate("Form", "生成模板"))
        self.n_x_threshold_6.setText(_translate("Form", "模板内容："))
        self.label_18.setText(_translate("Form", "旋转角度："))
        self.n_x_threshold_5.setText(_translate("Form", "模板图像"))
        self.pushButton_10.setText(_translate("Form", "左右检测"))
        self.pushButton_8.setText(_translate("Form", "上下检测"))
        self.pushButton_11.setText(_translate("Form", "获取检测区间"))
        self.label_12.setText(_translate("Form", "极性检测算法"))
        self.pushButton_15.setText(_translate("Form", "检测"))
        self.label_24.setText(_translate("Form", "极性检测结果:"))
        self.label_22.setText(_translate("Form", "正负极灰度差阈值:"))
        self.label_23.setText(_translate("Form", "正负极灰度差:"))
        self.n_x_threshold_2.setText(_translate("Form", "相似度阈值:"))
        self.pushButton_19.setText(_translate("Form", "生成模板"))
        self.min_unit_2.setText(_translate("Form", "%"))
        self.n_x_threshold_10.setText(_translate("Form", "模板图像"))
        self.pushButton_22.setText(_translate("Form", "检测"))
        self.pushButton_14.setText(_translate("Form", "正负左右旋转"))
        self.label_34.setText(_translate("Form", "极性检测算法："))
        self.pushButton_13.setText(_translate("Form", "正负上下反转"))
        self.pushButton_21.setText(_translate("Form", "获取检测区间"))
        self.pushButton_12.setText(_translate("Form", "正负左右反转"))
        self.pushButton_9.setText(_translate("Form", "正负上下旋转"))
        self.g_result_3.setText(_translate("Form", "极性检测结果:"))
        self.label_36.setText(_translate("Form", "正负极灰度差:"))
        self.label_35.setText(_translate("Form", "正负极灰度差阈值:"))

