# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'res/clientConnect.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dConnect(object):
    def setupUi(self, dConnect):
        dConnect.setObjectName("dConnect")
        dConnect.resize(300, 400)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ectec-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dConnect.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(dConnect)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frameMenuBar = QtWidgets.QFrame(dConnect)
        self.frameMenuBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMenuBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMenuBar.setObjectName("frameMenuBar")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frameMenuBar)
        self.horizontalLayout_2.setContentsMargins(6, 3, 6, 3)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.toolButtonMenu = QtWidgets.QToolButton(self.frameMenuBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButtonMenu.sizePolicy().hasHeightForWidth())
        self.toolButtonMenu.setSizePolicy(sizePolicy)
        self.toolButtonMenu.setMinimumSize(QtCore.QSize(0, 0))
        icon = QtGui.QIcon.fromTheme("configure")
        self.toolButtonMenu.setIcon(icon)
        self.toolButtonMenu.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.toolButtonMenu.setAutoRaise(True)
        self.toolButtonMenu.setObjectName("toolButtonMenu")
        self.horizontalLayout_2.addWidget(self.toolButtonMenu)
        self.verticalLayout.addWidget(self.frameMenuBar)
        self.groupServer = QtWidgets.QGroupBox(dConnect)
        self.groupServer.setChecked(False)
        self.groupServer.setObjectName("groupServer")
        self.formLayout = QtWidgets.QFormLayout(self.groupServer)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setObjectName("formLayout")
        self.labelAddress = QtWidgets.QLabel(self.groupServer)
        self.labelAddress.setObjectName("labelAddress")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labelAddress)
        self.entryAddress = QtWidgets.QLineEdit(self.groupServer)
        self.entryAddress.setText("192.168.178.0")
        self.entryAddress.setFrame(True)
        self.entryAddress.setPlaceholderText("192.168.178.28")
        self.entryAddress.setClearButtonEnabled(True)
        self.entryAddress.setObjectName("entryAddress")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.entryAddress)
        self.labelPort = QtWidgets.QLabel(self.groupServer)
        self.labelPort.setObjectName("labelPort")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelPort)
        self.spinBoxPort = QtWidgets.QSpinBox(self.groupServer)
        self.spinBoxPort.setMinimum(1)
        self.spinBoxPort.setMaximum(65530)
        self.spinBoxPort.setObjectName("spinBoxPort")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.spinBoxPort)
        self.verticalLayout.addWidget(self.groupServer)
        self.groupUser = QtWidgets.QGroupBox(dConnect)
        self.groupUser.setObjectName("groupUser")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupUser)
        self.formLayout_2.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_2.setObjectName("formLayout_2")
        self.labelRole = QtWidgets.QLabel(self.groupUser)
        self.labelRole.setObjectName("labelRole")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.labelRole)
        self.labelName = QtWidgets.QLabel(self.groupUser)
        self.labelName.setObjectName("labelName")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelName)
        self.comboBoxRole = QtWidgets.QComboBox(self.groupUser)
        self.comboBoxRole.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.comboBoxRole.setObjectName("comboBoxRole")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBoxRole)
        self.entryName = QtWidgets.QLineEdit(self.groupUser)
        self.entryName.setMaxLength(20)
        self.entryName.setObjectName("entryName")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.entryName)
        self.verticalLayout.addWidget(self.groupUser)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.frameBottom = QtWidgets.QFrame(dConnect)
        self.frameBottom.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameBottom.setObjectName("frameBottom")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frameBottom)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelStatus = QtWidgets.QLabel(self.frameBottom)
        self.labelStatus.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.labelStatus.setObjectName("labelStatus")
        self.horizontalLayout.addWidget(self.labelStatus)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.buttonConnect = QtWidgets.QPushButton(self.frameBottom)
        icon = QtGui.QIcon.fromTheme("network-connect")
        self.buttonConnect.setIcon(icon)
        self.buttonConnect.setObjectName("buttonConnect")
        self.horizontalLayout.addWidget(self.buttonConnect)
        self.buttonClose = QtWidgets.QToolButton(self.frameBottom)
        self.buttonClose.setText("")
        icon = QtGui.QIcon.fromTheme("window-close")
        self.buttonClose.setIcon(icon)
        self.buttonClose.setObjectName("buttonClose")
        self.horizontalLayout.addWidget(self.buttonClose)
        self.verticalLayout.addWidget(self.frameBottom)
        self.labelAddress.setBuddy(self.entryAddress)
        self.labelPort.setBuddy(self.spinBoxPort)
        self.labelRole.setBuddy(self.comboBoxRole)
        self.labelName.setBuddy(self.entryName)

        self.retranslateUi(dConnect)
        QtCore.QMetaObject.connectSlotsByName(dConnect)
        dConnect.setTabOrder(self.entryAddress, self.spinBoxPort)
        dConnect.setTabOrder(self.spinBoxPort, self.comboBoxRole)
        dConnect.setTabOrder(self.comboBoxRole, self.entryName)
        dConnect.setTabOrder(self.entryName, self.buttonConnect)
        dConnect.setTabOrder(self.buttonConnect, self.buttonClose)
        dConnect.setTabOrder(self.buttonClose, self.toolButtonMenu)

    def retranslateUi(self, dConnect):
        _translate = QtCore.QCoreApplication.translate
        dConnect.setWindowTitle(_translate("dConnect", "Connect to Server"))
        self.groupServer.setTitle(_translate("dConnect", "Server"))
        self.labelAddress.setText(_translate("dConnect", "Address"))
        self.labelPort.setText(_translate("dConnect", "Port"))
        self.groupUser.setTitle(_translate("dConnect", "User"))
        self.labelRole.setText(_translate("dConnect", "Role"))
        self.labelName.setText(_translate("dConnect", "Name"))
        self.entryName.setPlaceholderText(_translate("dConnect", "User name/id"))
        self.buttonConnect.setText(_translate("dConnect", "Connect"))
from . import ectec_res
