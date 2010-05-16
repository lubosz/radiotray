
import dbus
import dbus.service

INTERFACE_NAME = 'org.freedesktop.MediaPlayer'

class MprisCaps(object):
    """
        Specification for the capabilities field in MPRIS
    """
    NONE                  = 0
    CAN_GO_NEXT           = 1 << 0
    CAN_GO_PREV           = 1 << 1
    CAN_PAUSE             = 1 << 2
    CAN_PLAY              = 1 << 3
    CAN_SEEK              = 0
    CAN_PROVIDE_METADATA  = 0
    CAN_HAS_TRACKLIST     = 0

Radiotray_CAPS = (MprisCaps.CAN_GO_NEXT
                | MprisCaps.CAN_GO_PREV
                | MprisCaps.CAN_PAUSE
                | MprisCaps.CAN_PLAY
                | MprisCaps.CAN_SEEK
                | MprisCaps.CAN_PROVIDE_METADATA
                | MprisCaps.CAN_HAS_TRACKLIST)


class RadioTrayMprisPlayer(dbus.service.Object):
    def __init__(self, provider, mediator, bus):
        dbus.service.Object.__init__(self, bus, '/Player')
        self.provider = provider
        self.mediator = mediator
        self.lastRadio = None

    @dbus.service.method(INTERFACE_NAME)
    def Next(self):
        """
            Goes to the next element
        """
        pass

    @dbus.service.method(INTERFACE_NAME)
    def Prev(self):
        """
            Goes to the previous element
        """
        pass

    @dbus.service.method(INTERFACE_NAME)
    def Pause(self):
        """
            If playing, pause. If paused, unpause.
        """
        if self.mediator.isPlaying :
            self.Stop()
        else :
            self.Play()

    @dbus.service.method(INTERFACE_NAME)
    def Stop(self):
        """
            Stop playing
        """
        if self.mediator.isPlaying :
			self.lastRadio = self.mediator.getCurrentRadio()
        self.mediator.stop()

    @dbus.service.method(INTERFACE_NAME)
    def Play(self):
        """
            If Playing, rewind to the beginning of the current track, else.
            start playing
        """
        ## what should we play? first radio in list?
        if self.lastRadio is None :
            radios = self.provider.listRadioNames()
            if len(radios)>0 :
                self.mediator.play(radios[0])
        else:
            self.mediator.play(self.lastRadio)

    @dbus.service.method(INTERFACE_NAME, in_signature="b")
    def Repeat(self, repeat):
        """
            Toggle the current track repeat
        """
        pass

    @dbus.service.method(INTERFACE_NAME, out_signature="(iiii)")
    def GetStatus(self):
        """
            Return the status of "Media Player" as a struct of 4 ints:
              * First integer: 0 = Playing, 1 = Paused, 2 = Stopped.
              * Second interger: 0 = Playing linearly , 1 = Playing randomly.
              * Third integer: 0 = Go to the next element once the current has
                finished playing , 1 = Repeat the current element
              * Fourth integer: 0 = Stop playing once the last element has been
                played, 1 = Never give up playing
        """
        if self.mediator.isPlaying:
            playing = 0
        ## forget pause it's radio player
        #elif isPaused:
        #    playing = 1
        else:
            playing = 2
        
        ## does it matter?
        random = 0
        ## Do not have ability to repeat single track
        go_to_next = 0
        ## what about repeat?
        repeat = 0

        return (playing, random, go_to_next, repeat)

    @dbus.service.method(INTERFACE_NAME, out_signature="a{sv}")
    def GetMetadata(self):
        """
            Gives all meta data available for the currently played element.
        """
        return {
            'location' : unicode(self.provider.getRadioUrl(self.mediator.getCurrentRadio())),
            'artist'      : unicode(self.mediator.getCurrentRadio()),
            'title'      : unicode(self.mediator.getCurrentMetaData()),
            'album'      : u'',
            'tracknumber': u'',
            'time'       : 0,
            'mtime'      : 0,
            'genre'      : u'',
            'comment'    : u'',
            'rating'     : 0,
            'year'       : 0,
            'date'       : 0,
            'arturl'     : u'',
            'audio-bitrate': self.mediator.bitrate,
            'audio-samplerate': self.mediator.bitrate
        }

    @dbus.service.method(INTERFACE_NAME, out_signature="i")
    def GetCaps(self):
        """
            Returns the "Media player"'s current capabilities, see MprisCaps
        """
        return Radiotray_CAPS

    @dbus.service.method(INTERFACE_NAME, in_signature="i")
    def VolumeSet(self, volume):
        """
            Sets the volume, arument in the range [0, 100]
        """
        if volume < 0 or volume > 100:
            pass

        self.mediator.set_volume(volume / 100.0)

    @dbus.service.method(INTERFACE_NAME, out_signature="i")
    def VolumeGet(self):
        """
            Returns the current volume (must be in [0;100])
        """
        return self.mediator.getVolume()

    @dbus.service.method(INTERFACE_NAME, in_signature="i")
    def PositionSet(self, millisec):
        """
            Sets the playing position (argument must be in [0, <track_length>]
            in milliseconds)
        """
        pass

    @dbus.service.method(INTERFACE_NAME, out_signature="i")
    def PositionGet(self):
        """
            Returns the playing position (will be [0, track_length] in
            milliseconds)
        """
        return 0

    @dbus.service.signal(INTERFACE_NAME, signature="a{sv}")
    def TrackChange(self, metadata):
        """
            Signal is emitted when the "Media Player" plays another "Track".
            Argument of the signal is the metadata attached to the new "Track"
        """
        pass

    @dbus.service.signal(INTERFACE_NAME, signature="(iiii)")
    def StatusChange(self, struct):
        """
            Signal is emitted when the status of the "Media Player" change. The
            argument has the same meaning as the value returned by GetStatus.
        """
        pass

    @dbus.service.signal(INTERFACE_NAME)
    def CapsChange(self):
        """
            Signal is emitted when the "Media Player" changes capabilities, see
            GetCaps method.
        """
        pass

