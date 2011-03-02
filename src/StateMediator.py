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
from AudioPlayerGStreamer import AudioPlayerGStreamer
from SysTray import SysTray
from Notification import Notification
from lib.common import APPNAME
from Context import Context
from events.EventManager import EventManager

class StateMediator(object):

    def __init__(self, provider, cfg_provider, eventManager):
        self.provider = provider
        self.cfg_provider = cfg_provider
        self.eventManager = eventManager
        
        self.context = Context()
        self.context.state = Context.STATE_PAUSED

        radio = self.cfg_provider.getConfigValue("last_station")
        self.context.station = '' if not radio else radio 

        self.volume = float(self.cfg_provider.getConfigValue("volume_level"))
        self.bitrate = 0
        
        # validate station
        if not self.provider.getRadioUrl(radio):
            self.context.station = ''
        
        
        
    def init(self, audioPlayer):
        self.audioPlayer = audioPlayer
        # set volume level (can't call set_volume yet)
        self.audioPlayer.player.set_property("volume", self.volume)
        
        
    def getContext(self):
        return self.context
        


# ---  control commands ----

    def play(self, radio):

        if(self.context.state == 'playing'):
            self.stop()
            
        url = self.provider.getRadioUrl(radio)

        if(url):
            self.context.station = radio
            self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'connecting', 'station':radio})
                
            self.audioPlayer.start(url)
            self.cfg_provider.setConfigValue("last_station", radio)
        else:
            self.context.station = ''
            self.stop()

    def playUrl(self, url):

        if(self.isPlaying):
            self.audioPlayer.stop()
        
        self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'connecting', 'station':Context.UNKNOWN_RADIO})
        self.context.station = Context.UNKNOWN_RADIO
        self.audioPlayer.start(url)

    def playLast(self):
        if self.context.station:
            self.play(self.context.station)

    def stop(self):
        self.audioPlayer.stop()


    def isPlaying(self):
        return self.context.state == Context.STATE_PLAYING

    def volume_up(self):
        self.audioPlayer.volume_up(float(self.cfg_provider.getConfigValue("volume_increment")))
        self.eventManager.notify(EventManager.VOLUME_CHANGED, {'volume':self.getVolume()})

    def volume_down(self):
        self.audioPlayer.volume_down(float(self.cfg_provider.getConfigValue("volume_increment")))
        self.eventManager.notify(EventManager.VOLUME_CHANGED, {'volume':self.getVolume()})

    def set_volume(self, value):
        print "set volume: "+str(value)
        self.audioPlayer.player.set_property("volume", value)
        self.systray.updateTooltip()
        
    def getVolume(self):
        return int(round(self.volume * 100))    
        
    def updateVolume(self, volume):
        self.volume = volume
        self.cfg_provider.setConfigValue("volume_level", str(round(self.volume,2)))


   
    def on_state_changed(self, data):
        self.context.state = data['state']
        print self.context.state
        
        
    def on_station_error(self, data):
        self.context.state = 'paused'
        print self.context.state
        
        
    def on_song_changed(self, data):
        print data
        if('artist' in data.keys()):
            self.context.artist = data['artist']
        if('title' in data.keys()):
            print "set title"
            self.context.title = data['title']

