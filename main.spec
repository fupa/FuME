# -*- mode: python -*-
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
#
# Anmerkungen: aus https://stackoverflow.com/a/13421926
# Falls Pyinstaller sich beschwert (z.B. nach update von PyQt)
# FileNotFoundError: [Errno 2] No such file or directory: '/opt/local/lib/mysql55/mysql/libmysqlclient.18.dylib'
# muss die Verlinkung von
# /Users/Andreas/.pyenv/versions/3.5.0/lib/python3.5/site-packages/PyQt5/Qt/plugins/sqldrivers/libqsqlmysql.dylib
# geändert werden mit (install_name_tool -change old new input)
# sudo install_name_tool -change \
# /opt/local/lib/mysql55/mysql/libmysqlclient.18.dylib \
# /usr/local/Cellar/mysql@5.5/5.5.56/lib/libmysqlclient.18.dylib \
# /Users/Andreas/.pyenv/versions/3.5.0/lib/python3.5/site-packages/PyQt5/Qt/plugins/sqldrivers/libqsqlmysql.dylib
# Überprüfen mit
# otool -L /Users/Andreas/.pyenv/versions/3.5.0/lib/python3.5/site-packages/PyQt5/Qt/plugins/sqldrivers/libqsqlmysql.dylib

block_cipher = None

from sys import platform

os = None
name = 'FuME'
version = '1.1'
debug = False
console = False
excludes = []
onefile_windows = False

if platform == "darwin" or platform == "linux" or platform == "linux2":
    # macOS or linux
    os = 'unix'
    pathex = ['/Users/Andreas/Documents/projects/fume']
    binaries = [('chromedriver', '.')]
    datas = [('db/sql_default.db', 'db/.'),
             ('bin/header_klein.png', 'bin/.'),
             ('bin/qtbase_de.qm', 'bin/.'),
             ('LICENSE', '.'),
             ('bin/buttons', 'bin/buttons/.')]
    icon = 'bin/icon.icns'
    name_coll = name + '_mac'
else:
    # Windows
    os = 'windows'
    pathex = ['C:\\Users\\Andreas\\Documents\\fume',
              'C:\\Program Files\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin',
              'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x64']
    binaries = [('chromedriver.exe', '.')]
    datas = [('db\\sql_default.db', 'db\\.'),
             ('bin\\header_klein.png', 'bin\\.'),
             ('bin\\qtbase_de.qm', 'bin\\.'),
             ('bin\\icon.ico', 'bin\\.'),
             ('LICENSE', '.'),
             ('bin\\buttons\\', 'bin\\buttons\\.')]
    icon = 'bin\\icon.ico'
    name_coll = name + '_win'

a = Analysis(['main.py'],
             pathex=pathex,
             binaries=binaries,
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

if os == 'unix':
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,  # differs
              name=name,
              version=version,
              debug=debug,
              strip=False,
              upx=True,
              console=console,
              icon=icon)
else:
    if onefile_windows:
        exe = EXE(pyz,
                  a.scripts,
                  a.binaries,
                  a.zipfiles,
                  a.datas,
                  name=name,
                  debug=debug,
                  strip=False,
                  upx=True,
                  console=console,
                  icon=icon)
    else:
        exe = EXE(pyz,
                  a.scripts,
                  exclude_binaries=True,
                  name=name,
                  debug=debug,
                  strip=False,
                  upx=True,
                  console=False,
                  icon=icon)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=name_coll)

app = BUNDLE(coll,
             name=name + '.app',
             version=version,
             icon=icon,
             bundle_identifier=None,
             info_plist={
                 'NSHighResolutionCapable': 'True'
             })
