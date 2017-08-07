#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5 import QtGui

from fume.ui.about import Ui_Dialog


class AboutDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, path, version, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.label.setPixmap(QtGui.QPixmap(path))
        self.label_3.setText('Version v%s' % version)
