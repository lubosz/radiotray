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

class AudioPlayerGStreamer:

    def __init__(self, mediator, log):
        self.mediator = mediator
        self.log = log
        self.decoder = StreamDecoder()
        self.playlist = []

        # init player
        self.player = gst.element_factory_make("playbin", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)


    def start(self, uri):
        self.playlist = self.decoder.extractStream(uri)
        self.playNextStream()

    def playNextStream(self):
        if(len(self.playlist) > 0):
            stream = self.playlist.pop(0)
            print "Play " + stream
            self.player.set_property("uri", stream)
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.stop()
            self.mediator.notifyStopped()

    def stop(self):
        self.player.set_state(gst.STATE_NULL)



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

            if(len(self.playlist)>0):
                self.playNextStream()
            else:
                self.mediator.notifyError(err, debug)
        elif t == gst.MESSAGE_STATE_CHANGED:
            self.log.log("Received MESSAGE_STATE_CHANGED")
            oldstate, newstate, pending = message.parse_state_changed()

            if newstate == gst.STATE_PLAYING:
                self.mediator.notifyPlaying()
            elif newstate == gst.STATE_NULL:
                self.mediator.notifyStopped()

        elif t == gst.MESSAGE_TAG:

           taglist = message.parse_tag()
           for key in taglist.keys():
           	if (key == 'title'):
                	print "TITLE: " + taglist[key]
            		self.mediator.notifySong(taglist[key])

        return True
