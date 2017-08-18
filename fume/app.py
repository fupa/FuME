#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# --------------------------------------------------------------------------
# FuME FuPa Match Explorer Copyright (c) 2017 Andreas Feldl <fume@afeldl.de>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# The full license of the GNU General Public License is in the file LICENCE,
# distributed with this software; if not, see http://www.gnu.org/licenses/.
# --------------------------------------------------------------------------

import datetime
import os
import shutil
import sys

import appdirs
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtSql
from PyQt5 import QtWidgets

from fume.gui.AboutDialog import AboutDialog
from fume.gui.AboutQtDialog import AboutQtDialog
from fume.gui.FilterDialog import FilterDialog
from fume.gui.LogDialog import LogDialog
from fume.gui.SettingsDialog import SettingsDialog
from fume.gui.UpdateDialog import UpdateDialog
from fume.threads.ChromeDriverProcessor import ChromeDriverProcessor
from fume.threads.DownloadProcessor import DownloadProcessor
from fume.threads.ReserveProcessor import ReserveProcessor
from fume.threads.UpdateProcessor import UpdateProcessor
from fume.ui.mainwindow import Ui_MainWindow

version = '1.1'


class CustomSqlModel(QtSql.QSqlQueryModel):
    # adapted: https://stackoverflow.com/a/44104745
    def __init__(self, parent=None):
        QtSql.QSqlQueryModel.__init__(self, parent=parent)
        self.defaultFilter = 'select * from calendar'
        self.setQuery(self.defaultFilter)

    def data(self, item, role):
        # Changing color if "reserved" is True
        if role == QtCore.Qt.BackgroundRole:
            if QtSql.QSqlQueryModel.data(self, self.index(item.row(), 7), QtCore.Qt.DisplayRole) == 1:
                return QtGui.QBrush(QtGui.QColor.fromRgb(176, 234, 153))
            if QtSql.QSqlQueryModel.data(self, self.index(item.row(), 7), QtCore.Qt.DisplayRole) == 2:
                return QtGui.QBrush(QtGui.QColor.fromRgb(234, 189, 190))

        # Changing value 0=False, 1=True - deprecated
        # if role == QtCore.Qt.DisplayRole:
        #     if item.column() == 7:
        #         if QtSql.QSqlQueryModel.data(self, item, QtCore.Qt.DisplayRole) == 1:
        #             return True
        #         else:
        #             return False

        return QtSql.QSqlQueryModel.data(self, item, role)

    def setFilter(self, text):
        self.setQuery(self.defaultFilter + ' WHERE ' + text + ' order by match_date asc')

    def select(self):
        queryStr = self.query().executedQuery()
        self.query().clear()
        self.setQuery(queryStr)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.set_statusBar()
        self.read_settings()

        if sys.platform == "win32":
            self.setWindowIcon(QtGui.QIcon(self.get_pathToTemp(['bin', 'icon.ico'])))
        self.header = self.get_pathToTemp(["bin", "header_klein.png"])
        self.label.setPixmap(QtGui.QPixmap(self.header))

        self.logDialog = LogDialog(self)
        self.settingsDialog = SettingsDialog(self)
        self.aboutDialog = AboutDialog(path=self.header, version=version, parent=self)
        self.aboutQtDialog = AboutQtDialog(self)

        if not self.set_database():
            sys.exit(1)

        self.set_menuBar()
        self.set_chromeDriver()
        self.set_connections()
        self.set_tableStyleSheet()
        self.set_tableView()

        self.matchFilterString = ''
        self.regionFilterString = ''
        self.dateFilterString = ''
        self.resFilterString = ''

        self.set_comboBoxItems()
        self.date_changed()  # set date-range
        self.set_listWidget()
        self.comboBox_changed()  # set region
        self.datePeriodMenu_changed()
        self.viewMenu_changed()

        if not self.settings.value('updates/noautoupdate', False, bool):
            self.checkForUpdates(active=False)

        self.tableView.hideColumn(7)
        self.tableView.hideColumn(8)

        # widths = [72, 220, 125, 220, 220, 60, 140]
        # for i, d in enumerate(widths):
        #     self.tableView.setColumnWidth(i, d)
        self.tableView.resizeColumnsToContents()

        # Fixes "Error": (from https://stackoverflow.com/a/39311662/6304901)
        # QBasicTimer::start: QBasicTimer can only be used with threads started with QThread
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.show()

    def set_statusBar(self):
        self.statusBar.showMessage("Willkommen!")

        # Permanent labels
        self.statusBarLabel_1 = QtWidgets.QLabel(self.statusBar)
        self.statusBar.addPermanentWidget(self.statusBarLabel_1)

    def set_menuBar(self):
        self.actionUeber.triggered.connect(self.aboutDialog.show)
        self.action_ber_QT.triggered.connect(self.aboutQtDialog.show)
        self.actionEinstellungen.triggered.connect(self.settingsDialog.show)
        self.actionLog.triggered.connect(self.logDialog.show)
        self.actionBeenden.triggered.connect(self.close)
        self.actionHeute.triggered.connect(self.set_timeEditNow)
        self.actionAuf_Update_berpr_fen.triggered.connect(self.checkForUpdates)
        self.actionImportieren.triggered.connect(self.download_match)
        self.actionHinzuf_gen_reservieren.triggered.connect(self.reserve_match)
        self.actionL_schen.triggered.connect(self.deleteReservation)

        dateRangeGroup = QtWidgets.QActionGroup(self)
        dateRangeGroup.addAction(self.actionZeitpunkt)
        dateRangeGroup.addAction(self.actionZeitraum)
        dateRangeGroup.triggered.connect(self.datePeriodMenu_changed)

        viewGroup = QtWidgets.QActionGroup(self)
        viewGroup.addAction(self.actionAnsichtSpiele)
        viewGroup.addAction(self.actionAnsichtReservierungen)
        viewGroup.triggered.connect(self.viewMenu_changed)

    def set_connections(self):
        # Push Buttons
        self.pushButton_5.clicked.connect(self.download_match)
        self.pushButton_11.clicked.connect(self.reserve_match)

        # Command Link Buttons
        base = self.get_pathToTemp(['bin', 'buttons'], True)
        buttons = [self.commandLinkButton, self.commandLinkButton_2, self.commandLinkButton_3, self.commandLinkButton_4,
                   self.commandLinkButton_5]
        images = ['add-button-inside-black-circle', 'rounded-remove-button',
                  'rounded-adjust-button-with-plus-and-minus', 'cancel-button', 'swap-vertical-orientation-arrows']
        connections = [self.showFilterDialog, self.removeSelectedItems, self.invertSelection, self.resetSelection,
                       self.restoreSelection]
        tooltips = ["Mannschaften hinzufügen", "Ausgewählte Mannschaften entfernen", "Auswahl umkehren",
                    "Auswahl löschen",
                    "Auswahl zurücksetzen"]

        for button, image, connection, tooltip in zip(buttons, images, connections, tooltips):
            button.setIcon(QtGui.QIcon(""))  # removing default image set by QtDesigner
            button.setMaximumSize(21, 21)
            button.setStyleSheet(
                "QPushButton {{border-image: url({base}/{image}.png);}}"
                "QPushButton:hover {{border-image: url({base}/{image}_hover.png);}}".format(base=base, image=image)
            )
            button.clicked.connect(connection)
            button.setToolTip(tooltip)

        self.commandLinkButton_5.setVisible(False)  # currently not working properly

        # Other
        self.dateEdit_3.dateChanged.connect(self.date_changed)
        self.dateEdit_4.dateChanged.connect(self.date_changed)
        self.lineEdit.textChanged.connect(self.lineEdit_changed)
        self.listWidget.itemSelectionChanged.connect(self.itemSelection_changed)
        self.checkBox_2.stateChanged.connect(self.checkBox_changed)
        self.comboBox.currentTextChanged.connect(self.comboBox_changed)

    def set_database(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.dbPath)

        if not self.db.open():
            QtWidgets.QMessageBox.critical(None, QtWidgets.qApp.tr("Datenbank nicht verfügbar"),
                                           QtWidgets.qApp.tr(
                                               "Es konnte keine Verbindung zur Datenbank hergestellt werden.\n"
                                               "Dieses Programm benötigt SQLite support. Bitte lesen Sie "
                                               "die Qt SQL Treiber Dokumentation für mehr Informationen\n\n"
                                               "Klicke Abbrechen zum beenden."),
                                           QtWidgets.QMessageBox.Cancel)
            return False
        else:
            return True

    def set_tableStyleSheet(self):
        self.tableViewStyle = """
                                QTableView
                                {
                                    background-color: white;
                                    gridline-color: #545454;
                                    color: black;
                                    alternate-background-color: #eeeeee;
                                }
                                """
        self.setStyleSheet(self.tableViewStyle)

    def set_tableView(self):
        self.sqlmodel_calendar = CustomSqlModel()
        labels = ['ID', 'Liga', 'Datum/Uhrzeit', 'Heim', 'Gast', 'Tore', 'Region']
        for i in range(len(labels)):
            self.sqlmodel_calendar.setHeaderData(i, QtCore.Qt.Horizontal, labels[i])

        self.tableView.setModel(self.sqlmodel_calendar)
        # self.tableView_2.resizeColumnsToContents()
        self.tableView.setAlternatingRowColors(True)

    def set_comboBoxItems(self):
        # 18.05.2017
        items = ['Alle', 'Baden', 'Bayliga', 'Berlin', 'Brandenburg', 'Darmstadt', 'Hamburg', 'Lueneburg', 'Luxemburg',
                 'Mecklenburg-Vorpommern', 'Mittelbaden', 'Mittelfranken', 'Mittelhessen', 'Mittelrhein', 'Nahe',
                 'Niederbayern', 'Niederrhein', 'Nordhessen', 'Nordwest', 'Oberbayern', 'Oberfranken', 'Oberpfalz',
                 'Oberschwaben', 'Ostwestfalen', 'Rheinhessen', 'Rheinland', 'Ruhrgebiet', 'Saarland', 'Sachsen',
                 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Schwaben', 'Stuttgart', 'Suedbaden', 'Suedwest',
                 'Suedwestfalen', 'Thueringen', 'Weser-Ems', 'Westpfalz', 'Westrhein', 'Wiesbaden']
        self.comboBox.addItems(items)
        self.comboBox.setCurrentText(self.settings.value('region', 'Alle'))
        # self.comboBox.setItemData(self.comboBox.currentIndex(), QtGui.QColor.fromRgb(176, 234, 153), QtCore.Qt.ForegroundRole)

    def set_listWidget(self):
        # Sets the default values if the fume is closed without any elements in listWidget
        # Important: These values are preset and defined in .ui file
        defaults = ['Noch keine Mannschaften hinzugefügt...', 'Region wählen und unten auf "+" klicken']
        elements = self.settings.value('filter', defaults)
        if elements != defaults and len(elements) != 0:
            self.listWidget.clear()
            for i in elements:
                item = QtWidgets.QListWidgetItem()
                item.setText(i[0])
                item.setData(QtCore.Qt.UserRole, i[1])
                self.listWidget.addItem(item)

        # Loading selected items
        for i in self.settings.value('filter_calendar', []):
            for j in self.listWidget.findItems(i, QtCore.Qt.MatchExactly):
                j.setSelected(True)

        self.itemSelection_changed()
        self.current_selection = [x for x in self.listWidget.selectedItems()]  # for restoring selection

    def set_timeEditNow(self):
        now = datetime.datetime.now()
        self.dateEdit_3.setDate(QtCore.QDate(now.year, now.month, now.day))
        self.dateEdit_4.setDate(QtCore.QDate(now.year, now.month, now.day))

    def get_filterString(self):
        # Only join not empty filter strings
        str = ' AND '.join(filter(None, [self.dateFilterString, self.matchFilterString, self.regionFilterString,
                                         self.resFilterString]))
        # print(str)
        return str

    def get_pathToTemp(self, relative_path, css=False):
        # relative_path is a List or Array
        # set css to True if used for .setStyleSheet so '/' is set as separator instead of '\\'
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        if css and sys.platform == "win32":
            # Fixes "could not parse stylesheet of object ..." thrown by .setStyleSheet
            return os.path.join(base_path, *relative_path).replace("\\", "/")

        return os.path.join(base_path, *relative_path)

    def get_selectedMatches(self):
        selected = []
        indexes = self.tableView.selectedIndexes()

        if indexes == []:
            QtWidgets.QMessageBox.information(self, QtWidgets.qApp.tr("Keine Spiele ausgewählt"),
                                              QtWidgets.qApp.tr("Du hast kein Spiel ausgewählt.\n\n"
                                                                "Bitte markiere ein oder mehrere Zeilen "
                                                                "in der Spielübersicht und probiere es erneut."),
                                              QtWidgets.QMessageBox.Ok)
            return None
        else:
            for index in sorted(indexes):
                match_id = self.tableView.model().record(index.row()).value('match_id')
                match_date = self.tableView.model().record(index.row()).value('match_date')
                home = self.tableView.model().record(index.row()).value('home')
                guest = self.tableView.model().record(index.row()).value('guest')
                selected.append({'match_id': match_id, 'match_date': match_date, 'home': home, 'guest': guest})
            return selected

    def get_cookies(self):
        cookies = self.settings.value('cookie', '')
        if cookies == '':
            QtWidgets.QMessageBox.information(self, QtWidgets.qApp.tr("Cookies"),
                                              QtWidgets.qApp.tr("Keine Cookies vorhanden.\n\n"
                                                                "Erstelle jetzt deine Cookies in den Einstellungen"),
                                              QtWidgets.QMessageBox.Ok)
            return None
        else:
            return cookies

    def hideAll(self):
        for i in range(0, self.listWidget.count()):
            self.listWidget.item(i).setHidden(True)

    def showAll(self):
        for i in range(0, self.listWidget.count()):
            self.listWidget.item(i).setHidden(False)

    def write_settings(self):
        # $HOME/Library/Preferences/com.fume.Match-Explorer.plist
        self.settings.setValue('mainwindow/size', self.size())
        self.settings.setValue('mainwindow/pos', self.pos())

        self.settings.setValue('menubar/date/range', self.actionZeitraum.isChecked())
        self.settings.setValue('menubar/date/day', self.actionZeitpunkt.isChecked())

        self.settings.setValue('date_from_calendar', self.dateEdit_3.date())
        self.settings.setValue('date_to_calendar', self.dateEdit_4.date())
        self.settings.setValue('filter_calendar', [x.text() for x in self.listWidget.selectedItems()])
        self.settings.setValue('region', self.comboBox.currentText())
        self.settings.setValue('filter', [[self.listWidget.item(i).text(),
                                           self.listWidget.item(i).data(QtCore.Qt.UserRole)]
                                          for i in range(self.listWidget.count())])

    def read_settings(self):
        self.settings = QtCore.QSettings('fume', 'Match-Explorer')

        self.resize(self.settings.value('mainwindow/size', self.size()))
        try:
            self.move(self.settings.value('mainwindow/pos'))
        except:
            pass

        self.actionZeitraum.setChecked(self.settings.value('menubar/date/range', True, type=bool))
        self.actionZeitpunkt.setChecked(self.settings.value('menubar/date/day', False, type=bool))

        now = datetime.datetime.now()
        self.dateEdit_3.setDate(self.settings.value('date_from_calendar', QtCore.QDate(now.year, now.month, now.day)))
        self.dateEdit_4.setDate(self.settings.value('date_to_calendar', QtCore.QDate(now.year, now.month, now.day)))

        # dbPaths
        # Windows: C:\Documents and Settings\<User>\Application Data\Local Settings\FuME\FuME
        # macOS: /Users/<User>/Library/Application Support/FuME
        userDataDir = appdirs.user_data_dir('FuME', 'FuME')
        src = self.get_pathToTemp(['db', 'sql_default.db'])
        dst = os.path.join(userDataDir, 'sql.db')
        if not os.path.exists(userDataDir):
            os.makedirs(userDataDir)
            shutil.copy(src, dst)
        self.dbPath = dst

    def closeEvent(self, QCloseEvent):
        self.write_settings()
        self.chromeDriver.quit()
        self.db.close()

    @QtCore.pyqtSlot()
    def showFilterDialog(self):
        if self.comboBox.currentText() == 'Alle':
            QtWidgets.QMessageBox.warning(self, QtWidgets.qApp.tr("Region wählen"),
                                          QtWidgets.qApp.tr("Bitte zuerst eine Region wählen.\n\n"
                                                            "Ok drücken um fortzufahren."),
                                          QtWidgets.QMessageBox.Ok)
        else:
            self.filterWindow = FilterDialog(self)
            self.filterWindow.show()

    @QtCore.pyqtSlot()
    def date_changed(self):
        date_from = self.dateEdit_3.date()

        if self.actionZeitraum.isChecked():
            date_to = self.dateEdit_4.date()

            if date_from > date_to:
                date_to = date_from
                self.dateEdit_4.setDate(date_to)
            elif date_to < date_from:
                date_from = date_to
                self.dateEdit_3.setDate(date_from)

            date_from_str = date_from.toString("yyyy-MM-dd")
            date_to_str = date_to.addDays(1).toString("yyyy-MM-dd")  # Upper limit exclusive in BETWEEN statement

            self.dateFilterString = 'match_date BETWEEN "%s" AND "%s"' % (date_from_str, date_to_str)
        else:
            date_from_str = date_from.toString("yyyy-MM-dd")
            self.dateFilterString = 'match_date LIKE "%s%%"' % (date_from_str)

        self.sqlmodel_calendar.setFilter(self.get_filterString())
        self.sqlmodel_calendar.select()
        self.tableView.resizeColumnsToContents()

    @QtCore.pyqtSlot(str)
    def lineEdit_changed(self, text):
        # adapted: http://stackoverflow.com/a/32336368/6304901
        self.hideAll()

        for i in self.listWidget.findItems(text, QtCore.Qt.MatchContains):
            if self.comboBox.currentText() == i.data(QtCore.Qt.UserRole):
                if self.checkBox_2.isChecked():
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
    def comboBox_changed(self):
        region = self.comboBox.currentText()
        if region == 'Alle':
            self.regionFilterString = ''
        else:
            self.regionFilterString = 'region = "%s"' % region

        self.sqlmodel_calendar.setFilter(self.get_filterString())
        self.sqlmodel_calendar.select()
        # self.tableView_2.resizeColumnsToContents()

        self.showAll()
        if region != 'Alle':  # else do nothing (show all)
            for i in range(self.listWidget.count()):
                itemData = self.listWidget.item(i).data(QtCore.Qt.UserRole)
                if itemData != region and itemData != None:
                    self.listWidget.item(i).setHidden(True)

        # trigger itemSelection_changed for multiregion support
        self.itemSelection_changed()

    @QtCore.pyqtSlot()
    def itemSelection_changed(self):
        region = self.comboBox.currentText()
        self.selection = self.listWidget.selectedItems()

        self.matchFilterString = ''
        countTeams = 0

        if self.selection != []:
            if region == 'Alle':
                teams = [i.text() for i in self.selection]
            else:
                teams = [i.text() for i in self.selection if i.data(QtCore.Qt.UserRole) == region]
            teamStr = ['home = "%s"' % i for i in teams]
            teamStr = ' OR '.join(teamStr)
            countTeams = len(teams)
            if teamStr != '':
                # no selection in current region found
                self.matchFilterString = '(' + teamStr + ')'

        self.sqlmodel_calendar.setFilter(self.get_filterString())
        self.sqlmodel_calendar.select()
        if self.sqlmodel_calendar.rowCount() > 0:
            self.tableView.resizeColumnsToContents()

        countMatches = self.sqlmodel_calendar.rowCount()
        if countMatches == 256:
            countMatches = '\u221e'
        self.statusBarLabel_1.setText('%s Mannschaften / %s Spiele' % (countTeams, countMatches))

    @QtCore.pyqtSlot()
    def datePeriodMenu_changed(self):
        if self.actionZeitraum.isChecked():
            # Range
            self.label_2.setText('Vom:')
            self.label_4.setVisible(True)
            self.dateEdit_4.setVisible(True)

        elif self.actionZeitpunkt.isChecked():
            # Day
            self.label_2.setText('Am:')
            self.label_4.setVisible(False)
            self.dateEdit_4.setVisible(False)

        self.date_changed()
        self.itemSelection_changed()

    @QtCore.pyqtSlot()
    def viewMenu_changed(self):
        if self.actionAnsichtSpiele.isChecked():
            # Show matches
            self.label_5.setVisible(False)
            self.label_6.setVisible(False)
            self.resFilterString = ''
        elif self.actionAnsichtReservierungen.isChecked():
            # Show reservations
            self.label_5.setVisible(True)
            self.label_6.setVisible(True)
            self.resFilterString = 'reserved <> 0'
        self.itemSelection_changed()

    @QtCore.pyqtSlot()
    def restoreSelection(self):
        self.listWidget.selectionModel().clearSelection()

        for x in self.current_selection:  # Current selection saved during startup
            self.listWidget.setCurrentItem(x, QtCore.QItemSelectionModel.Select)

    @QtCore.pyqtSlot()
    def resetSelection(self):
        self.listWidget.selectionModel().clearSelection()

    @QtCore.pyqtSlot()
    def invertSelection(self):
        for i in range(self.listWidget.count()):
            if not self.listWidget.item(i).isHidden():
                self.listWidget.setCurrentRow(i, QtCore.QItemSelectionModel.Toggle)

    @QtCore.pyqtSlot()
    def removeSelectedItems(self):
        for i in self.listWidget.selectedItems():
            if i.data(QtCore.Qt.UserRole) == self.comboBox.currentText():
                self.listWidget.takeItem(self.listWidget.row(i))

    @QtCore.pyqtSlot()
    def reserve_match(self):
        selected = self.get_selectedMatches()
        cookies = self.get_cookies()

        if selected == None or cookies == None:
            return

        options = {
            'what': 'reserve',
            'cookie': cookies,
            'selected': selected,
            'database-path': self.dbPath,
            'parent': self
        }
        self.reserveProcess = ReserveProcessor(options)

        # Connections
        self.reserveProcess.loggerSignal.connect(self.logDialog.add)
        self.reserveProcess.statusBarSignal.connect(self.statusBar.showMessage)
        self.reserveProcess.alreadyReservedSignal.connect(self.alreadyReservedMessageBox)
        self.reserveProcess.finished.connect(self.sqlmodel_calendar.select)
        self.reserveProcess.finished.connect(self.tableView.resizeColumnsToContents)
        self.reserveProcess.updateGuiSignal.connect(self.sqlmodel_calendar.select)

        self.reserveProcess.start()

    @QtCore.pyqtSlot(str)
    def alreadyReservedMessageBox(self, text):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setBaseSize(QtCore.QSize(600, 300))
        msgBox.setText("Bereits reservierte Spiele gefunden!")
        msgBox.setInformativeText(text)
        msgBox.exec()

    @QtCore.pyqtSlot()
    def download_match(self):
        date_from = self.dateEdit_3.date()
        if self.actionZeitraum.isChecked():
            date_to = self.dateEdit_4.date()
        else:
            date_to = date_from

        options = {
            'region': self.comboBox.currentText(),
            'date-from': date_from,
            'date-to': date_to,
            'database-path': self.dbPath,
            'parent': self
        }

        if self.comboBox.currentText() == 'Alle':
            QtWidgets.QMessageBox.warning(self, QtWidgets.qApp.tr("Region wählen"),
                                          QtWidgets.qApp.tr("Bitte zuerst eine Region wählen.\n\n"
                                                            "Ok drücken um fortzufahren."),
                                          QtWidgets.QMessageBox.Ok)
            return
        else:
            self.downloadProcessor = DownloadProcessor(options)

        # Connections
        self.downloadProcessor.finished.connect(self.sqlmodel_calendar.select)
        self.downloadProcessor.finished.connect(self.tableView.resizeColumnsToContents)
        self.downloadProcessor.loggerSignal.connect(self.logDialog.add)
        self.downloadProcessor.statusBarSignal.connect(self.statusBar.showMessage)

        self.downloadProcessor.start()

    @QtCore.pyqtSlot()
    def set_chromeDriver(self):
        options = {'parent': self}
        self.chromeDriver = ChromeDriverProcessor(options)

        self.chromeDriver.loggerSignal.connect(self.logDialog.add)

        self.chromeDriver.start()

    @QtCore.pyqtSlot(dict)
    def set_updateDialog(self, data):
        if not self.settings.value('updates/skipthisversion/%s' % data['current'], False, bool):  # dont skip
            if data['latest'] > data['current']:  # silent check
                data.update({'logo': self.header})
                self.updateDialog = UpdateDialog(parent=self, data=data)
                self.updateDialog.show()
            elif data['active']:  # mannually checked for updates
                QtWidgets.QMessageBox.information(self, QtWidgets.qApp.tr("Software-Update"),
                                                  QtWidgets.qApp.tr("Keine Updates gefunden.\n\n"
                                                                    "FuME ist auf dem neusten Stand!"),
                                                  QtWidgets.QMessageBox.Ok)
            else:
                self.logDialog.add('Auf dem neusten Stand: Version %s' % version)

    @QtCore.pyqtSlot()
    def checkForUpdates(self, active=True):
        options = {
            'version': version,
            'active': active,
            'parent': self
        }
        self.updateProcessor = UpdateProcessor(options)

        # Connections
        self.updateProcessor.loggerSignal.connect(self.logDialog.add)
        self.updateProcessor.statusBarSignal.connect(self.statusBar.showMessage)
        self.updateProcessor.updateSignal.connect(self.set_updateDialog)

        self.updateProcessor.start()

    @QtCore.pyqtSlot()
    def deleteReservation(self):
        selected = self.get_selectedMatches()
        cookies = self.get_cookies()

        if selected == None or cookies == None:
            return

        options = {
            'what': 'delete',
            'cookie': cookies,
            'selected': selected,
            'database-path': self.dbPath,
            'parent': self
        }
        self.reserveProcess = ReserveProcessor(options)

        # Connections
        self.reserveProcess.loggerSignal.connect(self.logDialog.add)
        self.reserveProcess.statusBarSignal.connect(self.statusBar.showMessage)
        self.reserveProcess.alreadyReservedSignal.connect(self.alreadyReservedMessageBox)
        self.reserveProcess.finished.connect(self.sqlmodel_calendar.select)
        self.reserveProcess.finished.connect(self.tableView.resizeColumnsToContents)
        self.reserveProcess.updateGuiSignal.connect(self.sqlmodel_calendar.select)

        self.reserveProcess.start()


def run():
    app = QtWidgets.QApplication(sys.argv)

    # Translates standard-buttons (Ok, Cancel) and mac menu bar to german
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    path = os.path.join(base_path, 'bin', 'qtbase_de.qm')
    translator = QtCore.QTranslator()
    translator.load(path)
    app.installTranslator(translator)

    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
