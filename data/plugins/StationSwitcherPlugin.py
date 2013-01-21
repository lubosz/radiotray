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

# author Mark F  Jan 2013
from Plugin import Plugin
import gtk
import random

class StationSwitcherPlugin(Plugin):

    # Set by parent Plugin.py
    # self.name                   = name
    # self.eventManagerWrapper    = eventManagerWrapper
    # self.eventSubscriber        = eventSubscriber
    # self.provider               = provider
    # self.cfgProvider            = cfgProvider
    # self.mediator               = mediator
    # self.tooltip                = tooltip
        
    def __init__(self):
        super(StationSwitcherPlugin, self).__init__()
        self.shuffle = False   # way to set this property from RadioTray not implemented yet

    def getName(self):
        return self.name
        
    def activate(self):
        # only Next >> button added to avoid cluttering menu.  Play previous can be triggered using other means
        nextMenuItem = gtk.MenuItem("Next >>", False)
        
        # locate the turn on/off menu item and add next button after
        i = 0
        insertIndex = 0
        for child in self.tooltip.gui.radioMenu.get_children():
            if not isinstance(child, gtk.SeparatorMenuItem):
                if child.get_label().startswith("Turn"): 
                    insertIndex = i+1
                    break
                    # break statement is required due to bug/feature in gtk.  Examining MenuItem labels on 'separators' causes
                    # them not to be displayed correctly.  If gui classes are modified to use SeparatorMenuItem break can be removed 
            i+=1
            
        self.tooltip.gui.radioMenu.insert(nextMenuItem,insertIndex)
        nextMenuItem.connect('activate', self.on_next)
        nextMenuItem.show()    

    def on_next(self,data):
        self.playNextRadio()
        
    def playPreviousRadio(self):
        self.mediator.play(self.getPreviousRadio())
        
    def playNextRadio(self):
        self.mediator.play(self.getNextRadio())

    def getNextRadio(self):
        if self.shuffle: return self.getRandomRadio()
        
        allRadios = self.provider.listRadioNames()
        lastStation = self.mediator.cfg_provider.getConfigValue("last_station")
        lastStationIndex = allRadios.index(lastStation)

        if lastStationIndex==len(allRadios)-1: nextStationIndex=0
        else: nextStationIndex=lastStationIndex+1
        
        return allRadios[nextStationIndex]

    def getPreviousRadio(self):
        if self.shuffle: return self.getRandomRadio()
        
        allRadios = self.provider.listRadioNames()
        lastStation = self.mediator.cfg_provider.getConfigValue("last_station")
        lastStationIndex = allRadios.index(lastStation)

        if lastStationIndex==0: previousStationIndex=len(allRadios)-1
        else: previousStationIndex=lastStationIndex-1
        
        return allRadios[previousStationIndex]
    
    def getRandomRadio(self):
        
        allRadios = self.provider.listRadioNames()
        lastStation = self.mediator.cfg_provider.getConfigValue("last_station")
        lastStationIndex = allRadios.index(lastStation)

        randomStationIndex = lastStationIndex
        while (randomStationIndex==lastStationIndex):
            randomStationIndex = random.randint(0, len(allRadios)-1)
        
        return allRadios[randomStationIndex]
    
    def hasMenuItem(self):
        return True
    
    def on_menu(self, data):
        #plugin config gui goes here.  Need to add option for random station select
        print ""

