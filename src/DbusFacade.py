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
import dbus
import dbus.service
import dbus.glib


class DbusFacade(dbus.service.Object):
    def __init__(self, provider, mediator):

        self.dataProvider = provider
        self.mediator = mediator

        bus_name = dbus.service.BusName('net.sourceforge.radiotray', bus=dbus.SessionBus())

        dbus.service.Object.__init__(self, bus_name, '/net/sourceforge/radiotray')


    @dbus.service.method('net.sourceforge.radiotray')
    def listRadios(self):
        return self.dataProvider.listRadioNames()

    @dbus.service.method('net.sourceforge.radiotray')
    def getCurrentRadio(self):
        if self.mediator.isPlaying():
            return self.mediator.getContext().station
        else:
            return self.mediator.getContext().station + " (not playing)"

    @dbus.service.method('net.sourceforge.radiotray')
    def playRadio(self, radioName):
        self.mediator.play(radioName)

    @dbus.service.method('net.sourceforge.radiotray')
    def playUrl(self, url):
        self.mediator.playUrl(url)

    @dbus.service.method('net.sourceforge.radiotray')
    def turnOff(self):
        self.mediator.stop()

    @dbus.service.method('net.sourceforge.radiotray')
    def volumeUp(self):
        self.mediator.volume_up()

    @dbus.service.method('net.sourceforge.radiotray')
    def volumeDown(self):
        self.mediator.volume_down()

    @dbus.service.method('net.sourceforge.radiotray')
    def getCurrentMetaData(self):
        return self.mediator.getContext().getSongInfo()

    @dbus.service.method('net.sourceforge.radiotray')
    def togglePlay(self):
        if self.mediator.context.state == 'playing' or self.mediator.context.state == 'connecting':
            self.mediator.stop()
        else:
            self.mediator.playLast()
