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

import os
import sys
import time

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from fume.ui.settings import Ui_Settings


class SettingsDialog(QtWidgets.QDialog, Ui_Settings):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.settings = QtCore.QSettings('fume', 'Match-Explorer')

        # Connections
        self.pushButton.clicked.connect(self.createCookie)
        self.pushButton_2.clicked.connect(self.deleteSettings)
        self.accepted.connect(self.lineEdit_2.clear)

    def waitForLoad(self, inputXPath, browser, PATIENCE_TIME):
        # adapted: https://stackoverflow.com/a/39109601
        Wait = WebDriverWait(browser, PATIENCE_TIME)
        Wait.until(EC.presence_of_element_located((By.XPATH, inputXPath)))

    def get_pathToTemp(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def isFrozen(self):
        # TODO Use this
        if getattr(sys, 'frozen', False):
            return True
        else:
            return False

    @QtCore.pyqtSlot()
    def createCookie(self):
        __username = self.lineEdit.text()
        __password = self.lineEdit_2.text()

        options = webdriver.ChromeOptions()
        # waiting for Chrome 60 on Windows
        # Chrome 59 for macOS already supports headless Chrome!
        # options.add_argument('--headless')

        # https://doc.qt.io/qt-5/qmessagebox.html
        msgBox = QtWidgets.QMessageBox()

        try:
            self.driver = Remote('http://localhost:9515', desired_capabilities=options.to_capabilities())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, QtWidgets.qApp.tr("Keine Verbindung zu Google Chrome!"),
                                           QtWidgets.qApp.tr(
                                               "Es konnte keine Verbindung zu Google Chrome hergestellt werden! "
                                               "Bitte stelle sicher, dass alle Systemvoraussetzungen erfüllt sind.\n\n"
                                               "Fehler:\n" + str(e)),
                                           QtWidgets.QMessageBox.Cancel)
            return

        self.driver.get("https://www.fupa.net/fupa/admin/index.php")
        assert "Vereinsverwaltung" in self.driver.title
        self.driver.execute_script("document.getElementById('email').value = '%s'" % __username)
        self.driver.execute_script("document.getElementById('password').value = '%s'" % __password)
        time.sleep(3)
        self.driver.execute_script("firebase_on_login_form_submit(false)")
        try:
            # time.sleep(5)
            # self.driver.find_element_by_xpath("//a[@href='index.php?page=profil']")
            self.waitForLoad("//a[@href='index.php?page=profil']", self.driver, 3)

            cookies = self.driver.get_cookies()
            self.settings.setValue('cookie', cookies)

            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText("Cookie erfolgreich erstellt und gespeichert")
            msgBox.setInformativeText("Du kannst jetzt Spiele reservieren.")
        except:
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText("Login fehlgeschlagen")
            if "Ungültiger Zugriff" not in self.driver.page_source:
                errorMsg = self.driver.find_element_by_id("firebase_message").text
            else:
                errorMsg = "Ungültiger Zugriff. Bitte neu einloggen."
            msgBox.setInformativeText(errorMsg)

        self.driver.quit()
        msgBox.exec()

    @QtCore.pyqtSlot()
    def deleteSettings(self):
        ret = QtWidgets.QMessageBox.critical(self, QtWidgets.qApp.tr("Alle Einstellungen löschen"),
                                             QtWidgets.qApp.tr("Willst du wirklich alle Einstellungen löschen?\n\n"
                                                               "Drücke OK zum bestätigen und Cancel zum abbrechen."),
                                             QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if ret == QtWidgets.QMessageBox.Ok:
            QtWidgets.QMessageBox.critical(self, QtWidgets.qApp.tr("Alle Einstellungen löschen"),
                                           QtWidgets.qApp.tr("Alle Einstellungen werden gelöscht "
                                                             "und das Programm beendet"),
                                           QtWidgets.QMessageBox.Ok)

            #sys.exit(1)
            self.parent().close()
            self.settings.clear()
