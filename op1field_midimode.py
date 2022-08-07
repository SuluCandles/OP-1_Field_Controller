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

class MidiModeState(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        self._state.handleBlue(control, value)

    def handleOchre(self, control, value):
        self._state.handleOchre(control, value)

    def handleGray(self, control, value):
        self._state.handleGray(control, value)

    def handleOrange(self, control, value):
        self._state.handleOrange(control, value)

    def handleBlueButton(self, control, value):
        self._state.handleBlueButton(control, value)

    def handleOchreButton(self, control, value):
        self._state.handleOchreButton(control, value)
    
    def handleGrayButton(self, control, value):
        self._state.handleGrayButton(control, value)

    def handleOrangeButton(self, control, value):
        self._state.handleOrangeButton(control, value)