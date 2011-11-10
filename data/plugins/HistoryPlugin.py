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
from lib import utils
from lib.common import SYSTEM_PLUGIN_PATH, USER_PLUGIN_PATH
import os

class HistoryPlugin(Plugin):

    def __init__(self):
        super(HistoryPlugin, self).__init__()


    def getName(self):
        return self.name



    def activate(self):
        self.eventSubscriber.bind(EventManager.SONG_CHANGED, self.on_song_changed)

        if os.path.exists(os.path.join(USER_PLUGIN_PATH, "history.glade")):
            self.gladefile = utils.load_ui_file(os.path.join(USER_PLUGIN_PATH, "history.glade"))
        elif os.path.exists(os.path.join(SYSTEM_PLUGIN_PATH, "history.glade")):
            self.gladefile = utils.load_ui_file(os.path.join(SYSTEM_PLUGIN_PATH, "history.glade"))
        else:
            self.log.error('Error initializing History plugin: history.glade not found')

        self.text = self.gladefile.get_object('textview1')
        self.window = self.gladefile.get_object("dialog1")
        self.last_title = 'none'

        if (self.window):
            #dic = { "on_close_clicked" : self.on_close_clicked}
            self.gladefile.connect_signals(self)


    def on_song_changed(self, data):

        if('title' in data.keys()):
            title = data['title']
            if title != self.last_title:
                self.last_title = title
                buffer = self.text.get_buffer()
                buffer.insert(buffer.get_end_iter(),title+'\n')


    def on_menu(self, data):
        self.window.run()

    def on_close_clicked(self, widget):
        self.window.hide()

    def hasMenuItem(self):
        return True
