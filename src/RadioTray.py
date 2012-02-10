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
from XmlDataProvider import XmlDataProvider
from XmlConfigProvider import XmlConfigProvider
from AudioPlayerGStreamer import AudioPlayerGStreamer
from SysTray import SysTray
from StateMediator import StateMediator
from NotificationManager import NotificationManager
from events.EventManager import EventManager
from events.EventMngNotificationWrapper import EventMngNotificationWrapper
from events.EventSubscriber import EventSubscriber
from DbusFacade import DbusFacade
from TooltipManager import TooltipManager
from PluginManager import PluginManager
import os
from shutil import move, copy2
from lib.common import APPDIRNAME, USER_CFG_PATH, CFG_NAME, OLD_USER_CFG_PATH,\
    DEFAULT_RADIO_LIST, OPTIONS_CFG_NAME, DEFAULT_CONFIG_FILE,\
    USER_PLUGIN_PATH, LOGFILE
import mpris
from GuiChooserConfiguration import GuiChooserConfiguration
import logging
from logging import handlers

class RadioTray(object):

    def __init__(self, url=None):
        
        self.loadConfiguration()
        
        self.logger.info('Starting Radio Tray...')

        # load configuration
        
        # load bookmarks data provider and initializes it
        self.provider = XmlDataProvider(self.filename)
        self.provider.loadFromFile()

        # load config data provider and initializes it
        self.cfg_provider = XmlConfigProvider(self.cfg_filename)
        self.cfg_provider.loadFromFile()

        # load default config data provider and initializes it
        self.default_cfg_provider = XmlConfigProvider(self.default_cfg_filename)
        self.default_cfg_provider.loadFromFile()

        # load Event Manager
        eventManager = EventManager()
        eventManagerWrapper = EventMngNotificationWrapper(eventManager)

        # mediator
        self.mediator = StateMediator(self.provider, self.cfg_provider, eventManager)

        # load audio player
        self.audio = AudioPlayerGStreamer(self.mediator, self.cfg_provider, eventManager)

        # tooltip manager
        tooltipManager = TooltipManager()

        # chooser
        if(url == '--config'):
            chooser = GuiChooserConfiguration()
            gui_engine = chooser.run()
            self.cfg_provider.setConfigValue("gui_engine", gui_engine)
            url = None
        # load gui
        self.systray = SysTray(self.mediator, self.provider, self.cfg_provider, self.default_cfg_provider, eventManager, tooltipManager)
        
        
        
        # notification manager
        self.notifManager = NotificationManager(eventManagerWrapper)

        # bind events
        eventSubscriber = EventSubscriber(eventManager)
        eventSubscriber.bind(EventManager.STATE_CHANGED, self.mediator.on_state_changed)
        eventSubscriber.bind(EventManager.STATE_CHANGED, self.systray.on_state_changed)
        eventSubscriber.bind(EventManager.STATE_CHANGED, self.notifManager.on_state_changed)
        eventSubscriber.bind(EventManager.SONG_CHANGED, self.notifManager.on_song_changed)
        eventSubscriber.bind(EventManager.SONG_CHANGED, self.mediator.on_song_changed)
        eventSubscriber.bind(EventManager.SONG_CHANGED, self.systray.on_song_changed)
        eventSubscriber.bind(EventManager.STATION_ERROR, self.notifManager.on_station_error)
        eventSubscriber.bind(EventManager.VOLUME_CHANGED, self.systray.on_volume_changed)
        eventSubscriber.bind(EventManager.BOOKMARKS_RELOADED, self.notifManager.on_bookmarks_reloaded)

        # config mediator
        self.mediator.init(self.audio)


        # start dbus facade
        dbus = DbusFacade(self.provider, self.mediator)
        #dbus_mpris = mpris.RadioTrayMpris(self.provider, self.mediator)

	#load plugin manager
        self.pluginManager = PluginManager(eventManagerWrapper, eventSubscriber, self.provider, self.cfg_provider, self.mediator, tooltipManager, self.systray.getPluginMenu())
        self.systray.setPluginManager(self.pluginManager)
        self.pluginManager.discoverPlugins()
        self.pluginManager.activatePlugins()

        if(url != None):
            if (url == "--resume"):
                self.mediator.playLast()                
            else:
                self.mediator.playUrl(url)
        # start app
        self.systray.run()


    def loadConfiguration(self):

        if not os.path.exists(USER_CFG_PATH):
            #self.logger.info("user's directory created")
            os.mkdir(USER_CFG_PATH)
            
        if not os.path.exists(USER_PLUGIN_PATH):
            os.mkdir(USER_PLUGIN_PATH)
        
        self.configLogging()
        
        self.logger.debug("Loading configuration...")
        
        self.filename = os.path.join(USER_CFG_PATH, CFG_NAME)

        self.cfg_filename = os.path.join(USER_CFG_PATH, OPTIONS_CFG_NAME)

        self.default_cfg_filename = DEFAULT_CONFIG_FILE

        if not os.access(self.filename, os.F_OK): # If bookmarks file doesn't exist

            self.logger.warn('bookmarks file could not be found. Using default...')

            #check if it exists an old bookmark file, and then move it to the new location
            oldfilename = os.path.join(OLD_USER_CFG_PATH, CFG_NAME)
            if os.access(oldfilename, os.R_OK|os.W_OK):

                self.logger.info('Found old bookmark configuration and moved it to new location: %s', USER_CFG_PATH)
                move(oldfilename, self.filename)
                os.rmdir(OLD_USER_CFG_PATH)

            else:
                self.logger.info('Copying default bookmarks file to user directory')
                copy2(DEFAULT_RADIO_LIST, self.filename)

        if not os.access(self.cfg_filename, os.R_OK|os.W_OK):

            self.logger.warn('Configuration file not found. Copying default configuration file to user directory')
            copy2(DEFAULT_CONFIG_FILE, self.cfg_filename)


    def configLogging(self):
        # config logging
        self.logger = logging.getLogger('radiotray')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=2000000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

if __name__ == "__main__":
        radio = RadioTray()
