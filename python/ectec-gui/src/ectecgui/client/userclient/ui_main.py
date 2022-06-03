# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'res/clientUser.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dUserClient(object):
    def setupUi(self, dUserClient):
        dUserClient.setObjectName("dUserClient")
        dUserClient.resize(789, 600)
        dUserClient.setWindowTitle("Ectec User Client")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ectec-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dUserClient.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(dUserClient)
        self.verticalLayout.setSpacing(18)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frameMenuBar = QtWidgets.QFrame(dUserClient)
        self.frameMenuBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMenuBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMenuBar.setObjectName("frameMenuBar")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frameMenuBar)
        self.horizontalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_2.setSpacing(12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frameLocalInfo = QtWidgets.QFrame(self.frameMenuBar)
        self.frameLocalInfo.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameLocalInfo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameLocalInfo.setObjectName("frameLocalInfo")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frameLocalInfo)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.labelClient = QtWidgets.QLabel(self.frameLocalInfo)
        self.labelClient.setObjectName("labelClient")
        self.horizontalLayout_4.addWidget(self.labelClient)
        self.labelClientAddress = QtWidgets.QLabel(self.frameLocalInfo)
        self.labelClientAddress.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelClientAddress.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelClientAddress.setText("127.0.0.1")
        self.labelClientAddress.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelClientAddress.setObjectName("labelClientAddress")
        self.horizontalLayout_4.addWidget(self.labelClientAddress)
        self.labelClientName = QtWidgets.QLabel(self.frameLocalInfo)
        self.labelClientName.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelClientName.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelClientName.setText("user1")
        self.labelClientName.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelClientName.setObjectName("labelClientName")
        self.horizontalLayout_4.addWidget(self.labelClientName)
        self.horizontalLayout_2.addWidget(self.frameLocalInfo)
        self.line_2 = QtWidgets.QFrame(self.frameMenuBar)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_2.addWidget(self.line_2)
        self.frameServerInfo = QtWidgets.QFrame(self.frameMenuBar)
        self.frameServerInfo.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameServerInfo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameServerInfo.setObjectName("frameServerInfo")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frameServerInfo)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelServer = QtWidgets.QLabel(self.frameServerInfo)
        self.labelServer.setObjectName("labelServer")
        self.horizontalLayout_3.addWidget(self.labelServer)
        self.labelServerAddress = QtWidgets.QLabel(self.frameServerInfo)
        self.labelServerAddress.setEnabled(True)
        self.labelServerAddress.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelServerAddress.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelServerAddress.setText("197.12.45.23")
        self.labelServerAddress.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelServerAddress.setObjectName("labelServerAddress")
        self.horizontalLayout_3.addWidget(self.labelServerAddress)
        self.labelServerPort = QtWidgets.QLabel(self.frameServerInfo)
        self.labelServerPort.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelServerPort.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelServerPort.setText("50000")
        self.labelServerPort.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelServerPort.setObjectName("labelServerPort")
        self.horizontalLayout_3.addWidget(self.labelServerPort)
        self.horizontalLayout_2.addWidget(self.frameServerInfo)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.buttonDisconnect = QtWidgets.QPushButton(self.frameMenuBar)
        icon = QtGui.QIcon.fromTheme("network-disconnect")
        self.buttonDisconnect.setIcon(icon)
        self.buttonDisconnect.setAutoDefault(False)
        self.buttonDisconnect.setObjectName("buttonDisconnect")
        self.horizontalLayout_2.addWidget(self.buttonDisconnect)
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
        self.verticalLayout.addWidget(self.frameMenuBar)
        self.splitterMain = QtWidgets.QSplitter(dUserClient)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitterMain.sizePolicy().hasHeightForWidth())
        self.splitterMain.setSizePolicy(sizePolicy)
        self.splitterMain.setOrientation(QtCore.Qt.Horizontal)
        self.splitterMain.setHandleWidth(12)
        self.splitterMain.setChildrenCollapsible(False)
        self.splitterMain.setObjectName("splitterMain")
        self.frameWrite = QtWidgets.QFrame(self.splitterMain)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameWrite.sizePolicy().hasHeightForWidth())
        self.frameWrite.setSizePolicy(sizePolicy)
        self.frameWrite.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameWrite.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameWrite.setObjectName("frameWrite")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frameWrite)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.framePackageMeta = QtWidgets.QFrame(self.frameWrite)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.framePackageMeta.sizePolicy().hasHeightForWidth())
        self.framePackageMeta.setSizePolicy(sizePolicy)
        self.framePackageMeta.setObjectName("framePackageMeta")
        self.formLayout = QtWidgets.QFormLayout(self.framePackageMeta)
        self.formLayout.setContentsMargins(6, 6, 6, 6)
        self.formLayout.setObjectName("formLayout")
        self.labelTo = QtWidgets.QLabel(self.framePackageMeta)
        self.labelTo.setObjectName("labelTo")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.labelTo)
        self.labelFrom = QtWidgets.QLabel(self.framePackageMeta)
        self.labelFrom.setObjectName("labelFrom")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labelFrom)
        self.comboBoxFrom = QtWidgets.QComboBox(self.framePackageMeta)
        self.comboBoxFrom.setEditable(True)
        self.comboBoxFrom.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.comboBoxFrom.setObjectName("comboBoxFrom")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBoxFrom)
        self.comboBoxTo = QtWidgets.QComboBox(self.framePackageMeta)
        self.comboBoxTo.setEditable(True)
        self.comboBoxTo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.comboBoxTo.setObjectName("comboBoxTo")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBoxTo)
        self.verticalLayout_2.addWidget(self.framePackageMeta)
        self.textEditContent = QtWidgets.QTextEdit(self.frameWrite)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEditContent.sizePolicy().hasHeightForWidth())
        self.textEditContent.setSizePolicy(sizePolicy)
        self.textEditContent.setAcceptRichText(False)
        self.textEditContent.setObjectName("textEditContent")
        self.verticalLayout_2.addWidget(self.textEditContent)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonSend = QtWidgets.QPushButton(self.frameWrite)
        icon = QtGui.QIcon.fromTheme("document-send")
        self.buttonSend.setIcon(icon)
        self.buttonSend.setObjectName("buttonSend")
        self.horizontalLayout.addWidget(self.buttonSend)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.chatView = QtWidgets.QListView(self.splitterMain)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatView.sizePolicy().hasHeightForWidth())
        self.chatView.setSizePolicy(sizePolicy)
        self.chatView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chatView.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chatView.setObjectName("chatView")
        self.verticalLayout.addWidget(self.splitterMain)
        self.labelTo.setBuddy(self.comboBoxTo)
        self.labelFrom.setBuddy(self.comboBoxFrom)

        self.retranslateUi(dUserClient)
        QtCore.QMetaObject.connectSlotsByName(dUserClient)
        dUserClient.setTabOrder(self.buttonDisconnect, self.comboBoxFrom)
        dUserClient.setTabOrder(self.comboBoxFrom, self.comboBoxTo)
        dUserClient.setTabOrder(self.comboBoxTo, self.textEditContent)
        dUserClient.setTabOrder(self.textEditContent, self.buttonSend)
        dUserClient.setTabOrder(self.buttonSend, self.chatView)
        dUserClient.setTabOrder(self.chatView, self.toolButtonMenu)

    def retranslateUi(self, dUserClient):
        _translate = QtCore.QCoreApplication.translate
        self.labelClient.setText(_translate("dUserClient", "<html><head/><body><p><span style=\" font-style:italic;\">Local client</span></p></body></html>"))
        self.labelServer.setText(_translate("dUserClient", "<html><head/><body><p><span style=\" font-style:italic;\">Server</span></p></body></html>"))
        self.buttonDisconnect.setText(_translate("dUserClient", "Disconnect"))
        self.toolButtonMenu.setToolTip(_translate("dUserClient", "Menu"))
        self.labelTo.setText(_translate("dUserClient", "To:"))
        self.labelFrom.setText(_translate("dUserClient", "From:"))
        self.buttonSend.setText(_translate("dUserClient", "Send"))
from . import ectec_res
