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
import sys
from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF, APP_ICON_CONNECT, APP_INDICATOR_ICON_ON, APP_INDICATOR_ICON_OFF, APP_INDICATOR_ICON_CONNECT, IMAGE_PATH

from gi.repository import Gtk

import textwrap
import logging

# This class handles the gui interface for the Ubuntu's app indicator API
class AppIndicatorGui:

    def __init__(self, handler, mediator, cfg_provider, provider):
        self.handler = handler
        self.mediator = mediator
        self.cfg_provider = cfg_provider
        self.provider = provider
        self.log = logging.getLogger('radiotray')


    def buildMenu(self):

        try:            
            import appindicator
            self.app_indicator = appindicator.Indicator(APPNAME, APP_INDICATOR_ICON_OFF , appindicator.CATEGORY_APPLICATION_STATUS)
            self.app_indicator.set_status(appindicator.STATUS_ACTIVE)
        except Exception as e:
            self.log.debug(e)
            self.log.warn("Failed to create an Application Indicator!")
            self.app_indicator = None

        self.app_indicator.set_icon_theme_path(IMAGE_PATH)
        self.turnOnOff = None
        self.metadata_menu_item = None
        self.perferences_submenu = None
        self.preferences_menu = None            
        self.radioMenu = Gtk.Menu()
        self.build_app_indicator_menu(self.radioMenu)
        self.app_indicator.set_menu(self.radioMenu)
        self.handler.updateTooltip()


    def build_app_indicator_menu(self, menu):

        # config menu   
        if self.turnOnOff == None:                        
            if not self.mediator.context.station:
                self.turnOnOff = Gtk.MenuItem(_("Turned Off"))
                self.turnOnOff.set_sensitive(False)
            else:
                self.turnOnOff = Gtk.MenuItem(_('Turn On "%s"') % self.mediator.context.station)
                self.turnOnOff.set_sensitive(True)
                
            self.turnOnOff.connect('activate', self.handler.on_turn_on_off)
            
            
        # stream metadata info
        if self.metadata_menu_item == None:
            self.metadata_menu_item = Gtk.MenuItem("Idle")
            self.metadata_menu_item.set_sensitive(False)
        
        # if self.sleep_timer_menu_item == None:                        
        #     self.sleep_timer_menu_item = Gtk.CheckMenuItem(_("Sleep Timer"))
        
        if self.preferences_menu == None:
            self.preferences_menu = Gtk.ImageMenuItem(Gtk.STOCK_PREFERENCES)
        
        menu_config_radios = Gtk.MenuItem(_("Configure Radios..."))
        menu_reload_bookmarks = Gtk.MenuItem(_("Reload Bookmarks"))
        menu_config_plugin = Gtk.MenuItem(_("Configure Plugins..."))
        #Check bookmarks file status
        menu_config_radios.set_sensitive(self.provider.isBookmarkWritable())

        # build 
        menu.append(self.turnOnOff)
        menu.append(Gtk.MenuItem())
        menu.append(self.metadata_menu_item)
        menu.append(Gtk.MenuItem())
                
        self.provider.walk_bookmarks(self.group_callback, self.bookmark_callback, menu)
        
        menu_config_radios.connect('activate', self.handler.on_preferences)
        menu_reload_bookmarks.connect('activate', self.handler.reload_bookmarks)
        menu_config_plugin.connect('activate', self.handler.on_plugin_preferences)
   
                   
        menu.append(Gtk.MenuItem())
     
        # build preferences
        menu.append(self.preferences_menu)
        
        if self.perferences_submenu == None:  
            self.perferences_submenu = Gtk.Menu()
            self.preferences_menu.set_submenu(self.perferences_submenu)               
            #self.perferences_submenu.append(Gtk.MenuItem())
            self.perferences_submenu.append(menu_config_radios)
            self.perferences_submenu.append(menu_reload_bookmarks)

        # plugins submenu
        menu_plugins_item = Gtk.MenuItem("Plugins")
        self.menu_plugins = Gtk.Menu()
        self.menu_plugins.append(menu_config_plugin)
        self.menu_plugins.append(Gtk.MenuItem())	#add separator
        menu_plugins_item.set_submenu(self.menu_plugins)

        menu.append(menu_plugins_item)

        menu_about = Gtk.ImageMenuItem(Gtk.STOCK_ABOUT)
        menu_quit = Gtk.ImageMenuItem(Gtk.STOCK_QUIT)
        menu_quit.connect('activate', self.handler.on_quit)
        menu_about.connect('activate', self.handler.on_about)
        menu.append(menu_about)
        menu.append(menu_quit)

        menu.show_all()
        
        try:
            self.app_indicator.connect("scroll-event", self.app_indicator_scroll)
        except:
            # not available in this version of app indicator
            self.log.info("App indicator scroll events are not available.")


    def app_indicator_scroll(self, indicator, delta, direction):
        if direction == 0:
            self.mediator.volume_up()
        else:
            self.mediator.volume_down()


    def update_radios(self):
        for child in self.radioMenu.get_children():
            self.radioMenu.remove(child)

        self.build_app_indicator_menu(self.radioMenu)


    def group_callback(self, group_name, user_data):

        new_user_data = None
        
        if group_name != 'root':
            group = Gtk.MenuItem(group_name)
            user_data.append(group)  
            new_user_data = Gtk.Menu()
            group.set_submenu(new_user_data)
        else:
            new_user_data = self.radioMenu
            
        return new_user_data


    def bookmark_callback(self, radio_name, user_data):

        if radio_name.startswith("[separator-"):
            separator = Gtk.MenuItem()
            user_data.append(separator)
            separator.show()
        else:         
            radio = Gtk.MenuItem(radio_name)
            radio.show()
            radio.connect('activate', self.handler.on_start, radio_name)
            user_data.append(radio)



    def state_changed(self, data):

        state = data['state']

        if(state == 'playing'):
            station = data['station']
            self.turnOnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % station)
            self.turnOnOff.set_sensitive(True)
            
            self.app_indicator.set_icon(APP_INDICATOR_ICON_ON)
            
        elif(state == 'paused'):
            if not self.mediator.context.station:
                self.turnOnOff.set_label(_('Turned Off'))
                self.turnOnOff.set_sensitive(False)
            else:
                self.turnOnOff.set_label(_('Turn On "%s"' % self.mediator.context.station))
                self.turnOnOff.set_sensitive(True)
            
            self.app_indicator.set_icon(APP_INDICATOR_ICON_OFF)
        
        elif(state == 'connecting'):
            station = data['station']
            self.turnOnOff.set_sensitive(True)
            self.turnOnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % station)
            self.app_indicator.set_icon(APP_INDICATOR_ICON_CONNECT)


    def setTooltip(self, text):
        self.metadata_menu_item.set_label(text)

    def getCommonTooltipData(self):

        songInfo = self.mediator.getContext().getSongInfo()
        volume = self.mediator.getVolume()

        if (self.mediator.getContext().state == 'playing'):
            if(songInfo):
                otherInfo = "(vol: %s%%)" % (volume)         
                   
                # don't break volume info...
                text = textwrap.wrap(songInfo, 30)
                if (30 - len(text[-1])) >= (len(otherInfo)+1):
                    text[-1] += " " + otherInfo
                else:
                    text.append(otherInfo)
                        
                return "\n".join(text)
            else:
                return C_("Playing status tooltip information", "Playing (vol: %s%%)") % (volume)
        else:
            return C_("Informs Radio Tray is idle as a tooltip.", "Idle (vol: %s%%)") % (volume)


    def getPluginMenu(self):
        return self.menu_plugins
