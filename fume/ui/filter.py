# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filter.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_filter(object):
    def setupUi(self, filter):
        filter.setObjectName("filter")
        filter.resize(381, 435)
        self.gridLayout = QtWidgets.QGridLayout(filter)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(filter)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(filter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(filter)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(filter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(filter)
        self.lineEdit.setInputMask("")
        self.lineEdit.setPlaceholderText("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.checkBox = QtWidgets.QCheckBox(filter)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.label_2.raise_()
        self.listWidget.raise_()
        self.buttonBox.raise_()
        self.label.raise_()

        self.retranslateUi(filter)
        self.buttonBox.accepted.connect(filter.accept)
        self.buttonBox.rejected.connect(filter.reject)
        QtCore.QMetaObject.connectSlotsByName(filter)

    def retranslateUi(self, filter):
        _translate = QtCore.QCoreApplication.translate
        filter.setWindowTitle(_translate("filter", "Filter bearbeiten"))
        self.label_2.setText(_translate("filter", "Markiere alle Mannschaften, die hinzugefügt werden sollen"))
        self.label.setText(_translate("filter", "Suche:"))
        self.checkBox.setText(_translate("filter", "markiert"))

