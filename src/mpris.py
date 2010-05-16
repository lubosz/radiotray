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

"""
An implementation of the MPRIS D-Bus protocol for use with radiotray based on Exaile's MPRIS plugin
"""

import dbus
import dbus.service

import mpris_root
import mpris_tracklist
import mpris_player

OBJECT_NAME = 'org.mpris.radiotray'

class RadioTrayMpris(object):

    """
        Controller for various MPRIS objects.
    """

    def __init__(self, provider, mediator):
        """
            Constructs an MPRIS controller. Note, you must call acquire()
        """
        self.bus = dbus.service.BusName(OBJECT_NAME, bus=dbus.SessionBus())
        mpris_root.RadioTrayMprisRoot(mediator, self.bus) # don't need provider
        mpris_player.RadioTrayMprisPlayer(provider, mediator, self.bus)
        mpris_tracklist.RadioTrayMprisTrackList(self.bus) # actually TrackList doesn't provide anything yet

