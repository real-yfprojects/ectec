# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'res/error.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dErrorDialog(object):
    def setupUi(self, dErrorDialog):
        dErrorDialog.setObjectName("dErrorDialog")
        dErrorDialog.resize(406, 546)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(dErrorDialog)
        self.verticalLayout_2.setSpacing(12)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.lError = QtWidgets.QLabel(dErrorDialog)
        self.lError.setText("<html><head/><body><h3>AttributeError:\n"
"                  \'int\' object has no attribute \'b\'</h3></body></html>")
        self.lError.setObjectName("lError")
        self.verticalLayout_4.addWidget(self.lError)
        self.lDescription = QtWidgets.QLabel(dErrorDialog)
        self.lDescription.setText("An error occured. Please proceed with reporting it, so that we have the opportunity to fix it.")
        self.lDescription.setWordWrap(True)
        self.lDescription.setObjectName("lDescription")
        self.verticalLayout_4.addWidget(self.lDescription)
        self.verticalLayout_2.addLayout(self.verticalLayout_4)
        self.fTraceback = QtWidgets.QFrame(dErrorDialog)
        self.fTraceback.setObjectName("fTraceback")
        self.vboxlayout = QtWidgets.QVBoxLayout(self.fTraceback)
        self.vboxlayout.setContentsMargins(0, 0, 0, 0)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName("vboxlayout")
        self.tracebackView = QtWidgets.QTextEdit(self.fTraceback)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tracebackView.sizePolicy().hasHeightForWidth())
        self.tracebackView.setSizePolicy(sizePolicy)
        self.tracebackView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tracebackView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tracebackView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tracebackView.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.tracebackView.setReadOnly(True)
        self.tracebackView.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                    </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Traceback (most                    recent call last):                    </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> File                    &quot;&lt;string&gt;&quot;, line 1, in                    &lt;module&gt;                    </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">AttributeError:                    \'int\' object has no attribute \'b\'</p></body></html>")
        self.tracebackView.setObjectName("tracebackView")
        self.vboxlayout.addWidget(self.tracebackView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.bCopyTraceback = QtWidgets.QToolButton(self.fTraceback)
        self.bCopyTraceback.setText("")
        icon = QtGui.QIcon.fromTheme("edit-copy")
        self.bCopyTraceback.setIcon(icon)
        self.bCopyTraceback.setObjectName("bCopyTraceback")
        self.horizontalLayout.addWidget(self.bCopyTraceback)
        self.vboxlayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.fTraceback)
        self.fLogs = QtWidgets.QFrame(dErrorDialog)
        self.fLogs.setObjectName("fLogs")
        self._2 = QtWidgets.QVBoxLayout(self.fLogs)
        self._2.setContentsMargins(0, 0, 0, 0)
        self._2.setSpacing(4)
        self._2.setObjectName("_2")
        self.lLogs = QtWidgets.QLabel(self.fLogs)
        self.lLogs.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.lLogs.setObjectName("lLogs")
        self._2.addWidget(self.lLogs)
        self.logView = QtWidgets.QTextEdit(self.fLogs)
        font = QtGui.QFont()
        font.setKerning(False)
        self.logView.setFont(font)
        self.logView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.logView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.logView.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.logView.setReadOnly(True)
        self.logView.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                  </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">2023-02-19 15:00:19,638 DEBUG                  Server[ectecgui] Loaded translation de for [\'en-GB\', \'de\',                  \'en-US\'].</span>                  </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">2023-02-19 15:00:22,365 INFO                  Server[ectecgui.server.window] Start server on (192.168.178.36,                  50234).</span>                  </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">2023-02-19 15:00:24,369 INFO                  Server[ectecgui.server.window] Stopped server.</span>                  </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">2023-02-19 15:00:28,102 DEBUG                  Server[ectecgui.server.window] App closed.</span>                  </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>")
        self.logView.setObjectName("logView")
        self._2.addWidget(self.logView)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.bCopyLogs = QtWidgets.QToolButton(self.fLogs)
        self.bCopyLogs.setText("")
        icon = QtGui.QIcon.fromTheme("edit-copy")
        self.bCopyLogs.setIcon(icon)
        self.bCopyLogs.setObjectName("bCopyLogs")
        self.horizontalLayout_2.addWidget(self.bCopyLogs)
        self._2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.fLogs)
        spacerItem2 = QtWidgets.QSpacerItem(0, 8, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.buttonBox = QtWidgets.QDialogButtonBox(dErrorDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ignore|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_2.setStretch(2, 1)

        self.retranslateUi(dErrorDialog)
        QtCore.QMetaObject.connectSlotsByName(dErrorDialog)

    def retranslateUi(self, dErrorDialog):
        _translate = QtCore.QCoreApplication.translate
        dErrorDialog.setWindowTitle(_translate("dErrorDialog", "Form"))
        self.lLogs.setText(_translate("dErrorDialog", "<h4>Logs:</h4>"))
