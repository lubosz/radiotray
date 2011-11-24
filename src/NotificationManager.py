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
from Notification import Notification
from lib.common import APPNAME
from events.EventManager import EventManager

class NotificationManager(object):

    def __init__(self, eventManager):
        self.eventManager = eventManager
        
        
    def on_state_changed(self, data):
    
        state = data['state']
        
        if(state == 'playing'):
            station = data['station']
            self.eventManager.notify(EventManager.NOTIFICATION, {'title':'Radio Tray Playing', 'message':station})
#            self.notification.notify(C_("Notifies which radio is currently playing.", "Radio Tray Playing"), station)
            

    def on_song_changed(self, data):
    
        print data.keys()
        
        station = data['station']
        msgTitle = "%s - %s" % (APPNAME , station)

        if('artist' in data.keys() and 'title' in data.keys()):
            artist = data['artist']
            title = data['title']
            msg = "%s - %s" % (artist, title)            
            self.eventManager.notify(EventManager.NOTIFICATION, {'title': msgTitle, 'message':msg})
#            self.notification.notify("%s - %s" % (APPNAME , station), msg)
        elif('artist' in data.keys()):
            msg = data['artist']
            self.eventManager.notify(EventManager.NOTIFICATION, {'title': msgTitle, 'message':msg})
#            self.notification.notify("%s - %s" % (APPNAME , station), msg)
        elif('title' in data.keys()):
            msg = data['title']
            self.eventManager.notify(EventManager.NOTIFICATION, {'title': msgTitle, 'message':msg})
#            self.notification.notify("%s - %s" % (APPNAME , station), msg)


        
    def on_station_error(self, data):
    
        self.eventManager.notify(EventManager.NOTIFICATION, {'title': 'Radio Error', 'message':str(data['error'])})
#        self.notification.notify(C_("An error notification.", "Radio Error"), str(data['error']))

    def on_bookmarks_reloaded(self, data):

        self.eventManager.notify(EventManager.NOTIFICATION, {'title': _("Bookmarks Reloaded"), 'message':_("Bookmarks Reloaded")})
#        self.notification.notify(_("Bookmarks Reloaded"), _("Bookmarks Reloaded"))
        
        
