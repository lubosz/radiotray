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

class SleepTimerPlugin(Plugin):

    def __init__(self):
        super(SleepTimerPlugin, self).__init__()

    def activate(self):
        # sleep timer
        self.sleep_timer_id = None
        self.min_to_sleep = 0
        
        self.min_to_sleep_selected = self.cfgProvider.getConfigValue("sleep_timer")
        if self.min_to_sleep_selected == None:
            self.min_to_sleep_selected = 15
            self.cfgProvider.setConfigValue("sleep_timer", str(self.min_to_sleep_selected))
        else:
            self.min_to_sleep_selected = int(self.min_to_sleep_selected)


    def getName(self):
        return self.name

    def on_sleep_timer(self):
        self.min_to_sleep-=1       
                
        if self.min_to_sleep == 0:
            # set menu state
            self.ignore_toggle = True       
            self.sleep_timer_menu_item.set_active(False)            
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


    def get_sleep_timer_value(self, default_value):
        gtk.gdk.threads_enter()

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
        
        gtk.gdk.threads_leave()
        return sleep_timer_value

    def on_menu(self, data):
        print "menu clicked!"
    
