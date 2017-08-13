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

from PyQt5 import QtWidgets

from fume.ui.log import Ui_Log


class LogDialog(QtWidgets.QDialog, Ui_Log):
    def __init__(self, parent=None):
        super(LogDialog, self).__init__(parent)
        self.setupUi(self)
        self.__counter = 1

    def add(self, text):
        # if len(text) > 55:
        #     self.add(text[0:55])
        #     self.add(text[55:])
        # else:
        time = datetime.datetime.now().strftime("%H:%M:%S")
        self.plainTextEdit.appendPlainText("[%s] %s Uhr: %s" % (self.__counter, time, text))
        self.parent().statusBar.showMessage("%s" % text)
        self.__counter += 1
