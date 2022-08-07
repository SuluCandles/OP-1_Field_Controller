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

class PlaylistModeState(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        print("jog playhead by: " + str(value))
        if value > self._blueVal:
            self._blueVal = value
            ui.jog(JOG_UP)
        elif value < self._blueVal:
            self._blueVal = value
            ui.jog(JOG_DOWN)
        elif value == self._blueVal:
            if value == MAX_KNOB:
                ui.jog(JOG_UP)
            elif value == MIN_KNOB:
                ui.jog(JOG_DOWN)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleOchre(self, control, value):
        if value > self._ochreVal:
            self._ochreVal = value
            print("jumping marker by: " + str(JOG_UP))
            arrangement.jumpToMarker(JOG_UP, False)
        elif value < self._ochreVal:
            self._ochreVal = value
            print("jumping marker by: " + str(JOG_DOWN))
            arrangement.jumpToMarker(JOG_DOWN, False)
        elif value == self._ochreVal:
            if value == MAX_KNOB:
                print("jumping marker by: " + str(JOG_UP))
                arrangement.jumpToMarker(JOG_UP, False)
            elif value == MIN_KNOB:
                print("jumping marker by: " + str(JOG_DOWN))
                arrangement.jumpToMarker(JOG_DOWN, False)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleGray(self, control, value):
        def doChange(change):
            print("jog playlist track by: " + str(change))
            prev = self._selectedPlaylistTrack
            #playlist.deselectAll()
            if self._selectedPlaylistTrack == MAX_PLAYLIST_TRACK and change > 0:
                self._selectedPlaylistTrack = MIN_PLAYLIST_TRACK
            elif self._selectedPlaylistTrack == MIN_PLAYLIST_TRACK and change < 0:
                self._selectedPlaylistTrack = MAX_PLAYLIST_TRACK
            else:
                self._selectedPlaylistTrack += change
            if not playlist.isTrackSelected(self._selectedPlaylistTrack): playlist.selectTrack(self._selectedPlaylistTrack)
            else: playlist.selectTrack(self._selectedPlaylistTrack)
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
        if value > self._grayVal:
            self._grayVal = value
            doChange(JOG_UP)
        elif value < self._grayVal:
            self._grayVal = value
            doChange(JOG_DOWN)
        elif value == self._grayVal:
            if value == MAX_KNOB:
                doChange(JOG_UP)
            elif value == MIN_KNOB:
                doChange(JOG_DOWN)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

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
        print("back to playlist mode")
        self.controller.setState(PlaylistState())
        ui.setHintMsg("control mode - playlist")
        return

    def handleOchreButton(self, control, value):
        print("adding marker")
        arrangement.addAutoTimeMarker(arrangement.currentTime(False), patterns.getPatternName(patterns.patternNumber()))
        return

    def handleGrayButton(self, control, value):
        self._state.handleGrayButton(control, value)

    def handleOrangeButton(self, control, value):
        if self._isSELECTING:
            self._isSELECTING = False
            self._hasSELECTED = True
            print("placing live loop end")
            arrangement.liveSelection(arrangement.currentTime(False), True)
        else:
            if self._hasSELECTED:
                print("removing selected region")
                self._hasSELECTED = False
                arrangement.liveSelection(arrangement.currentTime(False), False)
                arrangement.liveSelection(arrangement.currentTime(False), True)
                return
            self._isSELECTING = True
            print("placing live loop start")
            arrangement.liveSelection(arrangement.currentTime(False), False)
        return