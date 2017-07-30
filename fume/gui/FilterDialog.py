#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtSql
from PyQt5 import QtWidgets

from fume.ui.filter import Ui_filter


class FilterDialog(QtWidgets.QDialog, Ui_filter):
    def __init__(self, parent=None):
        super(FilterDialog, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)

        self.settings = QtCore.QSettings('fume', 'Match-Explorer')

        self.region = self.parent().comboBox.currentText()
        self.lineEdit.setPlaceholderText("Region: " + self.region)

        self.set_listModel()
        self.set_listWidget()
        self.set_connections()

    def set_listModel(self):
        self.listmodel = QtSql.QSqlQueryModel()
        self.listmodel.setQuery("""
        select home from calendar
        WHERE region = "%s"
        UNION
        select home from team_default
        WHERE region = "%s"
        Order By home ASC
        """ % (self.region,self.region), self.parent().db)

        # Fetching all teams from db
        # adapted: http://stackoverflow.com/a/27393939/6304901
        while self.listmodel.canFetchMore():
            self.listmodel.fetchMore()

    def set_listWidget(self):
        # Adding all teams from region to listWidget
        for i in range(0, self.listmodel.rowCount()):
            item = QtWidgets.QListWidgetItem()
            item.setText(self.listmodel.record(i).value('home'))
            item.setData(QtCore.Qt.UserRole, self.region)
            self.listWidget.addItem(item)

        # Selecting teams from parent listwidget
        for i in range(self.parent().listWidget.count()):
            for j in self.listWidget.findItems(self.parent().listWidget.item(i).text(), QtCore.Qt.MatchExactly):
                j.setSelected(True)

    def set_connections(self):
        self.lineEdit.textChanged.connect(self.lineEdit_changed)
        self.checkBox.stateChanged.connect(self.checkBox_changed)
        self.buttonBox.accepted.connect(self.ButtonAccepted)

    def hideAll(self):
        for i in range(0, self.listWidget.count()):
            self.listWidget.item(i).setHidden(True)

    def showAll(self):
        for i in range(0, self.listWidget.count()):
            self.listWidget.item(i).setHidden(False)

    @QtCore.pyqtSlot(str)
    def lineEdit_changed(self, text):
        # adapted: http://stackoverflow.com/a/32336368/6304901
        self.hideAll()
        for i in self.listWidget.findItems(text, QtCore.Qt.MatchContains):
            if self.checkBox.isChecked():
                if i in self.listWidget.selectedItems():
                    i.setHidden(False)
            else:
                i.setHidden(False)

    @QtCore.pyqtSlot(int)
    def checkBox_changed(self, int):
        if int:  # 1: checkBox checked
            self.hideAll()
            for i in self.listWidget.selectedItems():
                i.setHidden(False)
        else:
            self.showAll()

        self.lineEdit_changed(self.lineEdit.text())

    @QtCore.pyqtSlot()
    def ButtonAccepted(self):
        parentListWidget = self.parent().listWidget

        # adding new elements and restore selected teams
        restoredSelection = parentListWidget.selectedItems()

        # removing all elements from current region so that we can add all new ones withount duplicates
        items = [parentListWidget.item(i) for i in range(parentListWidget.count())]
        for i in items:
            if not i.isHidden():
                parentListWidget.takeItem(i.listWidget().row(i))

        # adding selected teams
        for i in self.listWidget.selectedItems():
            item = QtWidgets.QListWidgetItem()
            item.setText(i.text())
            item.setData(QtCore.Qt.UserRole, i.data(QtCore.Qt.UserRole))
            parentListWidget.addItem(item)

        parentListWidget.sortItems()

        for i in restoredSelection:
            for j in parentListWidget.findItems(i.text(), QtCore.Qt.MatchExactly):
                j.setSelected(True)
