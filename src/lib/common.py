# -*- coding: utf-8 -*-

import os
import i18n
from xdg.BaseDirectory import xdg_data_home

try:
    from defs import *
except:
    APPVERSION = "0.5"
    datadir = "/usr/share"

# Application info
APPNAME = "Radio Tray"
APPDIRNAME = APPNAME.lower().replace(" ","")

COPYRIGHT_YEAR = '2009 - 2010'
COPYRIGHTS = "%s - Copyright (c) %s\n" \
             "Carlos Ribeiro <carlosmribeiro1@gmail.com>" % (APPNAME, COPYRIGHT_YEAR)
WEBSITE = "http://radiotray.sourceforge.net/"
AUTHORS = [
    _('Developers:'),
    "Carlos Ribeiro <carlosmribeiro1@gmail.com>",
    _('Contributors:'),
    'Og Maciel <ogmaciel@gnome.com>',

# Media path
if os.path.exists(os.path.abspath('../data/images/')):
    IMAGE_PATH = os.path.abspath('../data/images/')
else:
    IMAGE_PATH = '%s/%s/images' % (datadir, APPDIRNAME)

# Images
APP_ICON = os.path.join(IMAGE_PATH, 'radiotray.png')

# Config info
CFG_NAME = 'bookmarks.xml'
USER_CFG_PATH =  os.path.join(xdg_data_home, APPDIRNAME)
if os.path.exists(os.path.abspath('../data/')):
    DEFAULT_CFG_PATH = os.path.abspath('../data/')
else:
    DEFAULT_CFG_PATH = '%s/%s/' % (datadir, APPDIRNAME)
