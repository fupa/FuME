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
from sys import platform

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

# adapted: https://github.com/pypt/fervor
# which is very close to https://sparkle-project.org
from fume.ui.updatewindow import Ui_UpdateWindow


class UpdateDialog(QtWidgets.QDialog, Ui_UpdateWindow):
    def __init__(self, data, parent=None):
        super(UpdateDialog, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.data = data

        self.label.setPixmap(QtGui.QPixmap(data['logo']))
        self.settings = QtCore.QSettings('fume', 'Match-Explorer')

        self.wouldYouLikeToDownloadLabel.setText(
            "FuME {latest} ist verfügbar (Du verwendest Version {current}). "
            "Möchtest du die neue Version jetzt herunterladen?".format(current=data['current'], latest=data['latest']))

        self.textEdit.setText(data['changelog'])

        # restore check state
        self.checkBox.setChecked(self.settings.value('updates/noautoupdate', False, bool))

        # Connections
        self.skipThisVersionButton.clicked.connect(self.skipThisVersion)
        self.remindMeLaterButton.clicked.connect(self.close)
        self.installUpdateButton.clicked.connect(self.installUpdates)
        self.checkBox.stateChanged.connect(self.noAutoUpdates)

    @QtCore.pyqtSlot()
    def skipThisVersion(self):
        self.settings.setValue('updates/skipthisversion/%s' % self.data['current'], True)
        self.close()

    @QtCore.pyqtSlot()
    def installUpdates(self):
        if platform == "win32":
            url = self.data['url-windows']
            os = 'Windows'
        else:
            url = self.data['url-mac']
            os = 'macOS'

        text = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li {{ white-space: pre-wrap; }}
</style></head><body style=" font-family:'.SF NS Text'; font-size:13pt; font-weight:400; font-style:normal;">

Die neuste Version für {platform} kannst du unter folgendem Link herunterladen: <br />
<a href='{url}'>{url}</a><br /><br />
Lade das Update herunter, schließe FuME, installiere die Datei und öffne FuME erneut.<br /><br />
Mit einem klick auf OK erlaubst du FuME, den obigen Link in deinem Browser zu öffnen.<br /><br />

</body></html>
        """.format(platform=os, url=url)

        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setWindowTitle("Software-Update")
        msgBox.setText("Software-Update")
        msgBox.setInformativeText(text)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msgBox.setBaseSize(QtCore.QSize(550, 275))
        ret = msgBox.exec()

        if ret == QtWidgets.QMessageBox.Ok:
            webbrowser.open(url)
            self.close()

    @QtCore.pyqtSlot(int)
    def noAutoUpdates(self, int):
        if int == 2:
            # Checkbox checked
            self.settings.setValue('updates/noautoupdate', True)
        else:
            # checkbox unchecked: auto update on startup
            self.settings.setValue('updates/noautoupdate', False)
