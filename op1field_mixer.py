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

class MixerState(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        if value > self._blueVal:
            print("jogging mixer by: " + str(JOG_UP))
            self._blueVal = value
            ui.jog(JOG_UP)
        elif value < self._blueVal:
            print("jogging mixer by: " + str(JOG_DOWN))
            self._blueVal = value
            ui.jog(JOG_DOWN)
        elif value == self._blueVal:
            if value == MAX_KNOB:
                print("jogging mixer by: " + str(JOG_UP))
                ui.jog(JOG_UP)
            elif value == MIN_KNOB:
                print("jogging mixer by: " + str(JOG_DOWN))
                ui.jog(JOG_DOWN) 
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleOchre(self, control, value):
        print("setting track volume to: " + str(value))
        mixer.setTrackVolume(self._selectedMixerTrack, value/127, 1)
        return

    def handleGray(self, control, value):
        print("setting track pan to: " + str(value))
        mixer.setTrackPan(self._selectedMixerTrack, normalizePolar(value), 1)
        return

    def handleOrange(self, control, value):
        print("seperating stereo by: " + str(value))
        mixer.setTrackStereoSep(self._selectedMixerTrack, normalizePolar(value), 1)
        return

    def handleBlueButton(self, control, value):
        print("swapping to mixer moder")
        self.controller.setState(MixerModeState())
        ui.setHintMsg("mixer mode")
        return

    def handleOchreButton(self, control, value):
        print("muting mixer track: " + str(self._selectedMixerTrack))
        mixer.muteTrack(self._selectedMixerTrack)
        return
    
    def handleGrayButton(self, control, value):
        print("soloing mixer track: " + str(self._selectedMixerTrack))
        mixer.soloTrack(self._selectedMixerTrack)
        return

    def handleOrangeButton(self, control, value):
        print("arming track: " + str(self._selectedMixerTrack) + " for recording")
        mixer.armTrack(self._selectedMixerTrack)
        return