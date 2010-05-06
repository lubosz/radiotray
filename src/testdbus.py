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
import sys
import getopt


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "hlr:s", ["help", "list", "radio=", "stop", "up", "down", "current", "metadata", "url="])

        bus = dbus.SessionBus()
        radiotray = bus.get_object('net.sourceforge.radiotray', '/net/sourceforge/radiotray')

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                sys.exit()
            elif opt in ("-l", "--list"):
                listRadios = radiotray.get_dbus_method('listRadios', 'net.sourceforge.radiotray')
                print listRadios()

            elif opt in ("-r", "--radio"):
                playRadio = radiotray.get_dbus_method('playRadio', 'net.sourceforge.radiotray')
                playRadio(arg)

            elif opt in ("-s", "--stop"):
                turnOff = radiotray.get_dbus_method('turnOff', 'net.sourceforge.radiotray')
                turnOff()

            elif opt in ("--up"):
                volumeUp = radiotray.get_dbus_method('volumeUp', 'net.sourceforge.radiotray')
                volumeUp()

            elif opt in ("--down"):
                volumeDown = radiotray.get_dbus_method('volumeDown', 'net.sourceforge.radiotray')
                volumeDown()

            elif opt in ("--current"):
                getRadio = radiotray.get_dbus_method('getCurrentRadio', 'net.sourceforge.radiotray')
                print getRadio()

            elif opt in ("--metadata"):
                getMetadata = radiotray.get_dbus_method('getCurrentMetaData', 'net.sourceforge.radiotray')
                print getMetadata()

            elif opt in ("--url"):
                print "play url"
                playUrl = radiotray.get_dbus_method('playUrl', 'net.sourceforge.radiotray')
                playUrl(arg)

    except getopt.GetoptError:
        sys.exit(2)



if __name__ == "__main__":
    main(sys.argv[1:])
