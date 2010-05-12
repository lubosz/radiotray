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
"""/ Object for MPRIS specification interface to radioTray

http://wiki.xmms2.xmms.se/wiki/MPRIS#.2F_.28Root.29_object_methods
"""
import dbus
import dbus.service
import lib.common as common
from SysTray import SysTray

INTERFACE_NAME = 'org.freedesktop.MediaPlayer'

class RadioTrayMprisRoot(dbus.service.Object):

    """
        / (Root) object methods
    """

    def __init__(self, mediator, bus):
        dbus.service.Object.__init__(self, bus, '/')
        self.mediator = mediator

    @dbus.service.method(INTERFACE_NAME, out_signature="s")
    def Identity(self):
        """
            Identify the "media player"
        """
        return "%s %s" % (common.APPNAME, common.APPVERSION)

    @dbus.service.method(INTERFACE_NAME)
    def Quit(self):
        """
            Makes the "Media Player" exit.
        """
        self.mediator.systray.on_quit(1)

    @dbus.service.method(INTERFACE_NAME, out_signature="(qq)")
    def MprisVersion(self):
        """
            Makes the "Media Player" exit.
        """
        return (1, 0)

