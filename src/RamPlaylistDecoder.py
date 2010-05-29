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

class RamPlaylistDecoder:

    def __init__(self):
        print "RAM playlist decoder"

    def isStreamValid(self, contentType, firstBytes):

        if(contentType == 'audio/x-pn-realaudio' or contentType == 'audio/vnd.rn-realaudio'):
            print 'Stream is readable by RAM Playlist Decoder'
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
                tmp = line.strip()
                if(len(tmp) > 0):
                    playlist.append(line.strip())

        return playlist
