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
from utils import findfile

class SysTray:

	def __init__(self, mediator, provider, log):
		
		self.version='0.3'
		self.mediator = mediator

		# initialize data provider
		self.provider = provider

		# radios menu
		self.radioMenu = gtk.Menu()
		self.turnOff = gtk.MenuItem("Turn Off Radio")
		self.turnOff.connect('activate', self.on_turn_off)
		self.turnOff.set_sensitive(False)
		
		self.update_radios()

		# config menu

		self.menu = gtk.Menu()
                menu_item1 = gtk.MenuItem("Config radios...")
		menu_item3 = gtk.MenuItem("About")
		menu_item2 = gtk.MenuItem("Quit")
                self.menu.append(menu_item1)
		self.menu.append(menu_item3)
		self.menu.append(menu_item2)
                menu_item1.show()
		menu_item2.show()
		menu_item3.show()
		menu_item1.connect('activate', self.on_preferences)
		menu_item2.connect('activate', self.on_quit)
		menu_item3.connect('activate', self.on_about)

		self.icon = gtk.status_icon_new_from_file(findfile('icons/radiotray.png'))
		self.icon.set_tooltip('Radio Tray: idle')
		self.icon.connect('button_press_event', self.button_press)

	def button_press(self,widget,event):
		print "show menu"
		if(event.button == 1):
			self.radioMenu.popup(None, None, gtk.status_icon_position_menu, 0, event.get_time(), widget)
		else:
			self.menu.popup(None, None, gtk.status_icon_position_menu, 2, event.get_time(), widget)


	def on_preferences(self, data):
		print 'preferences'
		config = BookmarkConfiguration(self.provider, self.update_radios)

	def on_quit(self, data):
		print 'Exiting...'
		gtk.main_quit()

	def on_about(self, data):
		print 'About...'
		about = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, 'Radio Tray v'+self.version+'\n\nhttp://radiotray.sourceforge.net\n\nCopyright 2009 Carlos Ribeiro')
		about.run()
		about.hide()

	def on_turn_off(self, data):		
		self.mediator.stop()
		

	def on_start(self, data, radio):
		self.mediator.play(radio)
			

	def setStoppedState(self):
		self.turnOff.set_sensitive(False)
		self.icon.set_tooltip("Radio Tray: idle")

	def setPlayingState(self, radio):
		self.turnOff.set_sensitive(True)
		self.icon.set_tooltip("Playing " + radio)

	def setConnectingState(self, radio):
		self.turnOff.set_sensitive(True)
		self.icon.set_tooltip("Connecting to " + radio)


	def update_radios(self):
		print 'update'
		
		for child in self.radioMenu.get_children():
			self.radioMenu.remove(child)

		self.radioMenu.append(self.turnOff)
		self.turnOff.show()
		
		separator = gtk.MenuItem()
		self.radioMenu.append(separator)
		separator.show()

		#add configured radios

		for radio in self.provider.listRadioNames():
			
			radio1 = gtk.MenuItem(radio)
			self.radioMenu.append(radio1)
			radio1.show()
			radio1.connect('activate', self.on_start, radio)



	def run(self):
		gtk.gdk.threads_init()        
		gtk.main()	



