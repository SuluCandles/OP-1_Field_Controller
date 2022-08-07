from itertools import cycle

from op1field_synth import SynthMode
from op1field_channel import ChannelState
from op1field_browser import BrowserState
from op1field_menu import MenuState
from op1field_fullscreen import FullscreenState
from op1field_mixer import MixerState
from op1field_mixermode import MixerModeState
from op1field_pianoroll import PianoRollState
from op1field_playlist import PlaylistState
from op1field_playlistmode import PlaylistModeState
from op1field_pluginpicker import PluginPicker
from op1field_constants import *

import ui
import transport
import midi
import general

class Controller:

    _state = None
    _prevState = None
    _focusedWindow = 0
    _songPosition = 0
    _scroll_cycle = cycle(SCROLL_SPEED)
    _scrollSpeed = next(_scroll_cycle)
    _selectedGrid = 0
    _selectedMixerTrack = 0
    _selectedRouteTrack = 0
    _selectedPianoGrid = 0
    _selectedPlaylistTrack = 0

    _isSELECTING = False
    _hasSELECTED = False

    _blueVal = 0
    _ochreVal = 0
    _grayVal = 0
    _orangeVal = 0

    def __init__(self, state) -> None:
        self.setState(state)
    
    def setState(self, state):
        print(f"controller: transitioning to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def OnInit():
        print("please be in synth mode")
        ui.setHintMsg("synth mode")

    def OnDeInit():
        print("goodbye :)")

    
    def OnMidiIn(self, event):
        if self._state == SynthMode():
            self._state.OnMidiIn(event)
        control = event.data1
        value = event.data2
        if event.status == CONTROL_STATUS:
            if control in opTRANSPORT:
                self.handleTransport(control, value)
            elif control in opCONTROL:
                self.handleControl(control, value)
            elif control in opEDIT:
                self.handleEdit(control, value)
            elif control in opMACROS:
                self.handleMacro(control, value)
            elif control in opFOUR:
                self.handleFour(control, value)
            elif control in opSPECIAL:
                self.handleSpecial(control, value)
            elif control in opKNOBBUTTON:
                self.handleKnobButton(control, value)
            elif control in opKNOBS:
                self.handleKnobs(control, value)
            else:
                print("unrecognized: " + str(control) + ", " + str(value))
        
        event.handled = True

    def handleTransport(self, control, value):
        if value == 0:
            return
        print("transport")
        if transport.isPlaying():
            if control == playButton:
                print("wrong pause button")
                transport.start()
                self._songPosition = transport.getSongPos(2)
            elif control == stopButton:
                print("pausing playback...")
                transport.start()
                self._songPosition = transport.getSongPos(2)
        else:
            if control == playButton:
                print("starting playback...")
                transport.start()
            elif control == stopButton:
                print("returning to start")
                transport.stop()
                self._songPosition = 0
            elif control == recButton:
                print("recording enabled")
                transport.record()
            else:
                print("unrecognized: " + str(control) + "," + str(value))
        return

    def handleControl(self, control, value):
        if value == 0:
            return
        if control == synthButton:
            if self._state == PluginPicker():
                self.setState(ChannelState())
                print("closing plugin picker")
            else:
                self.setState(PluginPicker())
                print("opening plugin picker")
            transport.globalTransport(midi.FPT_F8, 1)
        elif control == drumButton:
            self.setState(ChannelState())
            print("focusing channel rack")
            _focusedWindow = midi.widChannelRack
            ui.setHintMsg("control mode - channel rack")
        elif control == tapeButton:
            self.setState(PlaylistState())
            print("focusing playlist")
            _focusedWindow = midi.widPlaylist
            ui.setHintMsg("control mode - playlist")
        elif control == mixerButton:
            self.setState(MixerState())
            print("focusing mixer")
            _focusedWindow = midi.widMixer
            ui.setHintMsg("control mode - mixer")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        if not ui.getVisible(_focusedWindow):
            ui.showWindow(_focusedWindow)
        ui.setFocused(_focusedWindow)
        return

    def handleEdit(self, control, value):
        if value == 0:
            return
        if control == liftButton:
            print("cutting...")
            transport.globalTransport(midi.FPT_Cut, 1)
        elif control == dropButton:
            print("pasting...")
            transport.globalTransport(midi.FPT_Paste, 1)
        elif control == cutButton:
            print("menu")
            if self._focusedWindow == midi.widPlaylist or self._focusedWindow == PIANO_ROLL:
                transport.globalTransport(midi.FPT_Menu, 2)
                return
            transport.globalTransport(midi.FPT_ItemMenu, 2)
        return

    def handleMacro(self, control, value):
        if value == 0:
            return
        print("macro button pressed")
        if control == opOne:
            print("undoing")
            general.undoUp()
        elif control == opTwo:
            print("redoing")
            general.undoDown()
        elif control == opThr:
            print("toggling loop recording")
            transport.globalTransport(midi.FPT_WaitForInput, 1)
        elif control == opFor:
            print("swapping loop mode")
            transport.setLoopMode()
        elif control == opFiv:
            print("jogging snap mode")
            transport.globalTransport(midi.FPT_SnapMode, 1)
        elif control == opSix:
            print("toggling browsing")
            if self._state == BrowserState(): 
                self.setState(ChannelState())
                ui.setFocused(midi.widChannelRack)
            else:
                self.setState(BrowserState())
                ui.setFocused(midi.widBrowser)
        elif control == opSev:
            print("seven")
        elif control == opEit:
            print("eight")
        return

    def handleSpecial(self, control, value):
        if value == 0:
            return
        if control == tempoButton:
            print("metronome pressed")
            transport.globalTransport(midi.FPT_Metronome, 1)
        elif control == seqButton:
            if _focusedWindow == PIANO_ROLL:
                print("closing piano roll")
                transport.globalTransport(midi.FPT_F7, 1)
                _focusedWindow = midi.widChannelRack
                ui.setFocused(midi.widChannelRack)
                self.setState(ChannelState())
            else:    
                print("opening piano roll")
                _focusedWindow = PIANO_ROLL
                transport.globalTransport(midi.FPT_F7, 1)
                self.setState(PianoRollState())
        elif control == micButton:
            print("panic!")
            transport.globalTransport(midi.FPT_F12, 1)
            transport.stop()
        elif control == comButton:
            print("emulating enter")
            transport.globalTransport(midi.FPT_Enter, 1)
        elif control == helpButton:
            print("help button pressed")
            transport.globalTransport(midi.FPT_WaitForInput, 1)
        return
    
    def handleKnobs(self, control, value):
        print("knob tweaked")
        if control == blueKnob:
            self._state.handleBlue(control, value)
        elif control == ochreKnob:
            self._state.handleOchre(control, value)
        elif control == grayKnob:
            self._state.handleGray(control, value)
        elif control == orangeKnob:
            self._state.handleOrange(control, value)
        else:
            print("unrecognized: " + str(control) + ", " + str(value))  
        return

    def handleKnobButton(self, control, value):
        if value == 0:
            return
        print("knob pressed")
        if control == blueButton:
            self._state.handleBlueButton(control, value)
        elif control == ochreButton:
            self._state.handleOchreButton(control, value)
        elif control == grayButton:
            self._state.handleGrayButton(control, value)
        elif control == orangeButton:
            self._state.handleOrangeButton(control, value)
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleFour(self, control, value):
        self._state.handleFour(control, value)

class State():

    @property
    def controller(self) -> Controller:
        return self._controller

    @controller.setter
    def controller(self, controller: Controller) -> None:
        self._controller = controller

#    @abstractmethod
    def OnMidiIn(self, event) -> None:
        self._state.OnMidiIn(event)

#    @abstractmethod
    def handleTransport(self, control, value):
        self._state.handleTransport(control, value)
    
#    @abstractmethod
    def handleControl(self, control, value):
        self._state.handleControl(control, value)

#    @abstractmethod
    def handleTransport(self, control, value):
        self._state.handleEdit(control, value)

#    @abstractmethod
    def handleMacro(self, control, value):
        self._state.handleTransport(control, value)

#    @abstractmethod
    def handleFour(self, control, value):
        self._state.handleFour(control, value)

#    @abstractmethod
    def handleSpecial(self, control, value):
        self._state.handleSpecial(control, value)

#    @abstractmethod
    def handleKnobButton(self, control, value):
        self._state.handleKnobButton(control, value)

#    @abstractmethod
    def handleKnobs(self, control, value):
        self._state.handleKnobs(control, value)

#    @abstractmethod
    def handleBlue(self, control, value):
        self._state.handleBlue(control, value)

#    @abstractmethod
    def handleOchre(self, control, value):
        self._state.handleOchre(control, value)

#    @abstractmethod
    def handleGray(self, control, value):
        self._state.handleGray(control, value)

#    @abstractmethod
    def handleOrange(self, control, value):
        self._state.handleOrange(control, value)

#    @abstractmethod
    def handleBlueButton(self, control, value):
        self._state.handleBlueButton(control, value)

#    @abstractmethod
    def handleOchreButton(self, control, value):
        self._state.handleOchreButton(control, value)
    
#    @abstractmethod
    def handleGrayButton(self, control, value):
        self._state.handleGrayButton(control, value)

#    @abstractmethod
    def handleOrangeButton(self, control, value):
        self._state.handleOrangeButton(control, value)