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
from lib.common import APPNAME, APPVERSION, APP_ICON_ON, APP_ICON_OFF
from lib import i18n
from about import AboutDialog

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
        self.turnOff = gtk.MenuItem(_("Turn Off Radio"))
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

    def button_press(self,widget,event):

        if(event.button == 1):
            self.radioMenu.popup(None, None, gtk.status_icon_position_menu, 0, event.get_time(), widget)
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

    def setStoppedState(self):
        self.turnOff.set_sensitive(False)
        self.icon.set_from_file(APP_ICON_OFF)
        self.icon.set_tooltip_markup(_("<i>Idle</i>"))

    def setPlayingState(self, radio):
        self.turnOff.set_sensitive(True)
        if(self.mediator.getCurrentMetaData() and len(self.mediator.getCurrentMetaData()) > 0):
            self.icon.set_tooltip_markup(_("Playing <b>%s</b>\n<i>%s</i>") % (radio, self.mediator.getCurrentMetaData()))
        else:
            self.icon.set_tooltip_markup(_("Playing <b>%s</b>") % radio)
        self.icon.set_from_file(APP_ICON_ON)

    def setConnectingState(self, radio):
        self.turnOff.set_sensitive(True)
        self.icon.set_tooltip_markup(_("Connecting to %s") % radio)

    def updateRadioMetadata(self, data):
        print self.mediator.getCurrentRadio()
        print data
        self.icon.set_tooltip_markup(_("Playing <b>%s</b>\n<i>%s</i>") % (self.mediator.getCurrentRadio(), data))

    def update_radios(self):

        for child in self.radioMenu.get_children():
            self.radioMenu.remove(child)

        self.radioMenu.append(self.turnOff)
        self.turnOff.show()

        separator = gtk.MenuItem()
        self.radioMenu.append(separator)
        separator.show()

        #add configured radios

        # We need a "group" for RadioMenuItems so that only one radiobutton gets selected
        radioMenuGroup = gtk.RadioMenuItem()
        self.radioMenu.append(radioMenuGroup)

        for radio in self.provider.listRadioNames():

            radio1 = gtk.RadioMenuItem(group=radioMenuGroup, label=radio)
            self.radioMenu.append(radio1)
            radio1.show()
            radio1.connect('activate', self.on_start, radio)



    def run(self):
        gtk.gdk.threads_init()
        gtk.main()
