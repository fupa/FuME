# -*- mode: python -*-

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

if platform == "darwin" or platform == "linux" or platform == "linux2":
    # macOS or linux
    os = 'unix'
    pathex = ['/Users/Andreas/Documents/projects/fume']
    binaries = [('chromedriver', '.')]
    datas = [('db/sql_default.db', 'db/.'),
             ('bin/header_klein.png', 'bin/.'),
             #('bin/header.png', 'bin/.'),  # for splash screen
             ('bin/buttons', 'bin/buttons/.')]
    icon = 'bin/icon.icns'
else:
    # Windows
    os = 'windows'
    pathex = ['C:\\Users\\Andreas\\Documents\\fume',
              'C:\\Program Files\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin',
              'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x64']
    binaries = [('chromedriver.exe', '.')]
    datas = [('db\\sql_default.db', 'db\\.'),
             ('bin\\header_klein.png', 'bin\\.'),
             #('bin\\header.png', 'bin\\.'),
             ('bin\\buttons\\', 'bin\\buttons\\.')]
    icon = 'bin\\icon.ico'

a = Analysis(['main.py'],
             pathex=pathex,
             binaries=binaries,
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=name)

app = BUNDLE(coll,
             name=name + '.app',
             version=version,
             icon=icon,
             bundle_identifier=None,
             info_plist={
                 'NSHighResolutionCapable': 'True'
             })
