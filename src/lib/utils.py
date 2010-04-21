##########################################################################
# Copyright 2009 Carlos Ribeiro
#
# This file is part of Radio Tray
#
# Radio Tray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 1 of the License, or
# (at your option) any later version.
#
# Radio Tray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################
from os.path import exists, join

try:
    import pygtk
    pygtk.require("2.0")
    import dbus
    import dbus.service
except:
      pass

try:
    import gtk
except ImportError, e:
    print str(e)
    raise SystemExit


def load_ui_file(name):
    import common
    ui = gtk.Builder()
    ui.add_from_file(join(common.DEFAULT_CFG_PATH, name))
    return ui

paths = ("/usr/local/share/radiotray","/usr/share/radiotray")

def tryopen(filename):
    """Returns a reading file handle for filename, searching through directories in the supplied paths."""
    try:
        f = open(filename)
        return f
    except IOError, e:
        for p in paths:
            try:
                f = open(join(p,filename))
                return f
            except IOError, e:
                0
    raise IOError, "Unable to find file "+filename

def findfile(filename):
    """Looks for filename, searching a built-in list of directories; returns the path where it finds the file."""
    if exists(filename): return filename
    for p in paths:
        x = join(p,filename)
	print x
        if exists(x): return x


def html_escape(text):
    """Produce entities within text."""

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }

    return "".join(html_escape_table.get(c,c) for c in text)

