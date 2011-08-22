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
import sys,os
import time
try:
    import pygtk
    pygtk.require("2.1")
    import gtk
except:
    pass
try:
    import gtk
    import gtk.glade
    import gobject
except:
    sys.exit(1)

from AudioPlayerGStreamer import AudioPlayerGStreamer
from XmlDataProvider import XmlDataProvider
from BookmarkConfiguration import BookmarkConfiguration
from PluginConfiguration import PluginConfiguration
from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF, APP_ICON_CONNECT, APP_INDICATOR_ICON_ON, APP_INDICATOR_ICON_OFF
from lib import i18n
from about import AboutDialog
from lib.utils import html_escape
from GuiChooserConfiguration import GuiChooserConfiguration
from events.EventManager import EventManager
from SysTrayGui import SysTrayGui
from AppIndicatorGui import AppIndicatorGui
from TooltipManager import TooltipManager
from Context import Context

import dbus
import textwrap

class AboutWindow(object):
    def __init__(self, dialog_class):
        self.dialog = None
        self.dialog_class = dialog_class

    def on_dialog_destroy(self):
        self.dialog = None

    def show(self, parent = None):
        if self.dialog:
            self.dialog.present()
        else:
            if parent:
                self.dialog = self.dialog_class(parent)
            else:
                self.dialog = self.dialog_class()
            self.dialog.connect("destroy", lambda *args: self.on_dialog_destroy())

about = AboutWindow(AboutDialog)

def about_dialog(parent=None):
    about.show(parent)



class SysTray(object):

    def __init__(self, mediator, provider, log, cfg_provider, default_cfg_provider, eventManager, tooltipManager):

        self.version = APPVERSION
        self.mediator = mediator
        self.eventManager = eventManager

        # initialize data provider
        self.provider = provider
        self.cfg_provider = cfg_provider
        self.tooltip = tooltipManager
        
            
        self.ignore_toggle = False

        # execute gui chooser
        self.gui_engine = self.cfg_provider.getConfigValue("gui_engine")
        if(self.gui_engine == None):
            self.gui_engine = default_cfg_provider.getConfigValue("gui_engine")
 
        if(self.gui_engine == None or self.gui_engine == "chooser"):
            print "show chooser"
            chooser = GuiChooserConfiguration()
            self.gui_engine = chooser.run()

        self.cfg_provider.setConfigValue("gui_engine", self.gui_engine)




        if self.gui_engine == "appindicator":
            self.app_indicator_enabled  = True
        else:
            self.app_indicator_enabled = False
            self.cfg_provider.setConfigValue("enable_application_indicator_support", "false")

        if(self.app_indicator_enabled):
            self.gui = AppIndicatorGui(self, self.mediator, self.cfg_provider, self.provider)
  
        else:
            self.gui = SysTrayGui(self, self.mediator, self.cfg_provider, self.provider)
        
        self.tooltip.setGui(self.gui)
        self.tooltip.addSource(self.gui.getCommonTooltipData)

        self.gui.buildMenu()
        
            
###### Action Events #######

    def scroll(self,widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.mediator.volume_up()
            
        if event.direction == gtk.gdk.SCROLL_DOWN:
            self.mediator.volume_down()
    def volume_up(self, menu_item):
        self.mediator.volume_up()
    def volume_down(self, menu_item):
        self.mediator.volume_down()

    

    def on_preferences(self, data):
        config = BookmarkConfiguration(self.provider, self.update_radios)

    def on_quit(self, data):
        print 'Exiting...'
        gtk.main_quit()

    def on_about(self, data):
        about_dialog(parent=None)

    def on_turn_on_off(self, data):
        if self.mediator.context.state == 'playing':
            self.mediator.stop()
        else:
            self.mediator.play(self.mediator.context.station)

    def on_start(self, data, radio):
        self.mediator.play(radio)
    
        
    def updateTooltip(self):
        self.tooltip.update()
    
    

		

    def update_radios(self):
        self.gui.update_radios()
    
        
    def run(self):
        gtk.gdk.threads_init()
        gtk.main()


    

            
    def reload_bookmarks(self, data):
        self.provider.loadFromFile()
        self.update_radios()
        self.eventManager.notify(EventManager.BOOKMARKS_RELOADED, {})
        

    
    def on_state_changed(self, data):

        if(data['state'] == Context.STATE_PAUSED and self.mediator.context.station == Context.UNKNOWN_RADIO):
            self.mediator.context.station = ''

        self.gui.state_changed(data)
        self.updateTooltip()

    def on_volume_changed(self, volume):
        self.updateTooltip()
      
    def on_song_changed(self, data):
        self.updateTooltip()


    def on_plugin_preferences(self, data):
        config = PluginConfiguration(self.pluginManager, self.cfg_provider)


    def getPluginMenu(self):
        return self.gui.getPluginMenu()

    def setPluginManager(self, pluginManager):
        self.pluginManager = pluginManager
        
