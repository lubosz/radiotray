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

class Context:

    station = None
    url = ""
    title = ""
    artist = None
    album = None
    state = None
    STATE_PLAYING = "playing"
    STATE_CONNECT = "connecting"
    STATE_PAUSED = "paused"
    UNKNOWN_RADIO = C_("Unknown radio specified by URL", "Unknown radio")
    
    
    def getSongInfo(self):

        if(self.title and len(self.title) > 0 and self.artist and len(self.artist) > 0):
            return self.artist + " - " + self.title
        elif(self.title and len(self.title) > 0):
            return self.title
        elif(self.artist and len(self.artist) > 0):
            return self.artist
        else:
            return 'unknown'
            
