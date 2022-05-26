# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'res/server.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dStartServer(object):
    def setupUi(self, dStartServer):
        dStartServer.setObjectName("dStartServer")
        dStartServer.resize(386, 462)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ectec-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dStartServer.setWindowIcon(icon)
        self.vboxlayout = QtWidgets.QVBoxLayout(dStartServer)
        self.vboxlayout.setObjectName("vboxlayout")
        self.frameMenuBar = QtWidgets.QFrame(dStartServer)
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
        icon = QtGui.QIcon.fromTheme("settings-configure")
        self.toolButtonMenu.setIcon(icon)
        self.toolButtonMenu.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.toolButtonMenu.setAutoRaise(True)
        self.toolButtonMenu.setObjectName("toolButtonMenu")
        self.horizontalLayout_2.addWidget(self.toolButtonMenu)
        self.vboxlayout.addWidget(self.frameMenuBar)
        self.frameSettings = QtWidgets.QFrame(dStartServer)
        self.frameSettings.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameSettings.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameSettings.setObjectName("frameSettings")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameSettings)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frameStartConfig = QtWidgets.QFrame(self.frameSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameStartConfig.sizePolicy().hasHeightForWidth())
        self.frameStartConfig.setSizePolicy(sizePolicy)
        self.frameStartConfig.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameStartConfig.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameStartConfig.setObjectName("frameStartConfig")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frameStartConfig)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.frameStartConfig)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.labelAddress = QtWidgets.QLabel(self.frame_3)
        self.labelAddress.setObjectName("labelAddress")
        self.verticalLayout_2.addWidget(self.labelAddress)
        self.comboBoxAddress = QtWidgets.QComboBox(self.frame_3)
        self.comboBoxAddress.setCurrentText("")
        self.comboBoxAddress.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLength)
        self.comboBoxAddress.setMinimumContentsLength(15)
        self.comboBoxAddress.setObjectName("comboBoxAddress")
        self.verticalLayout_2.addWidget(self.comboBoxAddress)
        self.horizontalLayout.addWidget(self.frame_3)
        self.framePort = QtWidgets.QFrame(self.frameStartConfig)
        self.framePort.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.framePort.setFrameShadow(QtWidgets.QFrame.Plain)
        self.framePort.setObjectName("framePort")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.framePort)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labelPort = QtWidgets.QLabel(self.framePort)
        self.labelPort.setObjectName("labelPort")
        self.verticalLayout_3.addWidget(self.labelPort)
        self.spinBoxPort = QtWidgets.QSpinBox(self.framePort)
        self.spinBoxPort.setMaximum(60000)
        self.spinBoxPort.setProperty("value", 50234)
        self.spinBoxPort.setObjectName("spinBoxPort")
        self.verticalLayout_3.addWidget(self.spinBoxPort)
        self.horizontalLayout.addWidget(self.framePort)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonStart = QtWidgets.QPushButton(self.frameStartConfig)
        self.buttonStart.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonStart.setDefault(True)
        self.buttonStart.setFlat(False)
        self.buttonStart.setObjectName("buttonStart")
        self.horizontalLayout.addWidget(self.buttonStart)
        self.verticalLayout.addWidget(self.frameStartConfig)
        self.frameRunningConfig = QtWidgets.QFrame(self.frameSettings)
        self.frameRunningConfig.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameRunningConfig.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameRunningConfig.setObjectName("frameRunningConfig")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frameRunningConfig)
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkBoxBlocking = QtWidgets.QCheckBox(self.frameRunningConfig)
        self.checkBoxBlocking.setObjectName("checkBoxBlocking")
        self.horizontalLayout_3.addWidget(self.checkBoxBlocking)
        self.verticalLayout.addWidget(self.frameRunningConfig)
        self.vboxlayout.addWidget(self.frameSettings)
        self.tableClients = QtWidgets.QTableView(dStartServer)
        self.tableClients.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tableClients.sizePolicy().hasHeightForWidth())
        self.tableClients.setSizePolicy(sizePolicy)
        self.tableClients.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableClients.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tableClients.setMidLineWidth(1)
        self.tableClients.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked)
        self.tableClients.setDragDropOverwriteMode(False)
        self.tableClients.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableClients.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableClients.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableClients.setGridStyle(QtCore.Qt.DashLine)
        self.tableClients.setSortingEnabled(True)
        self.tableClients.setCornerButtonEnabled(False)
        self.tableClients.setObjectName("tableClients")
        self.tableClients.horizontalHeader().setCascadingSectionResizes(True)
        self.tableClients.horizontalHeader().setSortIndicatorShown(True)
        self.tableClients.horizontalHeader().setStretchLastSection(True)
        self.tableClients.verticalHeader().setVisible(False)
        self.vboxlayout.addWidget(self.tableClients)
        self.labelAddress.setBuddy(self.comboBoxAddress)
        self.labelPort.setBuddy(self.spinBoxPort)

        self.retranslateUi(dStartServer)
        self.comboBoxAddress.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(dStartServer)
        dStartServer.setTabOrder(self.comboBoxAddress, self.spinBoxPort)
        dStartServer.setTabOrder(self.spinBoxPort, self.buttonStart)
        dStartServer.setTabOrder(self.buttonStart, self.tableClients)

    def retranslateUi(self, dStartServer):
        _translate = QtCore.QCoreApplication.translate
        dStartServer.setWindowTitle(_translate("dStartServer", "Start Server"))
        self.toolButtonMenu.setToolTip(_translate("dStartServer", "<html><head/><body><p>Menu</p></body></html>"))
        self.labelAddress.setText(_translate("dStartServer", "Local Address", "IP"))
        self.comboBoxAddress.setToolTip(_translate("dStartServer", "<html><head/><body><p>The address to start the server on.</p></body></html>"))
        self.labelPort.setText(_translate("dStartServer", "Port", "socket"))
        self.spinBoxPort.setToolTip(_translate("dStartServer", "<html><head/><body><p>The port (TCP) to start the sever on.</p></body></html>"))
        self.buttonStart.setToolTip(_translate("dStartServer", "<html><head/><body><p>Start the server.</p></body></html>"))
        self.buttonStart.setText(_translate("dStartServer", "Start", "verb"))
        self.checkBoxBlocking.setText(_translate("dStartServer", "Reject new clients."))
        self.tableClients.setToolTip(_translate("dStartServer", "<html><head/><body><p>List of connected clients.</p></body></html>"))
from . import ectec_res
