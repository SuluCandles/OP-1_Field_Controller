from op1field_constants import *
from op1field_midimode import MidiModeState
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

class MixerModeState(State):

    def handleFour(self, control, value):
        return

    def handleBlue(self, control, value):
        if value > self._blueVal:
            print("jogging mixer by: " + str(JOG_UP))
            self._blueVal = value
            transport.globalTransport(midi.FPT_MixerWindowJog, JOG_UP)
        elif value < self._blueVal:
            print("jogging mixer by: " + str(JOG_DOWN))
            self._blueVal = value
            transport.globalTransport(midi.FPT_MixerWindowJog, JOG_DOWN)
        elif value == self._blueVal:
            if value == MAX_KNOB:
                print("jogging mixer by: " + str(JOG_UP))
                transport.globalTransport(midi.FPT_MixerWindowJog, JOG_UP)
            elif value == MIN_KNOB:
                print("jogging mixer by: " + str(JOG_DOWN))
                transport.globalTransport(midi.FPT_MixerWindowJog, JOG_DOWN)
            else:
                print("this shouldn't happen")
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
        return

    def handleOchre(self, control, value):
        def doChange(change):
            print("jogging route by: " + str(change))
            mixer.selectTrack(self._selectedRouteTrack)
            self._selectedRouteTrack += change
            mixer.selectTrack(self._selectedRouteTrack)
            ui.miDisplayRect(self._selectedMixerTrack, self._selectedMixerTrack, 5000)
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
        print("not implemented" + str(value) + str(change))
        mixerNum = mixer.trackNumber()
        recEventID = mixer.getTrackPluginId(mixerNum, 0)
        res = 1/127
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Gain, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Gain+1, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Gain+2, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Freq, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Freq+1, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Freq+2, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Q, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Q+1, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Q+2, change, midi.REC_MIDIController, 0, 1, res)
        return

    def handleOrange(self, control, value):
        print("not implemented")
        mixerNum = mixer.trackNumber()
        recEventID = mixer.getTrackPluginId(mixerNum, 0)
        res = 1/127
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Gain, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Gain+1, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Gain+2, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Freq, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Freq+1, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Freq+2, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Q, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Q+1, change, midi.REC_MIDIController, 0, 1, res)
        mixer.automateEvent(recEventID + midi.REC_Mixer_EQ_Q+2, change, midi.REC_MIDIController, 0, 1, res)
        return

    def handleBlueButton(self, control, value):
        print("leaving mixer mode")
        self.controller.setState(MixerState())
        ui.setHintMsg("control mode - mixer")
        return

    def handleOchreButton(self, control, value):
        if self._selectedMixerTrack == self._selectedRouteTrack: return
        if mixer.getRouteSendActive(self._selectedMixerTrack, self._selectedRouteTrack):
            print("unrouting " + str(self._selectedMixerTrack) + " to " + str(self._selectedRouteTrack))
            mixer.setRouteTo(self._selectedMixerTrack, self._selectedRouteTrack, 0)
            mixer.setRouteTo(self._selectedMixerTrack, 0, 1)
        else:
            print("routing " + str(self._selectedMixerTrack) + " to " + str(self._selectedRouteTrack))
            mixer.setRouteTo(self._selectedMixerTrack, self._selectedRouteTrack, 1)
            mixer.setRouteTo(self._selectedMixerTrack, 0, 0)
        self._selectedRouteTrack = self._selectedMixerTrack
        return

    def handleGrayButton(self, control, value):
        print("linking channel: " + str(channels.selectedChannel()) + " to mixer: " + str(self._selectedMixerTrack))
        mixer.linkTrackToChannel(midi.ROUTE_ToThis)
        return

    def handleOrangeButton(self, control, value):
        print("swapping to midi mode")
        self.controller.setState(MidiModeState())
        ui.setHintMsg("midi mode")
        return