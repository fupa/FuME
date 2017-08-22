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

import requests
from PyQt5 import QtCore
from lxml import objectify


class UpdateProcessor(QtCore.QThread):
    loggerSignal = QtCore.pyqtSignal(str)
    statusBarSignal = QtCore.pyqtSignal(str)
    updateSignal = QtCore.pyqtSignal(dict)

    def __init__(self, options):
        super(UpdateProcessor, self).__init__(options['parent'])

        self.current = options['version']
        self.active = options['active']

    # def __del__(self):
    #     self.wait()

    def download(self, url):
        uAStr = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        headers = {'User-Agent': uAStr}
        return requests.get(url, timeout=10, headers=headers)

    def run(self):
        try:
            xml = self.download('https://fupadev.github.io/FuME/appcast.xml').content
        except Exception as e:
            self.loggerSignal.emit('Es konnte nicht auf Updates überprüft werden: %s' % str(e))
            return

        # parsing XML
        root = objectify.fromstring(xml)
        latest = root.latest

        try:
            changelog = self.download(latest.changelog).text
        except Exception as e:
            self.loggerSignal.emit('Es konnte nicht auf Updates überprüft werden: %s' % str(e))
            return

        data = {
            'active': self.active,
            'current': float(self.current),
            'latest': latest.version,
            'changelog': str(changelog),
            'url-windows': str(latest.windows),
            'url-mac': str(latest.mac)
        }

        self.updateSignal.emit(data)
