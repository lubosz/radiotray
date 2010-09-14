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
import pynotify
import gtk
from lib.common import APP_ICON, APPNAME

class Notification:

    def __init__(self):
        self.n = None

    def notify(self, title, message):
        if self.n == None:
        
            if pynotify.init(APPNAME):
                self.n = pynotify.Notification(title, message)
                self.n.set_urgency(pynotify.URGENCY_LOW)
                pixbuf = gtk.gdk.pixbuf_new_from_file(APP_ICON)
                self.n.set_icon_from_pixbuf(pixbuf)
                self.n.set_timeout(pynotify.EXPIRES_DEFAULT)
            else:
                print "Error: there was a problem initializing the pynotify module"
            
        else:
            self.n.update(title, message)
            
        self.n.show()
