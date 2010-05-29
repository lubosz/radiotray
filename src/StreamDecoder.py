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
from PlsPlaylistDecoder import PlsPlaylistDecoder
from M3uPlaylistDecoder import M3uPlaylistDecoder
from AsxPlaylistDecoder import AsxPlaylistDecoder
from XspfPlaylistDecoder import XspfPlaylistDecoder
from AsfPlaylistDecoder import AsfPlaylistDecoder
from UrlInfo import UrlInfo

class StreamDecoder:

    def __init__(self):
        plsDecoder = PlsPlaylistDecoder()
        m3uDecoder = M3uPlaylistDecoder()
        asxDecoder = AsxPlaylistDecoder()
        xspfDecoder = XspfPlaylistDecoder()
        asfDecoder = AsfPlaylistDecoder()
        
        self.decoders = [plsDecoder, m3uDecoder, asxDecoder, asfDecoder, xspfDecoder]

    

    def getMediaStreamInfo(self, url):

        if url.startswith("http") == False:
            print "Not an HTTP url. Maybe direct stream..."
            return UrlInfo(url, False, None)

        print "Requesting stream... " + url
        myHeaders = {'Range':'bytes=0-20'}
        req = urllib2.Request(url, headers=myHeaders)
        try:
            f = urllib2.urlopen(req, timeout=40)

        except urllib2.URLError, e:
            print "No radio stream found for %s" % url
            return None
        except Exception, e:
            print "No radio stream found. Error: %s" % str(e)
            return None

        metadata = f.info()
        firstbytes = f.read(20)
        print "##>"+firstbytes+"<##"

        f.close()
        print "Metadata obtained..."

        try:
            contentType = metadata["Content-Type"]
            print "Content-Type: " + contentType

        except Exception as e:
            print "Couldn't read content-type. Maybe direct stream..."
            print e
            return UrlInfo(url, False, None)

        for decoder in self.decoders:
                
            print "Checking decoder"
            if(decoder.isStreamValid(contentType, firstbytes)):

                return UrlInfo(url, True, contentType, decoder)
            
        # no playlist decoder found. Maybe a direct stream
        return UrlInfo(url, False, contentType)
        


    def getPlaylist(self, urlInfo):

        return urlInfo.getDecoder().extractPlaylist(urlInfo.getUrl())

