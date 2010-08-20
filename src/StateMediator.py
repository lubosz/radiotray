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

class StateMediator(object):

    def __init__(self, provider, cfg_provider, notification):
        self.provider = provider
        self.cfg_provider = cfg_provider
        self.notification = notification
        self.isPlaying = False
        self.isNotified = False
        self.currentRadio = ''
        self.currentMetaData = ''
        self.volume = float(self.cfg_provider.getConfigValue("volume_level"))
        self.bitrate = 0

    def setAudioPlayer(self, audioPlayer):
        self.audioPlayer = audioPlayer

        # set volume level (can't call set_volume yet)
        self.audioPlayer.player.set_property("volume", self.volume)

    def setSystray(self, systray):
        self.systray = systray

    def play(self, radio):

        if(self.isPlaying):
            self.audioPlayer.stop()
        self.currentMetaData = ''

        url = self.provider.getRadioUrl(radio)
        self.audioPlayer.start(url)
        self.systray.setConnectingState(radio)
        self.currentRadio = radio
        self.isNotified = False

    def playUrl(self, url):

        if(self.isPlaying):
            self.audioPlayer.stop()
        self.currentMetaData = ''
        self.audioPlayer.start(url)
        self.systray.setConnectingState(C_("Unknown radio specified by URL", "Unknown radio"))
        self.currentRadio = C_("Unknown radio specified by URL", "Unknown radio")
        self.isNotified = False

    def stop(self):
        self.audioPlayer.stop()
        self.systray.setStoppedState()
        self.isPlaying = False
        self.isNotified = False

    def volume_up(self):
        self.audioPlayer.volume_up(float(self.cfg_provider.getConfigValue("volume_increment")))
        self.systray.updateTooltip()

    def volume_down(self):
        self.audioPlayer.volume_down(float(self.cfg_provider.getConfigValue("volume_increment")))
        self.systray.updateTooltip()

    def set_volume(self, value):
        print "set volume: "+str(value)
        self.audioPlayer.player.set_property("volume", value)
        self.systray.updateTooltip()

    def notifyError(self, error, message):
        print "Error: " + str(error)
        print "Error: " + message
        self.systray.setStoppedState()
        self.isPlaying = False
        self.notification.notify(C_("An error notification.", "Radio Error"), str(error))
        
    def notify(self, msg):
        self.notification.notify("Radio Tray", msg)

    def notifyPlaying(self):
        if (self.isNotified == False):
            self.isNotified = True
            self.isPlaying = True            
            self.systray.setPlayingState(self.currentRadio)
            if self.cfg_provider.getConfigValue("enabled_notifications") == "true":
                self.notification.notify(C_("Notifies which radio is currently playing.", "Radio Playing"), self.currentRadio)

    def notifyStopped(self):
        self.systray.setStoppedState()
        self.isPlaying = False

    def notifySong(self, data):
        newMetadata = str(data)
        
        if (self.currentMetaData != newMetadata):
            self.currentMetaData = newMetadata
            self.systray.updateTooltip()

            if self.currentMetaData:
                if self.cfg_provider.getConfigValue("enabled_notifications") == "true":
                    self.notification.notify("%s - %s" % (APPNAME , self.currentRadio), self.currentMetaData)

    def getCurrentRadio(self):
        return self.currentRadio

    def getCurrentMetaData(self):
        return self.currentMetaData

    def updateVolume(self, volume):
        self.volume = volume
        self.cfg_provider.setConfigValue("volume_level", str(round(self.volume,2)))

    def getVolume(self):
        return int(round(self.volume * 100))

