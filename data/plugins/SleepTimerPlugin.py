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

from Plugin import Plugin
from gi.repository import Gtk, GObject
from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF, APP_ICON_CONNECT, APP_INDICATOR_ICON_ON, APP_INDICATOR_ICON_OFF

class SleepTimerPlugin(Plugin):

    def __init__(self):
        super(SleepTimerPlugin, self).__init__()


    def initialize(self, name, eventManagerWrapper, eventSubscriber, provider, cfgProvider, mediator, tooltip):
    
        self.name = name
        self.eventManagerWrapper = eventManagerWrapper
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip
        self.menuItem = Gtk.CheckMenuItem(self.getName())
        self.menuItem.connect('activate', self.on_menu)
        self.menuItem.show()



    def activate(self):
        # sleep timer
        self.sleep_timer_id = None
        self.min_to_sleep = 0
        self.ignore_toggle = False
        
        self.min_to_sleep_selected = self.cfgProvider.getConfigValue("sleep_timer")
        if self.min_to_sleep_selected == None:
            self.min_to_sleep_selected = 15
            self.cfgProvider.setConfigValue("sleep_timer", str(self.min_to_sleep_selected))
        else:
            self.min_to_sleep_selected = int(self.min_to_sleep_selected)
        self.tooltip.addSource(self.populate_tooltip)

    def getName(self):
        return self.name

    def on_sleep_timer(self):
        self.min_to_sleep-=1       
                
        if self.min_to_sleep == 0:
            # set menu state
            self.ignore_toggle = True       
            self.menuItem.set_active(False)            
            self.ignore_toggle = False
            
            self.sleep_timer_id = None
            self.mediator.stop()
            self.eventManagerWrapper.notify(_("Sleep Timer"), _("Sleep timer expired"))
            self.tooltip.update()                                            
            return False
        
        self.tooltip.update()
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


    def populate_tooltip(self):
        if self.sleep_timer_id != None:
            return _("Sleep: %smin") % str(self.min_to_sleep)
        else:
            return None

    def start_sleep_timer(self, interval, display_msg):
        self.sleep_timer_id = GObject.timeout_add(interval*60000, self.on_sleep_timer)
        self.min_to_sleep = interval
        self.min_to_sleep_selected = interval        
        if display_msg:        
            self.eventManagerWrapper.notify(_("Sleep Timer"), _("%s minute sleep timer started") % str(interval))            
    
    def stop_sleep_timer(self, display_msg):
        GObject.source_remove(self.sleep_timer_id)
        self.sleep_timer_id = None  
        if display_msg:                   
            self.eventManagerWrapper.notify(_("Sleep Timer"), _("Sleep timer stopped"))


    def get_sleep_timer_value(self, default_value):

        #Gdk.threads_enter()
        dialog = Gtk.Dialog(_("Edit Sleep Timer"), None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
                        
        entry = Gtk.Entry()
        entry.set_max_length(4)
        entry.set_text(str(default_value)) 
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_("Minutes:")), False, 5, 5)
        hbox.pack_end(entry, True, True, 5)
        dialog.vbox.pack_end(hbox, True, True, 20)
        dialog.set_icon_from_file(APP_ICON_ON)
        dialog.show_all()
        
        ret = dialog.run()
                        
        sleep_timer_value = 0
        
        if ret == Gtk.ResponseType.ACCEPT:
            if entry.get_text().isdigit():
                sleep_timer_value = int(entry.get_text())
                
        dialog.destroy()
        
        #Gdk.threads_leave()
        return sleep_timer_value

    def on_menu(self, data):

        if self.ignore_toggle:
            return
                
        state = self.menuItem.get_active()
        
        if state:
            if self.sleep_timer_id == None:
                
                sleep_timer_val = self.get_sleep_timer_value(self.min_to_sleep_selected)

                if sleep_timer_val > 0:
                    self.start_sleep_timer(sleep_timer_val, True)
                    self.cfgProvider.setConfigValue("sleep_timer", str(sleep_timer_val))
                else:
                    state = False
        else:
            self.stop_sleep_timer(True)

        # set menu state
        self.ignore_toggle = True
        self.menuItem.set_active(state)
        self.ignore_toggle = False                
        self.tooltip.update()
    

    def hasMenuItem(self):
        return True
