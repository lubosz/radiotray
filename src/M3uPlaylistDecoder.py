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
import urllib2

class M3uPlaylistDecoder:

    def __init__(self):
        print "M3U playlist decoder"

    def isStreamValid(self, contentType, firstBytes):

        if('audio/mpegurl' in contentType or 'audio/x-mpegurl' in contentType):
            print 'Stream is readable by M3U Playlist Decoder'
            return True
        else:
            return False



    def extractPlaylist(self,  url):
        print "Downloading playlist..."

        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        str = f.read()
        f.close()

        print "Playlist downloaded"
        print "Decoding playlist..."

        lines = str.split("\n")
        playlist = []

        for line in lines:
            if line.startswith("#") == False and len(line) > 0:
                playlist.append(line)

        return playlist
