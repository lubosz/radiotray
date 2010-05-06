#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dbus
import sys, os, string
from RadioTray import RadioTray
from dbus import DBusException

current_path = os.path.realpath(__file__)
basedir = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(basedir, "radiotray.py")):
    if os.path.exists(os.path.join(os.getcwd(), "radiotray.py")):
        basedir = os.getcwd()
sys.path.insert(0, basedir)
os.chdir(basedir)

def main(argv):
    if(len(argv) == 1):
        print "Trying to load URL: " + argv[0]

        try:
            bus = dbus.SessionBus()
            radiotray = bus.get_object('net.sourceforge.radiotray', '/net/sourceforge/radiotray')

            print "Radio Tray already running. Setting current radio through DBus..."

            playUrl = radiotray.get_dbus_method('playUrl', 'net.sourceforge.radiotray')
            playUrl(argv[0])

        except DBusException:
            RadioTray(argv[0])
    else:
        RadioTray()

if __name__ == "__main__":
    main(sys.argv[1:])
