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

class AudioPlayerGStreamer:

    def __init__(self, mediator, cfg_provider, log, eventManager):
        self.mediator = mediator
        self.log = log
        self.eventManager = eventManager
        self.decoder = StreamDecoder(cfg_provider)
        self.playlist = []

        # init player
        self.souphttpsrc = gst.element_factory_make("souphttpsrc", "source")
        self.souphttpsrc.set_property("user-agent", USER_AGENT)
		
        self.player = gst.element_factory_make("playbin2", "player")		
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def start(self, uri):

        urlInfo = self.decoder.getMediaStreamInfo(uri)

        if(urlInfo is not None and urlInfo.isPlaylist()):
            self.playlist = self.decoder.getPlaylist(urlInfo)
            print self.playlist
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
            print "Play " + stream

            urlInfo = self.decoder.getMediaStreamInfo(stream)
            if(urlInfo is not None and urlInfo.isPlaylist() == False):
                self.player.set_property("uri", stream)
                self.player.set_state(gst.STATE_PLAYING)
            elif(urlInfo is not None and urlInfo.isPlaylist()):
                self.playlist = self.decoder.getPlaylist(urlInfo) + self.playlist
                self.playNextStream()
            elif(urlInfo is None):
                self.playNextStream()
        else:
            self.stop()
            self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'paused'})
        self.mediator.updateVolume(self.player.get_property("volume"))

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
        if t == gst.MESSAGE_EOS:
            self.log.log("Received MESSAGE_EOS")
            self.player.set_state(gst.STATE_NULL)
            self.playNextStream()

        elif t == gst.MESSAGE_ERROR:
            self.log.log("Received MESSAGE_ERROR")
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print err
            print debug

            if(len(self.playlist)>0):
                self.playNextStream()
            else:
                self.eventManager.notify(EventManager.STATION_ERROR, {'error':debug})

        elif t == gst.MESSAGE_STATE_CHANGED:
            self.log.log("Received MESSAGE_STATE_CHANGED")
            oldstate, newstate, pending = message.parse_state_changed()

            if newstate == gst.STATE_PLAYING:
                station = self.mediator.getContext().station
                self.eventManager.notify(EventManager.STATE_CHANGED, {'state':'playing', 'station':station})
            #elif newstate == gst.STATE_NULL:
                #self.mediator.notifyStopped()

        elif t == gst.MESSAGE_TAG:

           taglist = message.parse_tag()
           station = self.mediator.getContext().station
           metadata = {}

           for key in taglist.keys():      
               metadata[key] = taglist[key]

           metadata['station'] = station
           
           self.eventManager.notify(EventManager.SONG_CHANGED, metadata)

        return True
