from op1field_constants import *
from op1field_states import *
from op1field_midimode import *
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

class ChannelState(State):

    def handleFour(self, control, value):
        selected = self.controller._selectedGrid
        mult = 1
        if control == oneButton:
            if channels.getGridBit(channels.selectedChannel(), selected):
                print("grid removed at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected, 0)
            else:
                print("grid added at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected, 1)
        elif control == twoButton:
            if channels.getGridBit(channels.selectedChannel(), selected+(1*mult)):
                print("grid removed at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected+(1*mult), 0)
            else:
                print("grid added at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected+(1*mult), 1)
        elif control == threeButton:
            if channels.getGridBit(channels.selectedChannel(), selected+(2*mult)):
                print("grid removed at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected+(2*mult), 0)
            else:
                print("grid added at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected+(2*mult), 1)
        elif control == fourButton:
            if channels.getGridBit(channels.selectedChannel(), selected+(3*mult)):
                print("grid removed at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected+(3*mult), 0)
            else:
                print("grid added at: " + str(selected))
                channels.setGridBit(channels.selectedChannel(), selected+(3*mult), 1)
        else:
            print("unrecognized: " + str(control) + "," + str(value))
        return
        
    def handleBlue(self, control, value):
        if value > _blueVal:
            print("jog channel by 1")
            _blueVal = value
            ui.jog(JOG_UP)
        elif value < _blueVal:
            print("jog channel by -1")
            _blueVal = value
            ui.jog(JOG_DOWN)
        elif value == _blueVal:
            if value == MAX_KNOB:
                print("jog channel by 1")
                ui.jog(JOG_UP)
            elif value == MIN_KNOB:
                print("jog channel by -1")
                ui.jog(JOG_DOWN) 
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        ui.crDisplayRect(self._selectedGrid, channels.selectedChannel(), 4, 1, 5000)
        return

    def handleOchre(self, control, value):
        if value > self._ochreVal:
            print("jog channel grid by 1")
            self._ochreVal = value
            if self._selectedGrid == MAX_GRID_LENGTH:
                self._selectedGrid = 0
            else:
                self._selectedGrid += 4
        elif value < self._ochreVal:
            print("jog channel grid by -1")
            self._ochreVal = value
            if self._selectedGrid == MIN_GRID_LENGTH:
                self._selectedGrid = 0
            else:
                self._selectedGrid -= 4
        elif value == self._ochreVal:
            if value == MAX_KNOB:
                print("jog channel grid by 1")
                if self._selectedGrid == MAX_GRID_LENGTH:
                    self._selectedGrid = 0
                else:
                    self._selectedGrid += 4
            elif value == MIN_KNOB:
                print("jog channel grid by -1")
                if self._selectedGrid == MIN_GRID_LENGTH:
                    self._selectedGrid = 0
                else:
                    self._selectedGrid -= 4
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        
        ui.crDisplayRect(self._selectedGrid, channels.selectedChannel(), 4, 1, 5000)
        return

    def handleGray(self, control, value):
        self._grayVal = value
        print("setting channel volume to: " + str(value))
        channels.setChannelVolume(channels.selectedChannel(), value/MAX_KNOB)
        return

    def handleOrange(self, control, value):
        print("changing pattern by: " + str(value))
        if value > self._orangeVal:
            self._orangeVal = value
            transport.globalTransport(midi.FPT_PatternJog, JOG_UP)
        elif value < self._orangeVal:
            self._orangeVal = value
            transport.globalTransport(midi.FPT_PatternJog, JOG_DOWN)
        elif value == self._orangeVal:
            if value == MAX_KNOB:
                transport.globalTransport(midi.FPT_PatternJog, JOG_UP)
            elif value == MIN_KNOB:
                transport.globalTransport(midi.FPT_PatternJog, JOG_DOWN)
            else:
                print("this shouldn't happen here")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleBlueButton(self, control, value):
        print("swapping to midi mode")
        ui.setHintMsg("channel rack - midi mode")
        self.controller.setState(MidiModeState())
        return

    def handleOchreButton(self, control, value):
        print("muting channel: " + str(channels.selectedChannel()))
        channels.muteChannel(channels.selectedChannel())    
        return

    def handleGrayButton(self, control, value):
        print("soloing channel: " + str(channels.selectedChannel()))
        channels.soloChannel(channels.selectedChannel())
        return

    def handleOrangeButton(self, control, value):
        index = channels.selectedChannel()
        ui.copy
        name = channels.getChannelName(index)
        color = channels.getChannelColor(index)
        patterns.findFirstNextEmptyPat(midi.FFNEP_DontPromptName)
        pattern = patterns.patternNumber()
        patterns.setPatternName(pattern, name)
        patterns.setPatternColor(pattern, color)
        patterns.jumpToPattern(pattern)
        return