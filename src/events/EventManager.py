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


class EventManager:

    STATE_CHANGED = 'state_changed'
    SONG_CHANGED = 'song_changed'
    BOOKMARKS_CHANGED = 'bookmarks_changed'
    STATION_ERROR = 'station_error'
    VOLUME_CHANGED = 'volume_changed'
    BOOKMARKS_RELOADED = 'bookmarks_reloaded'

    def __init__(self):

        
        self.observersMap = {self.STATE_CHANGED:[], self.SONG_CHANGED:[], self.BOOKMARKS_CHANGED:[], self.STATION_ERROR:[], self.VOLUME_CHANGED:[], self.BOOKMARKS_RELOADED:[]}
        
    
    def getObserversMap(self):
        return self.observersMap
    
    def notify(self, event, data):
        
        observersList = self.observersMap[event]
        
        for callback in observersList:
            callback(data)
