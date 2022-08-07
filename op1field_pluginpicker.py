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

class PluginPicker(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        if value > self._blueVal:
            print("jog blue by 1")
            self._blueVal = value
            ui.down(1)
        elif value < self._blueVal:
            print("jog blue by -1")
            self._blueVal = value
            ui.up(1)
        elif value == self._blueVal:
            if value == MAX_KNOB:
                print("jog blue by 1")
                ui.down(1)
            elif value == MIN_KNOB:
                print("jog blue by -1")
                ui.up(1) 
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(value))
        return

    def handleOchre(self, control, value):
        if value > self._ochreVal:
            print("jog ochre by 1")
            self._ochreVal = value
            ui.right(1)
        elif value < self._ochreVal:
            print("jog ochre by -1")
            self._ochreVal = value
            ui.left(1)
        elif value == self._ochreVal:
            if value == MAX_KNOB:
                print("jog ochre by 1")
                ui.right(1)
            elif value == MIN_KNOB:
                print("jog ochre by -1")
                ui.left(1)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(value))
        return

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