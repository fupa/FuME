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

from PyQt5 import QtWidgets
from PyQt5 import QtGui

from fume.ui.about import Ui_Dialog


class AboutDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, path, version, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.label.setPixmap(QtGui.QPixmap(path))
        self.label_3.setText('Version v%s' % version)
