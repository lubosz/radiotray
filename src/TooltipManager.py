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
from events.EventManager import EventManager

class TooltipManager(object):

    def __init__(self):
        self.tooltipSources = []


    def setGui(self, gui):
        self.gui = gui


    def addSource(self, callback):
        self.tooltipSources.append(callback)


    def update(self):
        complete = ''
        for src in self.tooltipSources:
            s = src()
            if s != None:
                complete += s + '\n'

        complete = complete.strip("\n")

        self.gui.setTooltip(complete)

    
