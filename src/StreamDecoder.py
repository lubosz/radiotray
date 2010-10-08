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
from lib.common import USER_AGENT
from PlsPlaylistDecoder import PlsPlaylistDecoder
from M3uPlaylistDecoder import M3uPlaylistDecoder
from AsxPlaylistDecoder import AsxPlaylistDecoder
from XspfPlaylistDecoder import XspfPlaylistDecoder
from AsfPlaylistDecoder import AsfPlaylistDecoder
from RamPlaylistDecoder import RamPlaylistDecoder
from UrlInfo import UrlInfo

class StreamDecoder:

    def __init__(self, cfg_provider):
        plsDecoder = PlsPlaylistDecoder()
        m3uDecoder = M3uPlaylistDecoder()
        asxDecoder = AsxPlaylistDecoder()
        xspfDecoder = XspfPlaylistDecoder()
        asfDecoder = AsfPlaylistDecoder()
        ramDecoder = RamPlaylistDecoder()
        
        self.decoders = [plsDecoder, asxDecoder, asfDecoder, xspfDecoder, ramDecoder, m3uDecoder]

        self.url_timeout = None

        try:
            self.url_timeout = cfg_provider.getConfigValue("url_timeout")
            if (self.url_timeout == None):
                print "Couldn't find url_timeout configuration"
                self.url_timeout = 2000
                cfg_provider.setConfigValue("url_timeout", str(self.url_timeout))
        except Exception, e:
            print "Couldn't find url_timeout configuration"
            self.url_timeout = 2000
            cfg_provider.setConfigValue("url_timeout", str(self.url_timeout))

        print "Using url timeout = " + str(self.url_timeout)


    def getMediaStreamInfo(self, url):

        if url.startswith("http") == False:
            print "Not an HTTP url. Maybe direct stream..."
            return UrlInfo(url, False, None)

        print "Requesting stream... " + url
        req = urllib2.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        try:
            f = urllib2.urlopen(req, timeout=float(self.url_timeout))

        except urllib2.URLError, e:
            print "No radio stream found for %s" % url
            return None
        except Exception, e:
            print "No radio stream found. Error: %s" % str(e)
            return None

        metadata = f.info()
        firstbytes = f.read(500)
        f.close()
        
        try:            
            print "Metadata obtained..."
            contentType = metadata["Content-Type"]
            print "Content-Type: " + contentType
            

        except Exception, e:
            print "Couldn't read content-type. Maybe direct stream..."
            print "Error: ",e
            return UrlInfo(url, False, None)

        for decoder in self.decoders:
                
            print "Checking decoder"
            if(decoder.isStreamValid(contentType, firstbytes)):

                return UrlInfo(url, True, contentType, decoder)
            
        # no playlist decoder found. Maybe a direct stream
        return UrlInfo(url, False, contentType)
        


    def getPlaylist(self, urlInfo):

        return urlInfo.getDecoder().extractPlaylist(urlInfo.getUrl())

