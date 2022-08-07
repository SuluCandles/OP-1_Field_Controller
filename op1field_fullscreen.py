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

class FullscreenState(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        self._state.handleBlue(control, value)

    def handleOchre(self, control, value):
        self._state.handleOchre(control, value)

    def handleGray(self, control, value):
        self._state.handleGray(control, value)

    def handleOrange(self, control, value):
        if value > self._orangeVal:
            self._orangeVal = value
            transport.globalTransport(midi.FPT_HZoomJog, JOG_UP)
        elif value < self._orangeVal:
            self._orangeVal = value
            transport.globalTransport(midi.FPT_HZoomJog, JOG_DOWN)
        elif value == self._orangeVal:
            if value == MAX_KNOB:
                transport.globalTransport(midi.FPT_HZoomJog, JOG_UP)
            elif value == MIN_KNOB:
                transport.globalTransport(midi.FPT_HZoomJog, JOG_DOWN)
            else:
                print("this shouldn't happen here")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleBlueButton(self, control, value):
        ui.enter(1)
        print("fullscreening piano roll")
        self.controller.setState(FullscreenState())
        ui.setHintMsg("piano roll - full screen")
        return
        
    def handleOchreButton(self, control, value):
        self._state.handleOchreButton(control, value)
    
    def handleGrayButton(self, control, value):
        self._state.handleGrayButton(control, value)

    def handleOrangeButton(self, control, value):
        self._state.handleOrangeButton(control, value)