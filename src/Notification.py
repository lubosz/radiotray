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

    def __init__(self, cfg_provider):
        self.notif = None
        self.cfg_provider = cfg_provider
        self.lastMessage = None

    def notify(self, title, message):

        if self.cfg_provider.getConfigValue("enabled_notifications") == "true" and self.lastMessage != message:

            self.lastMessage = message
            
            if self.notif == None:
        
                if pynotify.init(APPNAME):
                    self.notif = pynotify.Notification(title, message)
                    self.notif.set_urgency(pynotify.URGENCY_LOW)
                    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(APP_ICON, 48, 48)
                    self.notif.set_icon_from_pixbuf(pixbuf)
                    self.notif.set_timeout(pynotify.EXPIRES_DEFAULT)
                    self.notif.show()
                else:
                    print "Error: there was a problem initializing the pynotify module"
            
            else:
                self.notif.update(title, message)
                self.notif.show()
