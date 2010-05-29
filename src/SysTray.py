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

    def __init__(self, mediator, provider, log):

        self.version = APPVERSION
        self.mediator = mediator

        # initialize data provider
        self.provider = provider

        # radios menu
        self.radioMenu = gtk.Menu()
        self.turnOff = gtk.MenuItem(_("Turned Off"))
        self.turnOff.connect('activate', self.on_turn_off)
        self.turnOff.set_sensitive(False)
        self.update_radios()

        # config menu

        self.menu = gtk.Menu()
        menu_item1 = gtk.MenuItem(_("Configure radios..."))
        menu_item3 = gtk.MenuItem(_("About"))
        menu_item2 = gtk.MenuItem(_("Quit"))
        self.menu.append(menu_item1)
        self.menu.append(menu_item3)
        self.menu.append(menu_item2)
        menu_item1.show()
        menu_item2.show()
        menu_item3.show()
        menu_item1.connect('activate', self.on_preferences)
        menu_item2.connect('activate', self.on_quit)
        menu_item3.connect('activate', self.on_about)

        self.icon = gtk.status_icon_new_from_file(APP_ICON_OFF)
        self.icon.set_tooltip_markup(_('<i>Idle</i>'))
        self.icon.connect('button_press_event', self.button_press)
        self.icon.connect('scroll_event', self.scroll)

        # MediaKeys
        try:
            self.bus = dbus.SessionBus()
            self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')

            self.bus_object.connect_to_signal('MediaPlayerKeyPressed', self.handle_mediakey)
        except:
            print "Could not bind to Gnome for Media Keys"

    def scroll(self,widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.mediator.volume_up()
            
        if event.direction == gtk.gdk.SCROLL_DOWN:
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

    def on_turn_off(self, data):
        self.mediator.stop()

    def on_start(self, data, radio):
        self.mediator.play(radio)

    def setStoppedState(self):
        self.turnOff.set_label(_('Turned Off'))
        self.turnOff.set_sensitive(False)
        self.icon.set_from_file(APP_ICON_OFF)
        self.icon.set_tooltip_markup(_("<i>Idle</i>"))

    def setPlayingState(self, radio):
        self.turnOff.set_label(C_('Turns off the current radio.', 'Turn Off "%s"') % radio)
        self.turnOff.set_sensitive(True)
        self.updateTooltip()
        self.icon.set_from_file(APP_ICON_ON)

    def setConnectingState(self, radio):
        self.turnOff.set_sensitive(True)
        self.icon.set_tooltip_markup(C_("Connecting to a music stream.", "Connecting to %s") % radio.replace("&", "&amp;"))
        self.icon.set_from_file(APP_ICON_CONNECT)


    def updateTooltip(self):
        radio = html_escape(self.mediator.getCurrentRadio())

        songInfo = None
        if(self.mediator.getCurrentMetaData() and len(self.mediator.getCurrentMetaData()) > 0):
            songInfo = html_escape(self.mediator.getCurrentMetaData())
        
        volume = self.mediator.getVolume()

        if(songInfo):
            self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%)\n<i>%s</i>") % (radio, volume, songInfo))
        else:
            self.icon.set_tooltip_markup(C_("Informs what radio and music is being played as a tooltip.", "Playing <b>%s</b> (vol: %s%%)") % (radio, volume))

    def update_radios(self):

        for child in self.radioMenu.get_children():
            self.radioMenu.remove(child)

        self.radioMenu.append(self.turnOff)
        self.turnOff.show()

        separator = gtk.MenuItem()
        self.radioMenu.append(separator)
        separator.show()

        #add configured radios

        for radio in self.provider.listRadioNames():

            if radio.startswith("[separator-"):
                separator = gtk.MenuItem()
                self.radioMenu.append(separator)
                separator.show()
            else:
                radio1 = gtk.MenuItem(radio)
                self.radioMenu.append(radio1)
                radio1.show()
                radio1.connect('activate', self.on_start, radio)



    def run(self):
        gtk.gdk.threads_init()
        gtk.main()
