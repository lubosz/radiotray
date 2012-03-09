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
from lib.common import APPNAME
from events.EventMngNotificationWrapper import EventMngNotificationWrapper
import urllib2
from lib.common import USER_AGENT, ICON_FILE
import logging
import traceback

class NotificationManager(object):

    def __init__(self, eventManagerWrapper):
        self.eventManagerWrapper = eventManagerWrapper
        self.log = logging.getLogger('radiotray')
        self.lastState = None
        
    def on_state_changed(self, data):
    
        state = data['state']
        
        if(state == 'playing' and state != self.lastState):
            station = data['station']
            self.lastState = state
            self.eventManagerWrapper.notify(_('Radio Tray Playing'), station)

            

    def on_song_changed(self, data):
    
        self.log.debug(data)
        
        station = data['station']
        msgTitle = "%s - %s" % (APPNAME , station)
        msg = None

        if('artist' in data.keys() and 'title' in data.keys()):
            artist = data['artist']
            title = data['title']
            msg = "%s - %s" % (artist, title)            
        elif('artist' in data.keys()):
            msg = data['artist']
        elif('title' in data.keys()):
            msg = data['title']

        if('homepage' in data.keys() and (data['homepage'].endswith('png') or data['homepage'].endswith('jpg'))):
            #download image
            try:
                req = urllib2.Request(data['homepage'])
                req.add_header('User-Agent', USER_AGENT)
                response = urllib2.urlopen(req)
                pix = response.read()
                f = open(ICON_FILE,'wb')
                try:
                    f.write(pix)
                except Exception, e:
                    log.warn('Error saving icon')
                finally:
                    f.close()

                self.eventManagerWrapper.notify_icon(msgTitle, msg, ICON_FILE)
                
            except Exception, e:
                traceback.print_exc()
                self.eventManagerWrapper.notify(msgTitle, msg)
        else:
            self.eventManagerWrapper.notify(msgTitle, msg)
        
    def on_station_error(self, data):
    
        self.eventManagerWrapper.notify(_('Radio Error'), str(data['error']))

    def on_bookmarks_reloaded(self, data):

        self.eventManagerWrapper.notify(_("Bookmarks Reloaded"), _("Bookmarks Reloaded"))
        
        
