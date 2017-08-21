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

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from selenium import webdriver
from seleniumrequests import Remote


class GaleryProcessor(QtCore.QThread):
    loggerSignal = QtCore.pyqtSignal(str)
    statusBarSignal = QtCore.pyqtSignal(str)

    def __init__(self, options):
        super(GaleryProcessor, self).__init__(options['parent'])

        self.settings = QtCore.QSettings('fume', 'Match-Explorer')

        self.match = options['match']
        self.files = options['files']
        self.cookies = options['cookies']
        self.baseUrl = 'https://www.fupa.net/fupa/admin/index.php?page=fotograf_spiele'

    # def __del__(self):
    #     self.wait()

    def createGalery(self):
        url = 'https://www.fupa.net/fupa/admin/index.php?page=galerie_edit&aktion=new'
        self.driver.get(url=url)

        api = 'https://www.fupa.net/fupa/admin/api.php?p=galerie_upload'
        count = len(self.files)
        counter = 1
        for image in self.files:
            files = {'file': open(image, 'rb')}
            self.loggerSignal.emit('Upload %d/%d' % (counter, count))
            self.driver.request("POST", url=api, files=files)
            counter += 1

        url = 'https://www.fupa.net/fupa/admin/index.php?page=galerie_edit&gale_id='
        payload = {'act': 'new',
                   'input_match_id': str(self.match['match_id']),
                   'gale_bezeich': '123'}
        self.loggerSignal.emit('Erstelle Galerie...')
        self.driver.request("POST", url=url, data=payload)

    def run(self):
        self.loggerSignal.emit("Initialisiere Browser...")
        options = webdriver.ChromeOptions()
        if self.settings.value('chrome/headless', False, bool):
            options.add_argument('--headless')

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

        self.driver.get(self.baseUrl)

        for cookie in self.cookies:
            self.driver.add_cookie(cookie)

        self.createGalery()

        self.loggerSignal.emit('Galerie erfolgreich erstellt.')

        self.driver.close()
