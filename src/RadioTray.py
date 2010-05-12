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
from ConsoleLog import ConsoleLog
from XmlDataProvider import XmlDataProvider
from AudioPlayerGStreamer import AudioPlayerGStreamer
from SysTray import SysTray
from StateMediator import StateMediator
from Notification import Notification
from DbusFacade import DbusFacade
import os
from shutil import move, copy2
from lib.common import APPDIRNAME, USER_CFG_PATH, CFG_NAME, OLD_USER_CFG_PATH, DEFAULT_RADIO_LIST
import mpris

class RadioTray(object):

    def __init__(self, url=None):

        # load configuration
        self.loadConfiguration()

        # load notification engine
        notification = Notification()

        # load log engine
        self.log = ConsoleLog()

        # load bookmarks data provider and initializes it
        self.provider = XmlDataProvider(self.filename)
        self.provider.loadFromFile()

        # mediator
        self.mediator = StateMediator(self.provider, notification)

        # load audio player
        self.audio = AudioPlayerGStreamer(self.mediator, self.log)

        # load gui
        self.systray = SysTray(self.mediator, self.provider, self.log)

        # config mediator
        self.mediator.setAudioPlayer(self.audio)
        self.mediator.setSystray(self.systray)

        # start dbus facade
        dbus = DbusFacade(self.provider, self.mediator)
        dbus_mpris = mpris.RadioTrayMpris(self.provider, self.mediator)

        if(url != None):
            self.mediator.playUrl(url)

        # start app
        self.systray.run()


    def loadConfiguration(self):
        print "Loading configuration..."

        if not os.path.exists(USER_CFG_PATH):
            print "user's directory created"
            os.mkdir(USER_CFG_PATH)

        self.filename = os.path.join(USER_CFG_PATH, CFG_NAME)
        print self.filename

        if(os.access(self.filename, os.R_OK|os.W_OK) == False):

            #check if it exists an old bookmark file, and then move it to the new location
            oldfilename = os.path.join(OLD_USER_CFG_PATH, CFG_NAME)
            if(os.access(oldfilename, os.R_OK|os.W_OK) == True):

                print 'Old bookmark configuration moved to new location: ' + USER_CFG_PATH
                move(oldfilename, self.filename)
                os.rmdir(OLD_USER_CFG_PATH)

            else:
                copy2(DEFAULT_RADIO_LIST, self.filename)

if __name__ == "__main__":
        radio = RadioTray()
