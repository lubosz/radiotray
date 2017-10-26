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
from lib import utils
from lib.common import SYSTEM_PLUGIN_PATH, USER_PLUGIN_PATH
import os

from gi.repository import Gdk

class HistoryPlugin(Plugin):
    def __init__(self):
        super(HistoryPlugin, self).__init__()

    def getName(self):
        return self.name

    def activate(self):
        self.eventSubscriber.bind(EventManager.SONG_CHANGED, self.on_song_changed)

        gladepath = ""
        gladefile = "history.glade"
        userpath = os.path.join(USER_PLUGIN_PATH, gladefile)
        systempath = os.path.join(SYSTEM_PLUGIN_PATH, gladefile)
        if os.path.exists(userpath):
            gladepath = userpath
        elif os.path.exists(systempath):
            gladepath = systempath
        else:
            self.log.error('Error initializing History plugin: history.glade not found')

        Gdk.threads_enter()
        self.gladefile = utils.load_ui_file(gladepath)
        self.text = self.gladefile.get_object('textview1')
        self.window = self.gladefile.get_object("dialog1")
        self.last_title = 'none'
        self.time = datetime.now().replace(microsecond=0)

        if (self.window):
            self.gladefile.connect_signals(self)
        Gdk.threads_leave()

    def on_song_changed(self, data):
        if('title' in data.keys()):
            title = data['title']
            time = datetime.now().replace(microsecond=0)
            delta = time-self.time
            time_str = str(delta)
            if title != self.last_title:
                self.last_title = title
                if self.text:
                  buffer = self.text.get_buffer()
                  buffer.insert(buffer.get_end_iter(),' '+time_str+'\n'+title)
            self.time = time


    def on_menu(self, data):
        if self.window:
          self.window.show()

    def on_close_clicked(self, widget):
        if self.window:
          self.window.hide()
        return True

    def on_delete_event(self, widget, event, data=None):
        self.window.hide()
        return True

    def hasMenuItem(self):
        return True
