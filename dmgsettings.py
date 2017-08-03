# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import biplist
import os.path
import os

# Usage:
# $ dmgbuild -s dmgsettings.py "FuME" FuME.dmg

# .. Useful stuff ..............................................................

application = 'FuME.app'
appname = os.path.basename(application)

def icon_from_app(app_path):
    plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
    plist = biplist.readPlist(plist_path)
    icon_name = plist['CFBundleIconFile']
    icon_root,icon_ext = os.path.splitext(icon_name)
    if not icon_ext:
        icon_ext = '.icns'
    icon_name = icon_root + icon_ext
    return os.path.join(app_path, 'Contents', 'Resources', icon_name)

# .. Basics ....................................................................

# Uncomment to override the output filename
filename = 'FuME.dmg'

# Uncomment to override the output volume name
volume_name = 'FuME'

# Volume format (see hdiutil create -help)
format = 'UDBZ'

# Volume size
size = None

# Files to include
files = [ application ]

# Symlinks to create
symlinks = { 'Programme': '/Applications' }

#icon = '/path/to/icon.icns'
#badge_icon = icon_from_app(application)

# Where to put the icons
icon_locations = {
    appname:        (140, 180),
    'Programme': (500, 180)
    }

# .. Window configuration ......................................................

background = '../bin/dmg_background.png'

show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Window position in ((x, y), (w, h)) format
window_rect = ((100, 100), (640, 370))

default_view = 'icon-view'

# General view configuration
show_icon_preview = False

include_icon_view_settings = 'auto'
include_list_view_settings = 'auto'

# .. Icon view configuration ...................................................

arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = 'bottom' # or 'right'
text_size = 14
icon_size = 124