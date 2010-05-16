# Copyright (C) 2010 behrooz shabani (everplays) <behrooz@rock.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.
"""/TrackList object for MPRIS specification interface to radiotray

http://wiki.xmms2.xmms.se/wiki/MPRIS#.2FTrackList_object_methods
"""
import dbus
import dbus.service

INTERFACE_NAME = 'org.freedesktop.MediaPlayer'

class RadioTrayMprisTrackList(dbus.service.Object):

    """
        /TrackList object methods
    """

    def __init__(self, bus): #mediator, provider, bus):
        dbus.service.Object.__init__(self, bus, '/TrackList')
        ## we don't need these yet!
        #self.mediator = mediator
        #self.provider = provider

    @dbus.service.method(INTERFACE_NAME,
            in_signature="i", out_signature="a{sv}")
    def GetMetadata(self, pos):
        """
            Gives all meta data available for element at given position in the
            TrackList, counting from 0

            Each dict entry is organized as follows
              * string: Metadata item name
              * variant: Metadata value
        """
        return {}

    @dbus.service.method(INTERFACE_NAME, out_signature="i")
    def GetCurrentTrack(self):
        """
            Return the position of current URI in the TrackList The return
            value is zero-based, so the position of the first URI in the
            TrackList is 0. The behavior of this method is unspecified if
            there are zero elements in the TrackList.
        """
        return -1

    @dbus.service.method(INTERFACE_NAME, out_signature="i")
    def GetLength(self):
        """
            Number of elements in the TrackList
        """
        return 0

    @dbus.service.method(INTERFACE_NAME,
            in_signature="sb", out_signature="i")
    def AddTrack(self, uri, play_immediately):
        """
            Appends an URI in the TrackList.
        """
        return 0

    @dbus.service.method(INTERFACE_NAME, in_signature="i")
    def DelTrack(self, pos):
        """
            Appends an URI in the TrackList.
        """
        pass

    @dbus.service.method(INTERFACE_NAME, in_signature="b")
    def SetLoop(self, loop):
        """
            Sets the player's "repeat" or "loop" setting
        """
        pass

    @dbus.service.method(INTERFACE_NAME, in_signature="b")
    def SetRandom(self, random):
        """
            Sets the player's "random" setting
        """
        pass

    @dbus.service.signal(INTERFACE_NAME, signature="i")
    def TrackListChange(self, num_of_elements):
        """
            Signal is emitted when the "TrackList" content has changed:
              * When one or more elements have been added
              * When one or more elements have been removed
              * When the ordering of elements has changed

            The argument is the number of elements in the TrackList after the
            change happened.
        """
        pass
