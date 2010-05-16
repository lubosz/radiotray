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

class StreamDecoder:

    def __init__(self):
        plsDecoder = PlsPlaylistDecoder()
        m3uDecoder = M3uPlaylistDecoder()
        asxDecoder = AsxPlaylistDecoder()
        xspfDecoder = XspfPlaylistDecoder()
        self.formats = {
            'audio/x-scpls': plsDecoder,
            'audio/mpegurl': m3uDecoder,
            'audio/x-mpegurl': m3uDecoder,
            'video/x-ms-asf': asxDecoder,
            'audio/x-ms-wax': asxDecoder,
            'video/x-ms-wvx': asxDecoder,
            'application/xspf+xml': xspfDecoder
        }

    def extractStream(self, url):
        if url.startswith("http") == False:
            print "Not an HTTP url. Maybe direct stream..."
            return [url]

        print "Requesting stream... " + url
        myHeaders = {'Range':'bytes=0-9'}
        req = urllib2.Request(url, headers=myHeaders)
        try:
            f = urllib2.urlopen(req)
        except urllib2.URLError, e:
            print "No radio stream found for %s" % url
            return [url]
        except Exception, e:
            print "No radio stream found. Error: %s" % str(e)
            return [url]

        metadata = f.info()
        f.close()
        print "Metadata obtained..."

        try:
            contentType = metadata["Content-Type"]
            print "Content-Type: " + contentType

            format = self.formats[contentType]
            if format == None:
                print "No known formats found. Maybe direct stream..."
                return [url]
            else:
                print "Format detected"
                mediaUrl = format.extractStream(url)
                return mediaUrl
        except:
            print "Couldn't read content-type"
            return [url]
