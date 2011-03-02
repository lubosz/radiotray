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
from events.EventSubscriber import EventSubscriber
from events.EventManager import EventManager
from Plugin import Plugin
import gtk

# Basic example of a plugin
class HelloWorldPlugin(Plugin):

    def __init__(self):
        print "started"


    def getName(self):
        return self.name

    def activate(self):
        self.eventSubscriber.bind(EventManager.SONG_CHANGED, self.on_song_changed)
        self.tooltip.addSource(self.populate_tooltip)

        menuItem = gtk.MenuItem(self.getName(), False)
        menuItem.connect('activate', self.on_menu)
        menuItem.show()
        self.setMenuItem(menuItem)

    def populate_tooltip(self):
        return "Hello"

    def on_song_changed(self, data):
        print "song changed"
        print data

    def on_menu(self, data):
        print "menu clicked!"
