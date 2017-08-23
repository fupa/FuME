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

from __future__ import unicode_literals

import biplist
import os.path
import os

# Usage:
# $ dmgbuild -s build_dmg.py "FuME" FuME.dmg

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

def version_from_app(app_path):
    plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
    plist = biplist.readPlist(plist_path)
    return plist['CFBundleShortVersionString']

# .. Basics ....................................................................

# Uncomment to override the output filename
filename = 'FuME-' + version_from_app(application) + '.dmg'

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