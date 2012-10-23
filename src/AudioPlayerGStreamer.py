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
import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
from StreamDecoder import StreamDecoder
from lib.common import USER_AGENT
from events.EventManager import EventManager
from threading import Timer
import logging

class AudioPlayerGStreamer:

    def __init__(self, mediator, cfg_provider, eventManager):
        self.mediator = mediator
        self.eventManager = eventManager
        self.decoder = StreamDecoder(cfg_provider)
        self.playlist = []
        self.retrying = False

        self.log = logging.getLogger('radiotray')

        # init player
        self.souphttpsrc = gst.element_factory_make("souphttpsrc", "source")
        self.souphttpsrc.set_property("user-agent", USER_AGENT)
		
        self.player = gst.element_factory_make("playbin2", "player")		
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)

        #buffer size
        if(cfg_provider._settingExists("buffer_size")):
            bufferSize = int(cfg_provider.getConfigValue("buffer_size"))
            if (bufferSize > 0):
            
                self.log.debug("Setting buffer size to " + str(bufferSize))
                self.player.set_property("buffer-size", bufferSize)

        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def start(self, uri):

        urlInfo = self.decoder.getMediaStreamInfo(uri)

        if(urlInfo is not None and urlInfo.isPlaylist()):
            self.playlist = self.decoder.getPlaylist(urlInfo)
            if(len(self.playlist) == 0):
                self.log.warn('Received empty playlist!')
                self.mediator.stop()
                self.eventManager.notify(EventManager.STATION_ERROR, {'error':"Received empty stream from station"})
            self.log.debug(self.playlist)
            self.playNextStream()

        elif(urlInfo is not None and urlInfo.isPlaylist() == False):
            self.playlist = [urlInfo.getUrl()]
            self.playNextStream()

        else:
            self.stop()
            self.eventManager.notify(EventManager.STATION_ERROR, {'error':"Couldn't connect to radio station"})
            

    def playNextStream(self):
        if(len(self.playlist) > 0):
            stream = self.playlist.pop(0)
            self.log.info('Play "%s"', stream)

            urlInfo = self.decoder.getMediaStreamInfo(stream)
            if(urlInfo is not None and urlInfo.isPlaylist() == False):
                self.playStream(stream)
            elif(urlInfo is not None and urlInfo.isPlaylist()):
                self.playlist = self.decoder.getPlaylist(urlInfo) + self.playlist
                self.playNextStream()
            elif(urlInfo is None):
                self.playNextStream()
        else:
            self.stop()
            self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})
        self.mediator.updateVolume(self.player.get_property("volume"))


    def playStream(self, uri):
        self.player.set_property("uri", uri)
        self.player.set_state(gst.STATE_PAUSED) # buffer before starting playback

    def stop(self):
        self.player.set_state(gst.STATE_NULL)
        self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})

    def volume_up(self, volume_increment):   
        self.player.set_property("volume", min(self.player.get_property("volume") + volume_increment, 1.0))
        self.mediator.updateVolume(self.player.get_property("volume"))

    def volume_down(self, volume_increment):
        self.player.set_property("volume", max(self.player.get_property("volume") - volume_increment, 0.0))
        self.mediator.updateVolume(self.player.get_property("volume"))

    def on_message(self, bus, message):
        t = message.type

        stru = message.structure
        if(stru != None):
            name = stru.get_name()
            if(name == 'redirect'):
                self.log.info("redirect received")
                self.player.set_state(gst.STATE_NULL)
                stru.foreach(self.redirect, None)

                

        if t == gst.MESSAGE_EOS:
            self.log.debug("Received MESSAGE_EOS")
            self.player.set_state(gst.STATE_NULL)
            self.playNextStream()
        elif t == gst.MESSAGE_BUFFERING:
            percent = message.structure['buffer-percent']
            if percent < 100:
                self.log.debug("Buffering %s" % percent)
                self.player.set_state(gst.STATE_PAUSED)
            else:
                self.player.set_state(gst.STATE_PLAYING)
        elif t == gst.MESSAGE_ERROR:
            self.log.debug("Received MESSAGE_ERROR")
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            self.log.warn(err)
            self.log.warn(debug)

            if(len(self.playlist)>0):
                self.playNextStream()
            else:
                self.eventManager.notify(EventManager.STATION_ERROR, {'error':debug})

        elif t == gst.MESSAGE_STATE_CHANGED:
            oldstate, newstate, pending = message.parse_state_changed()
            self.log.debug(("Received MESSAGE_STATE_CHANGED (%s -> %s)") % (oldstate, newstate))

            if newstate == gst.STATE_PLAYING:
                self.retrying = False
                station = self.mediator.getContext().station
                self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'playing', 'station':station})
            elif oldstate == gst.STATE_PLAYING and newstate == gst.STATE_PAUSED:
                self.log.info("Received PAUSE state.")
                
                if self.retrying == False:
                    self.retrying = True
                    timer = Timer(20.0, self.checkTimeout)
                    timer.start()
                    self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})
                    
            

        elif t == gst.MESSAGE_TAG:

           taglist = message.parse_tag()

           #if there is no song information, there's no point in triggering song change event
           if('artist' in taglist.keys() or 'title' in taglist.keys()):
               station = self.mediator.getContext().station
               metadata = {}

               for key in taglist.keys():      
                   metadata[key] = taglist[key]

               metadata['station'] = station
           
               self.eventManager.notify(EventManager.SONG_CHANGED, metadata)

        return True

    def redirect(self, name, value, data):
        if(name == 'new-location'):
            self.start(value)
        return True


    def checkTimeout(self):
        self.log.debug("Checking timeout...")
        if self.retrying == True:
            self.log.info("Timed out. Retrying...")
            uri = self.player.get_property("uri")
            self.playStream(uri)
        else: 
            self.log.info("Timed out, but not retrying anymore")
