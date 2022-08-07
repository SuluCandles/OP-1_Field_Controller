from op1field_channel import ChannelState
from op1field_constants import *
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
from op1field_states import *

class SynthMode(State):
    def OnMidiIn(self, event) -> None:
        if event.status == CONTROL_STATUS and event.data1 == CONTROL_KEY:
            print("swapping to control mode")
            ui.setFocused(midi.widChannelRack)
            ui.showWindow(midi.widChannelRack)
            self.controller._focusedWindow = midi.widChannelRack
            event.handled = True
            ui.setHintMsg("control mode - channel rack")
            self.controller.setState(ChannelState())
            return

        if event.status in [midi.MIDI_START,midi.MIDI_STOP,midi.MIDI_CONTINUE,midi.MIDI_SYSTEMMESSAGE]:
            if transport.isPlaying():
                if event.status == midi.MIDI_START:
                    print("shouldn't ever happen")
                elif event.status == midi.MIDI_STOP:
                    print("pausing playback...")
                    _songPosition = transport.getSongPos(2)
                    transport.start()
                elif event.status == midi.MIDI_CONTINUE:
                    print("wrong pause button")
            else:
                if event.status == midi.MIDI_START:
                    print("starting playback...")
                    transport.start()
                elif event.status == midi.MIDI_STOP:
                    print("stopping playback...")
                    transport.stop()
                    _songPosition = transport.getSongPos(2)
                elif event.status == midi.MIDI_CONTINUE:
                    print("continuing playback...")
                    transport.start()
            event.handled = True
        else:
            device.processMIDICC(event)
        return