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
import sqlite3
from PyQt5 import QtWidgets

from fume.ui.edit import Ui_Dialog


class EditDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, selected, dbPath, parent=None):
        super(EditDialog, self).__init__(parent)
        self.setupUi(self)

        self.dbPath = dbPath

        self.match = self.setMatchInfos(selected)

        self.lineEdit.setText(str(self.match['match_id']))
        self.lineEdit_2.setText(self.match['league'])
        self.lineEdit_3.setText(self.match['match_date'])
        self.lineEdit_4.setText(self.match['home'])
        self.lineEdit_5.setText(self.match['guest'])
        self.lineEdit_6.setText(self.match['result'])
        self.lineEdit_7.setText(self.match['region'])

        self.buttonBox.accepted.connect(self.writeInfos)
        self.pushButton.clicked.connect(self.deleteRow)


    def setMatchInfos(self, match):
        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        selectStr = """SELECT league, result, region FROM calendar WHERE match_id = "{match_id}";"""
        sql_command = selectStr.format(match_id=match['match_id'])
        cursor.execute(sql_command)

        result = cursor.fetchone()

        connection.commit()
        connection.close()

        match['league'] = result[0]
        match['result'] = result[1]
        match['region'] = result[2]

        return match

    def writeInfos(self):
        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        update_str = """UPDATE calendar
                        SET match_id="{match_id}", home="{home}", guest="{guest}", region="{region}", 
                            match_date="{match_date}", result="{result}", league="{league}" 
                        WHERE match_id = "{match_id}";"""

        sql_command = update_str.format(match_id=self.lineEdit.text(), match_date=self.lineEdit_3.text(),
                                        league=self.lineEdit_2.text(), result=self.lineEdit_6.text(),
                                        home=self.lineEdit_4.text(), guest=self.lineEdit_5.text(),
                                        region=self.lineEdit_7.text())

        try:
            cursor.execute(sql_command)
        except:
            self.parent().logDialog.add('Die Änderungen konnten nicht geschrieben werden!')

        connection.commit()
        connection.close()

        self.parent().sqlmodel_calendar.select()

    def deleteRow(self):
        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        update_str = """DELETE FROM calendar WHERE match_id="{match_id}";"""

        sql_command = update_str.format(match_id=self.lineEdit.text())

        try:
            cursor.execute(sql_command)
        except:
            self.parent().logDialog.add('Die Änderungen konnten nicht geschrieben werden!')

        connection.commit()
        connection.close()

        self.close()
        self.parent().sqlmodel_calendar.select()