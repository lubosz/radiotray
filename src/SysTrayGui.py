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

from gi.repository import Gtk

from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF, APP_ICON_CONNECT, APP_INDICATOR_ICON_ON, APP_INDICATOR_ICON_OFF
from lib.utils import html_escape

# This class handles the gui for the systray mode
class SysTrayGui:

    def __init__(self, handler, mediator, cfg_provider, provider):
        self.handler = handler
        self.mediator = mediator
        self.cfg_provider = cfg_provider
        self.provider = provider


    def buildMenu(self):
        
        # radios menu
        self.radioMenu = Gtk.Menu()
            
        if not self.mediator.context.station:
            self.turnOnOff = Gtk.MenuItem(_("Turned Off"))
            self.turnOnOff2 = Gtk.MenuItem(_("Turned Off"))
            self.turnOnOff.set_sensitive(False)
            self.turnOnOff2.set_sensitive(False)
        else:
            self.turnOnOff = Gtk.MenuItem(_('Turn On "%s"') % self.mediator.context.station)
            self.turnOnOff.set_sensitive(True)
            self.turnOnOff2 = Gtk.MenuItem(_('Turn On "%s"') % self.mediator.context.station)
            self.turnOnOff2.set_sensitive(True)
            
        self.turnOnOff.connect('activate', self.handler.on_turn_on_off)
        self.turnOnOff2.connect('activate', self.handler.on_turn_on_off)
        self.update_radios()

        # config menu
        self.menu = Gtk.Menu()
        self.turnOnOff2 = Gtk.MenuItem(_("Turned Off"))
        self.turnOnOff2.connect('activate', self.handler.on_turn_on_off)
        self.turnOnOff2.set_sensitive(False)
        separator  = Gtk.MenuItem()
        menu_item1 = Gtk.MenuItem(_("Configure Radios..."))

        #Check bookmarks file status
        menu_item1.set_sensitive(self.provider.isBookmarkWritable())

        menu_item4 = Gtk.MenuItem(_("Reload Bookmarks"))
        menu_item3 = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ABOUT, None)
        menu_item2 = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_QUIT, None)
        self.menu.append(self.turnOnOff2)
        self.menu.append(separator)  
        self.menu.append(menu_item1)

        # plugins sub-menu
        menu_plugins_item = Gtk.MenuItem("Plugins")
        self.menu_plugins = Gtk.Menu()
        menu_plugins_item.set_submenu(self.menu_plugins)
        menu_item5 = Gtk.MenuItem(_("Configure Plugins..."))
        self.menu_plugins.append(menu_item5)
        self.menu_plugins.append(Gtk.MenuItem())    #add separator
        self.menu.append(menu_plugins_item) 

        self.menu.append(menu_item4)        
        self.menu.append(Gtk.MenuItem())
        self.menu.append(menu_item3)
        self.menu.append(menu_item2)        
        menu_item1.show()
        menu_item2.show()
        menu_item3.show()
        menu_item4.show()
        self.turnOnOff2.show()
        separator.show()   

          
        # set handlers for menu items
        
        menu_item1.connect('activate', self.handler.on_preferences)
        menu_item2.connect('activate', self.handler.on_quit)
        menu_item3.connect('activate', self.handler.on_about)
        menu_item4.connect('activate', self.handler.reload_bookmarks)
        menu_item5.connect('activate', self.handler.on_plugin_preferences)
                        
        self.menu.show_all()

        self.icon = Gtk.StatusIcon.new_from_file(APP_ICON_OFF)
        self.icon.set_tooltip_markup(_("Idle (vol: %s%%)") % (self.mediator.getVolume()))
        self.icon.connect('button_press_event', self.button_press)
        self.icon.connect('scroll_event', self.handler.scroll)

    def button_press(self,widget,event):
        if(event.button == 1):
            self.radioMenu.popup(None, None, Gtk.StatusIcon.position_menu, widget, event.button, event.get_time())
        elif (event.button == 2):
            if (self.mediator.getContext().state == 'playing'):
                self.mediator.stop()
            else:
                if self.mediator.getContext().station:
                    self.mediator.play(self.mediator.getContext().station)
        else:
            self.menu.popup(None, None, Gtk.StatusIcon.position_menu, widget, event.button, event.get_time())


    def update_radios(self):
        for child in self.radioMenu.get_children():
            self.radioMenu.remove(child)

        self.radioMenu.append(self.turnOnOff)
        self.turnOnOff.show()

        separator = Gtk.MenuItem()
        self.radioMenu.append(separator)
        separator.show()

        # build menu
        self.provider.walk_bookmarks(self.group_callback, self.bookmark_callback, self.radioMenu)
        self.radioMenu.show_all()

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
            
            self.turnOnOff2.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % station)
            self.turnOnOff2.set_sensitive(True)
            self.icon.set_from_file(APP_ICON_ON)
            
        elif(state == 'paused'):
            if not self.mediator.context.station:
                self.turnOnOff.set_label(_('Turned Off'))
                self.turnOnOff.set_sensitive(False)
                self.turnOnOff2.set_label(_('Turned Off'))
                self.turnOnOff2.set_sensitive(False)
            else:
                self.turnOnOff.set_label(_('Turn On "%s"') % self.mediator.context.station)
                self.turnOnOff.set_sensitive(True)
                self.turnOnOff2.set_label(_('Turn On "%s"') % self.mediator.context.station)
                self.turnOnOff2.set_sensitive(True)

            self.icon.set_from_file(APP_ICON_OFF)
        
        elif(state == 'connecting'):
            station = data['station']
            self.turnOnOff.set_sensitive(True)
            self.turnOnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % station)
            
            self.turnOnOff2.set_sensitive(True)
            self.icon.set_tooltip_markup(C_("Connecting to a music stream.", "Connecting to %s") % station.replace("&", "&amp;"))
            self.icon.set_from_file(APP_ICON_CONNECT)


    def setTooltip(self, text):
        self.icon.set_tooltip_markup(text)


    def getCommonTooltipData(self):

        radio = html_escape(self.mediator.getContext().station)
        songInfo = html_escape(self.mediator.getContext().getSongInfo())
        volume = self.mediator.getVolume()

        if (self.mediator.getContext().state == 'playing'):
            if(songInfo):
                return C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%)\n<i>%s</i>") % (radio, volume, songInfo)
            else:
                return C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%)") % (radio, volume)
        else:
            return C_("Informs Radio Tray is idle as a tooltip.", "Idle (vol: %s%%)") % (volume)


    def getPluginMenu(self):
        return self.menu_plugins
