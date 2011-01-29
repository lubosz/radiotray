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
from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF, APP_ICON_CONNECT
from lib import i18n
from about import AboutDialog
from lib.utils import html_escape
from events.EventManager import EventManager

import dbus

class OneWindow(object):
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

about = OneWindow(AboutDialog)

def about_dialog(parent=None):
    about.show(parent)

class SysTray(object):

    def __init__(self, mediator, provider, log, cfg_provider, eventManager):

        self.version = APPVERSION
        self.mediator = mediator
        self.eventManager = eventManager

        # initialize data provider
        self.provider = provider
        self.cfg_provider = cfg_provider

        # radios menu
        self.radioMenu = gtk.Menu()
        self.turnOff = gtk.MenuItem(_("Turned Off"))
        self.turnOff.connect('activate', self.on_turn_off)
        self.turnOff.set_sensitive(False)
        self.update_radios()

        # config menu
        self.menu = gtk.Menu()
        self.turnOff2 = gtk.MenuItem(_("Turned Off"))
        self.turnOff2.connect('activate', self.on_turn_off)
        self.turnOff2.set_sensitive(False)
        separator  = gtk.MenuItem()
        self.sleep_timer_menu = gtk.CheckMenuItem(_("Sleep Timer"))
        menu_item1 = gtk.MenuItem(_("Configure Radios..."))
        menu_item4 = gtk.MenuItem(_("Reload Bookmarks"))        
        menu_item3 = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        menu_item2 = gtk.ImageMenuItem(gtk.STOCK_QUIT)        
        self.menu.append(self.turnOff2)
        self.menu.append(separator) 
        self.menu.append(self.sleep_timer_menu)       
        self.menu.append(menu_item1)
        self.menu.append(menu_item4)        
        self.menu.append(gtk.MenuItem())        
        self.menu.append(menu_item3)
        self.menu.append(menu_item2)        
        menu_item1.show()
        menu_item2.show()
        menu_item3.show()
        menu_item4.show()
        self.sleep_timer_menu.show()
        self.turnOff2.show()
        separator.show()      
        
        menu_item1.connect('activate', self.on_preferences)
        menu_item2.connect('activate', self.on_quit)
        menu_item3.connect('activate', self.on_about)
        menu_item4.connect('activate', self.reload_bookmarks)
        #self.sleep_timer_menu.connect('activate', self.on_sleep_menu)
                        
        self.menu.show_all()

        self.icon = gtk.status_icon_new_from_file(APP_ICON_OFF)
        self.icon.set_tooltip_markup(_("Idle (vol: %s%%)") % (self.mediator.getVolume()))
        self.icon.connect('button_press_event', self.button_press)
        self.icon.connect('scroll_event', self.scroll)

        # sleep timer
        self.sleep_timer_id = None
        self.min_to_sleep = 0
        
        self.min_to_sleep_selected = self.cfg_provider.getConfigValue("sleep_timer")
        if self.min_to_sleep_selected == None:
            self.min_to_sleep_selected = 15
            self.cfg_provider.setConfigValue("sleep_timer", str(self.min_to_sleep_selected))
        else:
            self.min_to_sleep_selected = int(self.min_to_sleep_selected)
            
        self.ignore_toggle = False

        # MediaKeys
        
            
            
###### Action Events #######

    def scroll(self,widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.mediator.volume_up()
            
        if event.direction == gtk.gdk.SCROLL_DOWN:
            self.mediator.volume_down()

    def button_press(self,widget,event):

        if(event.button == 1):
            self.radioMenu.popup(None, None, gtk.status_icon_position_menu, 0, event.get_time(), widget)
        elif (event.button == 2):
            if (self.mediator.getContext().state == 'playing'):
                self.mediator.stop()
            else:
                if self.mediator.getContext().station:
                    self.mediator.play(self.mediator.getContext().station)
        else:
            self.menu.popup(None, None, gtk.status_icon_position_menu, 2, event.get_time(), widget)

    

    def on_preferences(self, data):
        config = BookmarkConfiguration(self.provider, self.update_radios)

    def on_quit(self, data):
        print 'Exiting...'
        gtk.main_quit()

    def on_about(self, data):
        about_dialog(parent=None)

    def on_turn_off(self, data):
        self.mediator.stop()

    def on_start(self, data, radio):
        self.mediator.play(radio)
    
        
    def on_sleep_timer(self):
        self.min_to_sleep-=1       
                
        if self.min_to_sleep == 0:
            # set menu state
            self.ignore_toggle = True       
            self.sleep_timer_menu.set_active(False)            
            self.ignore_toggle = False
            
            self.sleep_timer_id = None
            self.mediator.stop()
            self.mediator.notify("Sleep timer expired")
            self.updateTooltip()                                            
            return False
        
        self.updateTooltip()
        return True
                
    def on_sleep_menu(self, menu_item):        
                                                         
        if self.ignore_toggle:
            return
                
        state = menu_item.get_active()
        
        if state:
            if self.sleep_timer_id == None:
                
                sleep_timer_val = self.get_sleep_timer_value(self.min_to_sleep_selected)

                if sleep_timer_val > 0:
                    self.start_sleep_timer(sleep_timer_val, True)
                    self.cfg_provider.setConfigValue("sleep_timer", str(sleep_timer_val))
                else:
                    state = False
        else:
            self.stop_sleep_timer(True)

        # set menu state
        self.ignore_toggle = True
        menu_item.set_active(state)
        self.ignore_toggle = False                
        self.updateTooltip()


    def start_sleep_timer(self, interval, display_msg):
        self.sleep_timer_id = gobject.timeout_add(60000, self.on_sleep_timer)
        self.min_to_sleep = interval
        self.min_to_sleep_selected = interval        
        if display_msg:        
            self.mediator.notify(str(interval) + " minute sleep timer started")            
    
    def stop_sleep_timer(self, display_msg):
        gobject.source_remove(self.sleep_timer_id)
        self.sleep_timer_id = None  
        if display_msg:                   
            self.mediator.notify("Sleep timer stopped")



    def updateTooltip(self):
        radio = html_escape(self.mediator.getContext().station)
        songInfo = html_escape(self.mediator.getContext().getSongInfo())
        
        volume = self.mediator.getVolume()
        
        sleep_timer_info = ""
        if self.sleep_timer_id != None:
            sleep_timer_info = ", sleep: " + str(self.min_to_sleep) + "min"
        
        if (self.mediator.getContext().state == 'playing'):
            if(songInfo):
                self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%%s)\n<i>%s</i>") % (radio, volume, sleep_timer_info, songInfo))
            else:
                self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%%s)") % (radio, volume, sleep_timer_info))
        else:
            self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Idle (vol: %s%%%s)") % (volume, sleep_timer_info))
		


    def update_radios(self):

        for child in self.radioMenu.get_children():
            self.radioMenu.remove(child)

        self.radioMenu.append(self.turnOff)
        self.turnOff.show()

        separator = gtk.MenuItem()
        self.radioMenu.append(separator)
        separator.show()

        # build menu
        self.provider.walk_bookmarks(self.group_callback, self.bookmark_callback, self.radioMenu)
        self.radioMenu.show_all()

        
    def run(self):
        gtk.gdk.threads_init()
        gtk.main()


    def group_callback(self, group_name, user_data):

        new_user_data = None
        
        if group_name != 'root':
            group = gtk.MenuItem(group_name)
            user_data.append(group)  
            new_user_data = gtk.Menu()
            group.set_submenu(new_user_data)
        else:
            new_user_data = self.radioMenu
            
        return new_user_data


    def bookmark_callback(self, radio_name, user_data):

        if radio_name.startswith("[separator-"):
            separator = gtk.MenuItem()
            user_data.append(separator)
            separator.show()
        else:         
            radio = gtk.MenuItem(radio_name)
            radio.show()
            radio.connect('activate', self.on_start, radio_name)
            user_data.append(radio)

            
    def reload_bookmarks(self, data):
        self.provider.loadFromFile()
        self.update_radios()
        self.eventManager.notify(EventManager.BOOKMARKS_RELOADED, {})
        

    def get_sleep_timer_value(self, default_value):

        dialog = gtk.Dialog("Edit Sleep Timer", None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
                        
        entry = gtk.Entry(4)       
        entry.set_text(str(default_value)) 
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Minutes:"), False, 5, 5)
        hbox.pack_end(entry, True, True, 5)
        dialog.vbox.pack_end(hbox, True, True, 20)
        dialog.set_icon_from_file(APP_ICON_ON)
        dialog.show_all()
        
        ret = dialog.run()
                        
        sleep_timer_value = 0
        
        if ret == gtk.RESPONSE_ACCEPT:
            if entry.get_text().isdigit():
                sleep_timer_value = int(entry.get_text())
                
        dialog.destroy()
        
        return sleep_timer_value
    
    
    def on_state_changed(self, data):
    
        state = data['state']
        
        
        if(state == 'playing'):
            station = data['station']
            self.turnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % station)
            self.turnOff.set_sensitive(True)
            self.turnOff2.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % station)
            self.turnOff2.set_sensitive(True)
            self.icon.set_from_file(APP_ICON_ON)
            self.updateTooltip()
            
        elif(state == 'paused'):
            self.turnOff.set_label(_('Turned Off'))
            self.turnOff.set_sensitive(False)
            self.turnOff2.set_label(_('Turned Off'))
            self.turnOff2.set_sensitive(False)
            self.icon.set_from_file(APP_ICON_OFF)
            self.updateTooltip()
        
        elif(state == 'connecting'):
            station = data['station']
            self.turnOff.set_sensitive(True)
            self.turnOff2.set_sensitive(True)
            self.icon.set_tooltip_markup(C_("Connecting to a music stream.", "Connecting to %s") % station.replace("&", "&amp;"))
            self.icon.set_from_file(APP_ICON_CONNECT)

    def on_volume_changed(self, volume):
        self.updateTooltip()
        
