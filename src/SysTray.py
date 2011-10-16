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
from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF, APP_ICON_CONNECT, APP_INDICATOR_ICON_ON, APP_INDICATOR_ICON_OFF
from lib import i18n
from about import AboutDialog
from lib.utils import html_escape
from GuiChooserConfiguration import GuiChooserConfiguration

import dbus
import textwrap

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

    def __init__(self, mediator, provider, log, cfg_provider, default_cfg_provider):

        self.version = APPVERSION
        self.mediator = mediator

        # initialize data provider
        self.provider = provider
        self.cfg_provider = cfg_provider

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

        self.app_indicator_use_theme = self.cfg_provider.getConfigValue("enable_application_indicator_theme_support")
        if self.app_indicator_use_theme == None:
            self.app_indicator_use_theme = False
            self.cfg_provider.setConfigValue("enable_application_indicator_theme_support", "false")
        else:
            self.app_indicator_use_theme = (self.app_indicator_use_theme == "true")
                
        if self.app_indicator_enabled:
            try:            
                import appindicator
                self.app_indicator = appindicator.Indicator(APPNAME,
                                                            APP_INDICATOR_ICON_OFF if self.app_indicator_use_theme else APP_ICON_OFF,
                                                            appindicator.CATEGORY_APPLICATION_STATUS)
                self.app_indicator.set_status(appindicator.STATUS_ACTIVE)
            except:
                print "Failed to create an Application Indicator!" 
                self.app_indicator = None
        else:
            self.app_indicator = None
        
        # should we use the old menu?
        if not self.app_indicator:    
            # radios menu
            self.radioMenu = gtk.Menu()
            
            if not self.mediator.currentRadio:
                self.turnOnOff = gtk.MenuItem(_("Turned Off"), False)
                self.turnOnOff2 = gtk.MenuItem(_("Turned Off"), False)
                self.turnOnOff.set_sensitive(False)
                self.turnOnOff2.set_sensitive(False)
            else:
                self.turnOnOff = gtk.MenuItem(_('Turn On "%s"') % self.mediator.currentRadio, False)
                self.turnOnOff.set_sensitive(True)
                self.turnOnOff2 = gtk.MenuItem(_('Turn On "%s"') % self.mediator.currentRadio, False)                
                self.turnOnOff2.set_sensitive(True)
            
            self.turnOnOff.connect('activate', self.on_turn_on_off)
            self.turnOnOff2.connect('activate', self.on_turn_on_off)
            self.update_radios()
    
            # config menu
            self.menu = gtk.Menu()
            separator  = gtk.MenuItem()
            self.sleep_timer_menu_item = gtk.CheckMenuItem(_("Sleep Timer"))
            menu_item1 = gtk.MenuItem(_("Configure Radios..."))
            menu_item4 = gtk.MenuItem(_("Reload Bookmarks"))        
            menu_item3 = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
            menu_item2 = gtk.ImageMenuItem(gtk.STOCK_QUIT)        
            self.menu.append(self.turnOnOff2)
            self.menu.append(separator) 
            self.menu.append(self.sleep_timer_menu_item)       
            self.menu.append(menu_item1)
            self.menu.append(menu_item4)        
            self.menu.append(gtk.MenuItem())                
            self.menu.append(menu_item3)
            self.menu.append(menu_item2)        
            menu_item1.show()
            menu_item2.show()
            menu_item3.show()
            menu_item4.show()
            self.sleep_timer_menu_item.show()
            self.turnOnOff2.show()
            separator.show()      
            
            menu_item1.connect('activate', self.on_preferences)
            menu_item2.connect('activate', self.on_quit)
            menu_item3.connect('activate', self.on_about)
            menu_item4.connect('activate', self.reload_bookmarks)
            self.sleep_timer_menu_item.connect('activate', self.on_sleep_menu)
                            
            self.menu.show_all()      

            self.icon = gtk.status_icon_new_from_file(APP_ICON_OFF)
            self.icon.set_tooltip_markup(_("Idle (vol: %s%%)") % (self.mediator.getVolume()))
            self.icon.connect('button_press_event', self.button_press)
            self.icon.connect('scroll_event', self.scroll)

        else:
            # app indicator support
            self.turnOnOff = None
            self.metadata_menu_item = None
            self.sleep_timer_menu_item = None
            self.perferences_submenu = None
            self.preferences_menu = None            
            self.radioMenu = gtk.Menu()
            self.build_app_indicator_menu(self.radioMenu)
            self.app_indicator.set_menu(self.radioMenu)
            self.updateTooltip()

            try:
                self.app_indicator.connect("scroll-event", self.app_indicator_scroll)
            except:
                # not available in this version of app indicator
                print "Volume mouse scroll events not available."
            
        # MediaKeys
        try:
            self.bus = dbus.SessionBus()
            self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
            self.bus_object.GrabMediaPlayerKeys("RadioTray", 0, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
            self.bus_object.connect_to_signal('MediaPlayerKeyPressed', self.handle_mediakey)
        except:
            print "Could not bind to Gnome for Media Keys"

    def app_indicator_scroll(self, indicator, delta, direction):
        if direction == 0:
            self.mediator.volume_up()
        else:    
            self.mediator.volume_down()

    def scroll(self,widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.mediator.volume_up()
            
        if event.direction == gtk.gdk.SCROLL_DOWN:
            self.mediator.volume_down()
            
    def volume_up(self, menu_item):
        self.mediator.volume_up()
            
    def volume_down(self, menu_item):
        self.mediator.volume_down()

    def button_press(self,widget,event):

        if event.button == 2:
            if (self.mediator.isPlaying):
                self.mediator.stop()
            else:
                if self.mediator.currentRadio:
                    self.mediator.play(self.mediator.currentRadio)
            return

        if(event.button == 1):
            self.radioMenu.popup(None, None, gtk.status_icon_position_menu, 0, event.get_time(), widget)
        else:
            self.menu.popup(None, None, gtk.status_icon_position_menu, 2, event.get_time(), widget)

    def handle_mediakey(self, *mmkeys):
        for key in mmkeys:
            if key == "Play":
                if (self.mediator.isPlaying):
                    self.mediator.stop()
                elif self.mediator.currentRadio:
                    self.mediator.play(self.mediator.currentRadio)
            elif key == "Stop":
                if (self.mediator.isPlaying):
                    self.mediator.stop()

    def on_preferences(self, data):
        config = BookmarkConfiguration(self.provider, self.update_radios)

    def on_quit(self, data):
        print 'Exiting...'
        gtk.main_quit()

    def on_about(self, data):
        about_dialog(parent=None)

    def on_turn_on_off(self, data):
        if self.mediator.isPlaying:
            self.mediator.stop()
        else:
            self.mediator.play(self.mediator.currentRadio)

    def on_start(self, data, radio):
        self.mediator.play(radio)
        
    def on_sleep_timer(self):
        self.min_to_sleep-=1       
                
        if self.min_to_sleep == 0:
            # set menu state
            self.ignore_toggle = True       
            self.sleep_timer_menu_item.set_active(False)            
            self.ignore_toggle = False
            
            self.sleep_timer_id = None
            self.mediator.stop()
            self.mediator.notify(_("Sleep timer expired"))
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
            self.mediator.notify(_("%s minute sleep timer started") % str(interval))
    
    def stop_sleep_timer(self, display_msg):
        gobject.source_remove(self.sleep_timer_id)
        self.sleep_timer_id = None  
        if display_msg:                   
            self.mediator.notify(_("Sleep timer stopped"))
    
    def setStoppedState(self):
        if not self.mediator.currentRadio:        
            self.turnOnOff.set_label(_('Turned Off'))
            self.turnOnOff.set_sensitive(False)
        else:
            self.turnOnOff.set_label(_('Turn On "%s"') % self.mediator.currentRadio)
            self.turnOnOff.set_sensitive(True)
                                
        if not self.app_indicator:
            if not self.mediator.currentRadio:            
                self.turnOnOff2.set_label(_('Turned Off'))
                self.turnOnOff2.set_sensitive(False)
            else:
                self.turnOnOff2.set_label(_('Turn On "%s"') % self.mediator.currentRadio)
                self.turnOnOff2.set_sensitive(True)
                
            self.icon.set_from_file(APP_ICON_OFF)
        else:        
            self.app_indicator.set_icon(APP_INDICATOR_ICON_OFF if self.app_indicator_use_theme else APP_ICON_OFF)
        
        self.updateTooltip()

    def setPlayingState(self, radio):
        self.turnOnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % radio)
        self.turnOnOff.set_sensitive(True)
        
        if not self.app_indicator:
            self.turnOnOff2.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % radio)
            self.turnOnOff2.set_sensitive(True)
            self.icon.set_from_file(APP_ICON_ON)
        else:        
            self.app_indicator.set_icon(APP_INDICATOR_ICON_ON if self.app_indicator_use_theme else APP_ICON_ON)        
                
        self.updateTooltip()

    def setConnectingState(self, radio):
        #if self.app_indicator:
        self.turnOnOff.set_sensitive(True)
        self.turnOnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % radio)       
                                
        if not self.app_indicator:
            self.turnOnOff2.set_sensitive(True)
            self.turnOnOff2.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % radio)
            self.icon.set_tooltip_markup(C_("Connecting to a music stream.", "Connecting to %s") % radio.replace("&", "&amp;"))
            self.icon.set_from_file(APP_ICON_CONNECT)

    def updateTooltip(self):
        
        radio = html_escape(self.mediator.getCurrentRadio())

        songInfo = None
        if(self.mediator.getCurrentMetaData() and len(self.mediator.getCurrentMetaData()) > 0):
            songInfo = self.mediator.getCurrentMetaData() if self.app_indicator else html_escape(self.mediator.getCurrentMetaData())            
        
        volume = self.mediator.getVolume()
        sleep_timer_info = ""
        if self.sleep_timer_id != None:
            sleep_timer_info = _(', sleep: %s min') % str(self.min_to_sleep)
        
        if self.mediator.isPlaying:
            if(songInfo):
                if not self.app_indicator:
                    self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%%s)\n<i>%s</i>") % (radio, volume, sleep_timer_info, songInfo))
                else:           
                    otherInfo = "(vol: %s%%%s)" % (volume, sleep_timer_info)         
                   
                    # don't break volume info...
                    text = textwrap.wrap(songInfo, 30)
                    if (30 - len(text[-1])) >= (len(otherInfo)+1):
                        text[-1] += " " + otherInfo
                    else:
                        text.append(otherInfo)
                        
                    self.metadata_menu_item.set_label("\n".join(text))                    
            else:
                if not self.app_indicator:
                    self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%%s)") % (radio, volume, sleep_timer_info))
                else:                    
                    self.metadata_menu_item.set_label(_("Playing (vol: %s%%%s)") % (volume, sleep_timer_info))
        else:
            if not self.app_indicator:
                self.icon.set_tooltip_markup(C_("Informs Radiotray is idle as a tooltip.", "Idle (vol: %s%%%s)") % (volume, sleep_timer_info))
            else:                
                self.metadata_menu_item.set_label(C_("Informs Radiotray is idle as a tooltip.", "Idle (vol: %s%%%s)") % (volume, sleep_timer_info))              

    def update_radios(self):

        for child in self.radioMenu.get_children():
            self.radioMenu.remove(child)

        if not self.app_indicator:
        
            self.radioMenu.append(self.turnOnOff)
            self.turnOnOff.show()
    
            separator = gtk.MenuItem()
            self.radioMenu.append(separator)
            separator.show()
    
            # build menu
            self.provider.walk_bookmarks(self.group_callback, self.bookmark_callback, self.radioMenu)
            self.radioMenu.show_all()
        else:
            self.build_app_indicator_menu(self.radioMenu)
        
        
    def run(self):
        gtk.main()


    def group_callback(self, group_name, user_data):

        new_user_data = None
        
        if group_name != 'root':
            group = gtk.MenuItem(group_name, False)
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
            radio = gtk.MenuItem(radio_name, False)
            radio.show()
            radio.connect('activate', self.on_start, radio_name)
            user_data.append(radio)

            
    def reload_bookmarks(self, data):
        self.provider.loadFromFile()
        self.update_radios()
        self.mediator.notify(_("Bookmarks Reloaded"))
        

    def get_sleep_timer_value(self, default_value):

        gtk.gdk.threads_enter()

        dialog = gtk.Dialog(_("Edit Sleep Timer"), None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
                        
        entry = gtk.Entry(4)       
        entry.set_text(str(default_value)) 
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(_("Minutes:")), False, 5, 5)
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
    

    def build_app_indicator_menu(self, menu):
                    
        # config menu   
        if self.turnOnOff == None:                        
            if not self.mediator.currentRadio:
                self.turnOnOff = gtk.MenuItem(_("Turned Off"), False)
                self.turnOnOff.set_sensitive(False)
            else:
                self.turnOnOff = gtk.MenuItem(_('Turn On "%s"') % self.mediator.currentRadio, False)
                self.turnOnOff.set_sensitive(True)
                
            self.turnOnOff.connect('activate', self.on_turn_on_off)
            
            
        # stream metadata info
        if self.metadata_menu_item == None:
            self.metadata_menu_item = gtk.MenuItem(_("Idle"), False)
            self.metadata_menu_item.set_sensitive(False)
        
        if self.sleep_timer_menu_item == None:                        
            self.sleep_timer_menu_item = gtk.CheckMenuItem(_("Sleep Timer"))        
        
        if self.preferences_menu == None:
            self.preferences_menu = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)                
        
        menu_config_radios = gtk.MenuItem(_("Configure Radios..."))
        menu_reload_bookmarks = gtk.MenuItem(_("Reload Bookmarks"))
        volume_menu_item_up = gtk.MenuItem(_("Volume Up"))
        volume_menu_item_down = gtk.MenuItem(_("Volume Down"))

        # build 
        menu.append(self.turnOnOff)                             
        menu.append(gtk.MenuItem())                        
        menu.append(self.metadata_menu_item)
        menu.append(gtk.MenuItem())
                
        self.provider.walk_bookmarks(self.group_callback, self.bookmark_callback, menu)
        
        menu_config_radios.connect('activate', self.on_preferences)
        menu_reload_bookmarks.connect('activate', self.reload_bookmarks)
        self.sleep_timer_menu_item.connect('activate', self.on_sleep_menu)
        
        volume_menu_item_up.connect('activate', self.volume_up)
        volume_menu_item_down.connect('activate', self.volume_down)        
                   
        menu.append(gtk.MenuItem())
     
        # build preferences
        menu.append(self.preferences_menu)
        
        if self.perferences_submenu == None:  
            self.perferences_submenu = gtk.Menu()
            self.preferences_menu.set_submenu(self.perferences_submenu)               
            self.perferences_submenu.append(volume_menu_item_up)
            self.perferences_submenu.append(volume_menu_item_down)
            self.perferences_submenu.append(gtk.MenuItem())          
            self.perferences_submenu.append(self.sleep_timer_menu_item)       
            self.perferences_submenu.append(menu_config_radios)
            self.perferences_submenu.append(menu_reload_bookmarks)

        menu_about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        menu_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)        
        menu_quit.connect('activate', self.on_quit)
        menu_about.connect('activate', self.on_about)
        menu.append(menu_about)
        menu.append(menu_quit)

        menu.show_all() 
        
