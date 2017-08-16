# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutqt.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(452, 144)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setOpenExternalLinks(True)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setOpenExternalLinks(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setOpenExternalLinks(True)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Über Qt"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p>Dieses Programm verwendet Qt5 unter <a href=\"https://www.qt.io/qt-licensing-terms/\"><span style=\" text-decoration: underline; color:#0000ff;\">GNU LGPL v3</span></a></p></body></html>"))
        self.label_5.setText(_translate("Dialog", "<html><head/><body><p>Website: <a href=\"https:/qt.io\"><span style=\" text-decoration: underline; color:#0000ff;\">www.qt.io</span></a></p></body></html>"))
        self.label_6.setText(_translate("Dialog", "<html><head/><body><p>Qt Licensing: <a href=\"https:/qt.io/licensing/\"><span style=\" text-decoration: underline; color:#0000ff;\">www.qt.io/licensing/</span></a></p></body></html>"))
        self.label_7.setText(_translate("Dialog", "<html><head/><body><p>Third-Party Licenses Used in Qt: <a href=\"http://doc.qt.io/qt-5.6/3rdparty.html\"><span style=\" text-decoration: underline; color:#0000ff;\">www.doc.qt.io/qt-5.6/3rdparty.html</span></a></p></body></html>"))

