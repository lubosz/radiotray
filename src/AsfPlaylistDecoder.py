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
from lxml import etree
from lxml import objectify
from StringIO import StringIO

class AsfPlaylistDecoder:

    def __init__(self):
        print "ASF playlist decoder"


    def isStreamValid(self, contentType, firstBytes):

        if('video/x-ms-asf' in contentType and firstBytes.strip().lower().startswith('[reference]')):
            print "Stream is readable by ASF Playlist Decoder"
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

        playlist = []
        lines = str.split("\n")
        for line in lines:

            if (line.startswith("Ref") == True):

                list = line.split("=", 1)
                tmp = list[1].strip()

                if (tmp.endswith("?MSWMExt=.asf")):
                    playlist.append(tmp.replace("http", "mms"))
                else:
                    playlist.append(tmp)
         
        return playlist

