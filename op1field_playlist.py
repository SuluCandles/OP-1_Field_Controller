from op1field_constants import *
from op1field_states import *
import midi
import transport
import device
import ui
import channels
import patterns
import mixer
import playlist
import arrangement
import plugins
import general
from itertools import cycle

class PlaylistState(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        def doChange(change):
            print("jog playlist track by: " + str(change))
            prev = self._selectedPlaylistTrack
            playlist.deselectAll()
            if self._selectedPlaylistTrack == MAX_PLAYLIST_TRACK and change > 0:
                self._selectedPlaylistTrack = MIN_PLAYLIST_TRACK
            elif self._selectedPlaylistTrack == MIN_PLAYLIST_TRACK and change < 0:
                self._selectedPlaylistTrack = MAX_PLAYLIST_TRACK
            else:
                self._selectedPlaylistTrack += change
            playlist.selectTrack(self._selectedPlaylistTrack)
            if prev == MIN_PLAYLIST_TRACK and self._selectedPlaylistTrack == MAX_PLAYLIST_TRACK:
                for i in range(1,MAX_PLAYLIST_TRACK-4):
                    transport.globalTransport(midi.FPT_Down, 1)
            elif prev == MAX_PLAYLIST_TRACK and self._selectedPlaylistTrack == MIN_PLAYLIST_TRACK:
                for i in range(1,MAX_PLAYLIST_TRACK-4):
                    transport.globalTransport(midi.FPT_Up, 1)
            elif self._selectedPlaylistTrack > 5 and change == JOG_UP:
                    transport.globalTransport(midi.FPT_Down, 1)
            elif self._selectedPlaylistTrack > 4 and change == JOG_DOWN:
                    transport.globalTransport(midi.FPT_Up, 1)
            return
        if value > self._blueVal:
            self._blueVal = value
            doChange(JOG_UP)
        elif value < self._blueVal:
            self._blueVal = value
            doChange(JOG_DOWN)
        elif value == self._blueVal:
            if value == MAX_KNOB:
                doChange(JOG_UP)
            elif value == MIN_KNOB:
                doChange(JOG_DOWN)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleOchre(self, control, value):
        def doChange(change):
            print("jog playlist by: " + str(change))
            bar = transport.getSongPos(3) + change - 1
            pos = transport.getSongPos(2) + (change * (general.getRecPPB() * self._scrollSpeed))
            ui.scrollWindow(midi.widPlaylist, bar, 1)
            print(bar)
            transport.setSongPos(pos, 2)
            self._songPosition = pos
            return
        if value > self._ochreVal:
            self._ochreVal = value
            doChange(JOG_UP)
        elif value < self._ochreVal:
            self._ochreVal = value
            doChange(JOG_DOWN)
        elif value == self._ochreVal:
            if value == MAX_KNOB:
                doChange(JOG_UP)
            elif value == MIN_KNOB:
                doChange(JOG_DOWN)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleGray(self, control, value):
        self._state.handleGray(control, value)

    def handleOrange(self, control, value):
        if value > self._orangeVal:
            self._orangeVal = value
            print("changing playlist zoom by: " + str(JOG_UP))
            transport.globalTransport(midi.FPT_HZoomJog, JOG_UP)
        elif value < self._orangeVal:
            self._orangeVal = value
            print("changing playlist zoom by: " + str(JOG_DOWN))
            transport.globalTransport(midi.FPT_HZoomJog, JOG_DOWN)        
        elif value == self._orangeVal:
            if value == MAX_KNOB:
                print("changing playlist zoom by: " + str(JOG_UP))
                transport.globalTransport(midi.FPT_HZoomJog, JOG_UP)            
            elif value == MIN_KNOB:
                print("changing playlist zoom by: " + str(JOG_DOWN))
                transport.globalTransport(midi.FPT_HZoomJog, JOG_DOWN)            
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleBlueButton(self, control, value):
        print("swapping to playlist mode")
        self.controller.setState(PlaylistModeState())
        ui.setHintMsg("playlist mode")
        return

    def handleOchreButton(self, control, value):
        print("muting playlist track: " + str(self._selectedPlaylistTrack))
        playlist.muteTrack(self._selectedPlaylistTrack)
        return
    
    def handleGrayButton(self, control, value):
        print("soloing playlist track: " + str(self._selectedPlaylistTrack))
        playlist.soloTrack(self._selectedPlaylistTrack)
        return

    def handleOrangeButton(self, control, value):
        self._scrollSpeed = next(self._scroll_cycle)
        print("changing scroll speed to: " + str(self._scrollSpeed))
        return