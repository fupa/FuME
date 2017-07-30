# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Log(object):
    def setupUi(self, Log):
        Log.setObjectName("Log")
        Log.resize(631, 264)
        self.gridLayout = QtWidgets.QGridLayout(Log)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Log)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(11)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setPlainText("")
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Log)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 0, 1, 1, 1)

        self.retranslateUi(Log)
        self.buttonBox.accepted.connect(Log.accept)
        self.buttonBox.rejected.connect(Log.reject)
        QtCore.QMetaObject.connectSlotsByName(Log)

    def retranslateUi(self, Log):
        _translate = QtCore.QCoreApplication.translate
        Log.setWindowTitle(_translate("Log", "Log"))

