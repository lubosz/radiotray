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

class UrlInfo(object):

    def __init__(self, url, playlist, contentType, decoder = None):
        self.url = url
        self.playlist = playlist
        self.contentType = contentType
        self.decoder = decoder

    def isPlaylist(self):
        return self.playlist

    def getContentType(self):
        return self.contentType

    def getDecoder(self):
        return self.decoder

    def getUrl(self):
        return self.url
