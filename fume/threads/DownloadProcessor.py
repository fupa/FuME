#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os

import lxml.html
import requests
from PyQt5 import QtCore

class DownloadProcessor(QtCore.QThread):
    loggerSignal = QtCore.pyqtSignal(str)
    statusBarSignal = QtCore.pyqtSignal(str)

    def __init__(self, options):
        super(DownloadProcessor, self).__init__(options['parent'])

        self.region = options['region']
        self.date_from = options['date-from']
        self.date_to = options['date-to']
        self.dbPath = options['database-path']

    def __del__(self):
        self.wait()

    def download(self, date):
        uAStr = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        headers = {'User-Agent': uAStr}
        url = 'http://www.fupa.net/index.php?page=kalender&site_linkurl=%s&date=%s' % (self.region, date)
        r = requests.get(url, headers=headers)
        doc = lxml.html.fromstring(r.content)

        path = '/html/body//table[@class]//tr/td/a[not(contains(@class, "spielbericht_icon"))]//text() | ' \
               '/html/body//table[@class]//tr/td//img/@src | ' \
               '/html/body//table[@class]//th//text() | ' \
               '/html/body//table[@class]//th/a/@href | ' \
               '/html/body//table[@class]//tr/td[@style]/a/@href'

        raw = doc.xpath(path)

        # replacing '-Live-' with '-:-'
        raw = [i.replace('http://www.fupa.net/fupa/images/buttons/tipp_live.jpg', '-:-') for i in raw]

        # From
        # ['/liga/bezirksliga-west-31261.html', 'Bezirksliga West', '19:15 Uhr', 'TSV Abensberg', '-:-',
        # '/spielberichte/tsv-abensberg-spvgg-mariaposching-3679861.html', 'SpVgg Mariaposching',
        # To
        # [['Bezirksliga West', '19:15 Uhr', 'TSV Abensberg', '-:-', '3679861', 'SpVgg Mariaposching'],
        matches = []
        for i, d in enumerate(raw):

            if 'Relegation' in d:
                league = 'Relegation'
            elif '/liga/' in d:
                league = raw[i + 1]
            elif 'Test' in d:
                league = raw[i]

            if 'Uhr' in d:
                # print(i)
                current = [league]
                for i in raw[i:i + 5]:
                    if '/spielberichte/' in i:
                        i = i.split('.')[0].split('-')[-1]
                        if '/spielberichte/' in i:  # Fehler in Fupa: URL = '/spielberichte/.html'
                            i = ''
                    current.append(i)
                matches.append(current)

        # rearrange
        # ['3679861', 'Bezirksliga West', '19:15 Uhr', 'TSV Abensberg', 'SpVgg Mariaposching', '-:-']
        tmp = []
        for spiel in matches:
            order = [4, 0, 1, 2, 5, 3]
            spiel = [spiel[i] for i in order]
            spiel[2] = date + ' ' + spiel[2][0:5]
            tmp.append(spiel)
        data = tmp

        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        for p in data:
            format_str = """INSERT OR IGNORE INTO calendar(match_id, league, match_date, home, guest, result, region)
                VALUES ("{match_id}", "{league}", "{match_date}", "{home}", "{guest}", "{result}", "{region}");"""

            sql_command = format_str.format(match_id=p[0], league=p[1], match_date=p[2],
                                            home=p[3], guest=p[4], result=p[5], region=self.region)

            if p[0] != '':  # fehler in URL bei Fupa
                cursor.execute(sql_command)
            else:
                print("Fehler bei SQL: " + str(sql_command))

            update_str = """UPDATE calendar
                    SET match_date="{match_date}", result="{result}", league="{league}" WHERE match_id = "{match_id}";"""

            sql_command = update_str.format(match_id=p[0], match_date=p[2], league=p[1], result=p[5])
            cursor.execute(sql_command)

        connection.commit()
        connection.close()

        return len(data)

    def run(self):
        self.statusBarSignal.emit("Download")
        if self.region == 'Alle':
            self.loggerSignal.emit('Bitte eine Region wählen!')
            return

        date_from = self.date_from
        date_to = self.date_to.addDays(1)
        counter = 0

        while date_from != date_to:
            try:
                counter += self.download(date_from.toString("yyyy-MM-dd"))
            except:
                self.loggerSignal.emit('Fehler beim importieren!')
                return
            date_from = date_from.addDays(1)
            self.statusBarSignal.emit("Download: #%s Spiele" % counter)

        self.loggerSignal.emit('%s Spiele erfolgreich hinzugefügt' % counter)
        self.statusBarSignal.emit("Bereit")
