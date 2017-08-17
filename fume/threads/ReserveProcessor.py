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
import sqlite3
import sys

import lxml.html
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from selenium import webdriver
from seleniumrequests import Remote


class ReserveProcessor(QtCore.QThread):
    loggerSignal = QtCore.pyqtSignal(str)
    statusBarSignal = QtCore.pyqtSignal(str)
    alreadyReservedSignal = QtCore.pyqtSignal(str)
    updateGuiSignal = QtCore.pyqtSignal()

    def __init__(self, options):
        super(ReserveProcessor, self).__init__(options['parent'])

        self.settings = QtCore.QSettings('fume', 'Match-Explorer')
        self.options = options

        self.selected = options['selected']
        self.cookies = options['cookie']
        self.dbPath = options['database-path']
        self.baseUrl = 'https://www.fupa.net/fupa/admin/index.php?page=fotograf_spiele'

    # def __del__(self):
    #     self.wait()

    def reserve(self, match):
        payload = {'match_selected': match['match_id'],
                   'match_verein_id': '',
                   'as_values_match_verein_id': '',
                   'check_match': match['match_id']}

        r = self.driver.request("POST", self.baseUrl + '&act=new', data=payload)
        doc = lxml.html.fromstring(r.content)
        path_match = "/html/body//table//tr[@id]/*//text() | " \
                     "/html/body//table//tr[@id]/*//@href"
        raw = doc.xpath(path_match)

        # 2017-06-05 -> 05.06.17
        date = datetime.datetime.strptime(match['match_date'], '%Y-%m-%d %H:%M').strftime('%d.%m.%y %H:%M')

        # ---- raw snipet -----
        # 0 06.06.17 18:30 Uhr
        # 1 Relegation
        # 2 TSV Landsberg
        # 3 - TSV Bogen
        # 4 index.php?page=fotograf_spiele&mafo_id=43704&act=del
        # 5 Bereits jemand eingetragen:
        # 6 http://www.fupa.net/fupaner/abc-def-3
        # 7 abc def
        # ...

        for i, d in enumerate(raw):
            if date in d:
                if match['home'] in raw[i + 2] and match['guest'] in raw[i + 3]:
                    url = raw[i + 4]
                    match['mafo_id'] = url.split("?")[1].split("&")[1].split("=")[1]
                    try:
                        if 'Bereits jemand eingetragen' in raw[i + 5]:
                            # already reserved
                            return match, raw[i + 7]  # Photographer
                    except:
                        pass
                    # match can be reserved
                    return match, None

    def insertMafoId(self, match):
        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        selectStr = """SELECT mafo_id FROM calendar WHERE match_id = "{match_id}";"""
        sql_command = selectStr.format(match_id=match['match_id'])
        cursor.execute(sql_command)

        mafo_id = cursor.fetchone()[0]

        connection.commit()
        connection.close()

        match['mafo_id'] = mafo_id
        return match

    def delete(self, match):
        self.loggerSignal.emit('Lösche Reservierung von %s - %s #%s' % (match['home'], match['guest'], match['match_id']))
        self.driver.request("GET", self.baseUrl + '&mafo_id=%s&act=del' % match['mafo_id'])

    def markRowAsReserved(self, match, val):
        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        updateStr = """UPDATE calendar SET reserved="{val}", mafo_id="{mafo_id}" WHERE match_id = "{match_id}";"""
        sql_command = updateStr.format(val=val, mafo_id=match['mafo_id'], match_id=match['match_id'])
        cursor.execute(sql_command)

        connection.commit()
        connection.close()
        self.updateGuiSignal.emit()

    def get_pathToTemp(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def run(self):
        if self.options['what'] == 'reserve':
            self.runReserve()
        elif self.options['what'] == 'delete':
            self.runDelete()

    def runReserve(self):
        self.statusBarSignal.emit("Reserviere Spiele...")
        counter = 0

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

        alreadyReserved = []
        for match in self.selected:
            self.loggerSignal.emit("Reserviere %s - %s #%d" % (match['home'], match['guest'], match['match_id']))
            try:
                matchNew, ph = self.reserve(match)
            except Exception as e:
                self.loggerSignal.emit("Fehler beim reservieren von %s" % match['match_id'])
                self.driver.close()
                print(e)
                return
            match = matchNew
            if ph != None:
                alreadyReserved.append([match, ph])
                self.loggerSignal.emit("Bereits reserviert von %s" % ph)
                self.markRowAsReserved(match, 2)
                self.delete(match)
            else:
                # changing db row to reserved
                self.markRowAsReserved(match, 1)
            counter += 1

        self.driver.close()

        # for MessageBox
        if len(alreadyReserved) > 0:
            infoText = ''
            try:
                for i in alreadyReserved:
                    infoText += ' '.join([i[0]['home'], '-', i[0]['guest'], 'von', i[1], '\n'])
            except:
                print(alreadyReserved)
            self.alreadyReservedSignal.emit(infoText)

        self.loggerSignal.emit('%s Spiele erfolgreich reserviert' % (counter - len(alreadyReserved)))
        self.loggerSignal.emit('%s davon waren reserviert' % len(alreadyReserved))
        self.statusBarSignal.emit("Bereit")

    def runDelete(self):
        self.statusBarSignal.emit("Lösche Reservierungen...")
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

        for match in self.selected:
            match = self.insertMafoId(match)
            self.delete(match)
            self.markRowAsReserved(match, 0)

        self.loggerSignal.emit('%s Reservierungen erfolgreich gelöscht.' % len(self.selected) )

        self.driver.close()
