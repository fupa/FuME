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

import webbrowser

from PyQt5 import QtWidgets

from fume.threads.GaleryProcessor import GaleryProcessor
from fume.ui.creategalery import Ui_Dialog


class GaleryDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, match, cookies, parent=None):
        super(GaleryDialog, self).__init__(parent)
        self.setupUi(self)

        self.cookies = cookies
        self.match = match
        self.files = None

        self.label_3.setText(self.match['home'])
        self.label_5.setText(self.match['guest'])
        self.label_7.setText(str(self.match['match_id']))

        self.pushButton.clicked.connect(self.addImages)
        self.pushButton_2.clicked.connect(self.uploadGalery)

    def addImages(self):
        options = QtWidgets.QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        self.files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Fotos (*.jpg) wählen", "",
                                                               "Images (*.jpg)", options=options)
        if self.files:
            for file in self.files:
                self.plainTextEdit.appendPlainText(file)

    def uploadGalery(self):
        self.plainTextEdit.appendPlainText('----------------------------')

        options = {
            'match': self.match,
            'files': self.files,
            'cookies': self.cookies,
            'parent': self
        }

        if self.files:
            self.galeryProcessor = GaleryProcessor(options)
        else:
            return

        # Connections
        self.galeryProcessor.finished.connect(self.openGalery)
        self.galeryProcessor.started.connect(lambda: self.pushButton_2.setEnabled(False))
        self.galeryProcessor.loggerSignal.connect(self.parent().logDialog.add)
        self.galeryProcessor.loggerSignal.connect(self.plainTextEdit.appendPlainText)
        self.galeryProcessor.statusBarSignal.connect(self.parent().statusBar.showMessage)

        self.galeryProcessor.start()

    def openGalery(self):
        if self.checkBox.isChecked():
            webbrowser.open('https://www.fupa.net/spielberichte/xxx-xxx-xxx-%d.html' % self.match['match_id'])
