#name= OP-1 Field Objectified

from op1field_constants import *
from op1field_states import *
from op1field_channel import ChannelState
from op1field_synth import SynthMode
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
import op1field_states
import op1field_channel

#Globals to keep track of

#MODES
_isSYNTHMODE = False
_isMIXERMODE = False
_isMIDIMODE = False
_isPLAYLISTMODE = False
_isPLUGINPICKING = False
_midiMODE = OCHRE_CONTROL
_midiPage = oneButton
_isSELECTING = False
_hasSELECTED = False
_isREWINDING = False
_isBROWSING = False

#BLUE VALUES
_blueVal = 0
_blueMixVal = 0
_blueChanVal = 0
_bluePlayVal = 0

#OCHRE VALUES
_ochreVal = 0
_ochreMixVal = 0
_ochreChanVal = 0
_ochrePlayVal = 0

#GRAY VALUES
_grayVal = 0
_grayMixVal = 0
_grayChanVal = 0
_grayPlayVal = 0

#ORANGE VALUES
_orangeVal = 0
_orangeMixVal = 0
_orangeChanVal = 0
_orangePlayVal = 0

#SELECTED VALUES
_focusedWindow = midi.widPlaylist
_pianoFullScreen = False
_scroll_cycle = cycle(SCROLL_SPEED)
_scrollSpeed = next(_scroll_cycle)
_selectedMixerTrack = 0
_selectedInsert = 0
_selectedPlaylistTrack = MIN_PLAYLIST_TRACK
_selectedRouteTrack = 0
_selectedGrid = 0
_selectedPianoGrid = 0
_songLength = 0
_songPosition = 0
_activeSLOTS = []

_eqAmount = 0
_eqSpice = 0

#-----------------------------------------------------------------------------------------------
#-------------------------------------------MIDI-STUFF------------------------------------------
#-----------------------------------------------------------------------------------------------


op1field = Controller(SynthMode())

def OnInit():
    op1field.OnInit()
    return

def OnDeInit():
    op1field.OnDeInit()
    return

def OnMidiIn(event):
    print("----------------------------------")
    print("Status      : " + str(event.status))
    print("Data 1      : " + str(event.data1))
    print("Data 2      : " + str(event.data2))
    print("Port        : " + str(event.port))
    print("Note        : " + str(event.note))
    print("Velocity    : " + str(event.velocity))
    print("Pressure    : " + str(event.pressure))
    print("Prog Num    : " + str(event.progNum))
    print("Ctrl Num    : " + str(event.controlNum))
    print("Ctrl Val    : " + str(event.controlVal))
    print("Pitch Bend  : " + str(event.pitchBend))
    print("SysEx       : " + str(event.sysex))
    print("Increment   : " + str(event.isIncrement))
    print("Res         : " + str(event.res))
    print("In EV       : " + str(event.inEv))
    print("Out EV      : " + str(event.outEv))
    print("MIDI ID     : " + str(event.midiId))
    print("MIDI CHAN   : " + str(event.midiChan))
    print("MIDI CHAN EX: " + str(event.midiChanEx))
    print("----------------------------------")
    if event.status > 200 and not op1field._state == SynthMode():
        print("back to synth mode")
        op1field.setState(SynthMode())
        ui.setHintMsg("synth mode")
    if op1field._state == SynthMode():
        if event.status == CONTROL_STATUS and event.data1 == CONTROL_KEY:
            print("swapping to control mode")
            ui.setFocused(midi.widChannelRack)
            ui.showWindow(midi.widChannelRack)
            op1field._focusedWindow = midi.widChannelRack
            op1field.setState(ChannelState())
            event.handled = True
            ui.setHintMsg("control mode - channel rack")
            return
        else:
            op1field.OnMidiIn(event)
            return
    else:
        if event.status != CONTROL_STATUS:
            print("keyboard pressed")
            return
        else:
            op1field.OnMidiIn(event)
            return

def OnSysEx(event):
    print("uncaught sysex message. status: " + str(event.status))
    event.handled = True
    return


#-----------------------------------------------------------------------------------------------
#-------------------------------------------CONTROL-VS-SYNTH------------------------------------
#-----------------------------------------------------------------------------------------------

def OnSynthMidiIn(event):
    global _songPosition
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

def OnControlMidiIn(event):
    global _isMIDIMODE
    control = event.data1
    value = event.data2
    if event.status == CONTROL_STATUS:
        if control in opTRANSPORT:
            handleTransport(control, value)
        elif control in opCONTROL:
            handleControl(control, value)
        elif control in opEDIT:
            handleEdit(control, value)
        elif control in opMACROS:
            handleMacro(control, value)
        elif control in opFOUR:
            if _isMIDIMODE:
                print("midi page")
                handleMidiPage(control)
            else:
                handleFour(control, value)
        elif control in opSPECIAL:
            handleSpecial(control, value)
        elif control in opKNOBBUTTON:
            handleKnobButton(control, value)
        elif control in opKNOBS:
            if _isMIDIMODE:
                print("assignable midi")
                handleChannelMidi(event)
                return
            else:
                handleKnobs(control, value)
        else:
            print("unrecognized: " + str(control) + ", " + str(value))
    
    event.handled = True
    return

#-----------------------------------------------------------------------------------------------
#-------------------------------------------Main-Handling---------------------------------------
#-----------------------------------------------------------------------------------------------
def handleChannelMidi(event):
    global _midiMODE
    global _midiPage

    if _midiMODE == OCHRE_CONTROL:
        event = setOchreMidi(event)
        print("ochre control")
    elif _midiMODE == GRAY_CONTROL:
        event = setGrayMidi(event)
        print("gray control")
    elif _midiMODE == ORANGE_CONTROL:
        event = setOrangeMidi(event)
        print("orange control")
    else:
        print("unrecognized: " + str(event.data1) + ", " + str(event.data2))
    
    if _midiPage == oneButton:
        print("page 1")
    elif _midiPage == twoButton:
        print("page 2")
        event.data1 += 4
    elif _midiPage == threeButton:
        print("page 3")
        event.data1 += 8
    elif _midiPage == fourButton:
        print("page 4")
        event.data1 += 12
    else:
        print("unrecognized: " + str(event.data1) + ", " + str(event.data2))


    print("----------------------------------")
    print("Status      : " + str(event.status))
    print("Data 1      : " + str(event.data1))
    print("Data 2      : " + str(event.data2))
    print("Port        : " + str(event.port))
    print("Note        : " + str(event.note))
    print("Velocity    : " + str(event.velocity))
    print("Pressure    : " + str(event.pressure))
    print("Prog Num    : " + str(event.progNum))
    print("Ctrl Num    : " + str(event.controlNum))
    print("Ctrl Val    : " + str(event.controlVal))
    print("Pitch Bend  : " + str(event.pitchBend))
    print("SysEx       : " + str(event.sysex))
    print("Increment   : " + str(event.isIncrement))
    print("Res         : " + str(event.res))
    print("In EV       : " + str(event.inEv))
    print("Out EV      : " + str(event.outEv))
    print("MIDI ID     : " + str(event.midiId))
    print("MIDI CHAN   : " + str(event.midiChan))
    print("MIDI CHAN EX: " + str(event.midiChanEx))
    print("----------------------------------")

    return

def handleMidiPage(control):
    global _midiMODE
    global _midiPage

    if control == _midiPage:
        print("same page pressed")
        return
    elif control == oneButton:
        print("midi page 1")
        _midiPage = oneButton
        return
    elif control == twoButton:
        print("midi page 2")
        _midiPage = twoButton
        return
    elif control == threeButton:
        print("midi page 3")
        _midiPage = threeButton
        return
    elif control == fourButton:
        print("midi page 4")
        _midiPage = fourButton
        return
    else:
        print("unrecognized: " + str(control))

    return

def handleTransport(control, value):
    global _songPosition
    if value == 0:
        return
    
    print("transport")
    if transport.isPlaying():
        if control == playButton:
            print("wrong pause button")
            transport.start()
            _songPosition = transport.getSongPos(2)
        elif control == stopButton:
            print("pausing playback...")
            transport.start()
            _songPosition = transport.getSongPos(2)
    else:
        if control == playButton:
            print("starting playback...")
            transport.start()
        elif control == stopButton:
            print("returning to start")
            transport.stop()
            _songPosition = 0
        elif control == recButton:
            print("recording enabled")
            transport.record()
        else:
            print("unrecognized: " + str(control) + "," + str(value))
    return

def handleMacro(control, value):
    global _isREWINDING
    global _isBROWSING
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
        if _isBROWSING: 
            _isBROWSING = False
            ui.setFocused(midi.widChannelRack)
        else: 
            ui.setFocused(midi.widBrowser)
            _isBROWSING = True
    elif control == opSev:
        print("seven")
    elif control == opEit:
        print("eight")

    return

def handleFour(control, value):
    global _isMIDIMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _focusedWindow
    if value == 0:
        return
    
    if _focusedWindow == midi.widChannelRack or _focusedWindow == PIANO_ROLL:
        print("channel four button pressed")
        handleChannelFour(control, value)

    return

def handleEdit(control, value):
    global _focusedWindow
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
        if _focusedWindow == midi.widPlaylist or _focusedWindow == PIANO_ROLL:
            transport.globalTransport(midi.FPT_Menu, 2)
            return
        transport.globalTransport(midi.FPT_ItemMenu, 2)
    return

def handleSpecial(control, value):
    global _focusedWindow
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
        else:    
            print("opening piano roll")
            _focusedWindow = PIANO_ROLL
            transport.globalTransport(midi.FPT_F7, 1)
    elif control == micButton:
        print("panic!")
        transport.globalTransport(midi.FPT_F12, 1)
        transport.stop()
        resetModes()
    elif control == comButton:
        print("emulating enter")
        transport.globalTransport(midi.FPT_Enter, 1)
    elif control == helpButton:
        print("help button pressed")
        transport.globalTransport(midi.FPT_WaitForInput, 1)
    return

def handleControl(control, value):
    global _focusedWindow
    global _isPLUGINPICKING

    if value == 0:
        return

    if control == synthButton:
        if _isPLUGINPICKING:
            print("closing plugin picker")
            transport.globalTransport(midi.FPT_F8, 1)
            _isPLUGINPICKING = False
        else:
            print("opening plugin picker")
            transport.globalTransport(midi.FPT_F8, 1)   
            _isPLUGINPICKING = True
        return
    elif control == drumButton:
        print("focusing channel rack")
        _focusedWindow = midi.widChannelRack
        ui.setHintMsg("control mode - channel rack")
    elif control == tapeButton:
        print("focusing playlist")
        _focusedWindow = midi.widPlaylist
        ui.setHintMsg("control mode - playlist")
    elif control == mixerButton:
        print("focusing mixer")
        _focusedWindow = midi.widMixer
        ui.setHintMsg("control mode - mixer")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    if not ui.getVisible(_focusedWindow):
        ui.showWindow(_focusedWindow)
    ui.setFocused(_focusedWindow)
    resetModes()
    return

def handleKnobButton(control, value):
    if value == 0:
        return

    print("knob pressed")
    if control == blueButton:
        handleBlueButton(control, value)
    elif control == ochreButton:
        handleOchreButton(control, value)
    elif control == grayButton:
        handleGrayButton(control, value)
    elif control == orangeButton:
        handleOrangeButton(control, value)
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    return

def handleKnobs(control, value):
    global _isPLUGINPICKING
    print("knob tweaked")
    if _isPLUGINPICKING:
        handlePluginPicking(control, value)
        return
    if control == blueKnob:
        handleBlue(control, value)
    elif control == ochreKnob:
        handleOchre(control, value)
    elif control == grayKnob:
        handleGray(control, value)
    elif control == orangeKnob:
        handleOrange(control, value)
    else:
        print("unrecognized: " + str(control) + ", " + str(value))  
    return

#-----------------------------------------------------------------------------------------------
#-------------------------------------------KNOB-HANDLING---------------------------------------
#-----------------------------------------------------------------------------------------------

def handleBlue(control, value):
    global _blueVal
    global _blueMixVal
    global _blueChanVal
    global _bluePlayVal
    global _focusedWindow
    global _isMIDIMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack
    global _selectedInsert

    if ui.isInPopupMenu():
        print("in menu entering")
        handleBlueMenu(value)
        return

    if _isMIXERMODE:
        print("handling blue mixer mode knob")
        #handleInsertBlueKnob(control, value)
        #print("Setting Volume of Mixer Track: " + str(_selectedMixerTrack))
        #mixer.setTrackVolume(_selectedMixerTrack, value/127)
        handleMixerBlueKnob(control, value)
        return
    if _isPLAYLISTMODE:
        print("handling blue playlist mode knob")
        handlePlaylistModeBlueKnob(control, value)
        return
    if _focusedWindow == PIANO_ROLL:
        print("handling blue piano roll knob")
        handlePluginPicking(control, value)
        return
    elif _focusedWindow == midi.widPlaylist:
        print("handling blue playlist knob")
        handlePlaylistBlueKnob(control, value)
        return
    if value > _blueVal:
        print("jog blue by 1")
        _blueVal = value
        ui.jog(JOG_UP)
    elif value < _blueVal:
        print("jog blue by -1")
        _blueVal = value
        ui.jog(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            print("jog blue by 1")
            ui.jog(JOG_UP)
        elif value == MIN_KNOB:
            print("jog blue by -1")
            ui.jog(JOG_DOWN) 
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    if _focusedWindow == midi.widChannelRack:
        print("handling blue channel knob")
        handleChannelBlueKnob(control, value)
    if _focusedWindow == midi.widMixer:
        updateSelected(0)
    return

def handleOchre(control, value):
    global _ochreVal
    global _ochreMixVal
    global _ochreChanVal
    global _ochrePlayVal
    global _focusedWindow
    global _isMIDIMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack
    global _selectedPlaylistTrack

    if _isPLAYLISTMODE:
        print("handling ochre playlist mode knob")
        handlePlaylistModeOchreKnob(control, value)
        return
    if _focusedWindow == PIANO_ROLL:
        print("handling ochre piano roll knob")
        handlePianoOchreKnob(control, value)
        return
    if _focusedWindow == midi.widPlaylist:
        print("handling ochre playlist knob")
        handlePlaylistOchreKnob(control, value)
        return
    elif _focusedWindow == midi.widChannelRack:
        print("handling ochre channel knob")
        handleChannelOchreKnob(control, value)
        return
    if _focusedWindow == midi.widMixer:
        print("handling ochre mixer knob")
        handleMixerOchreKnob(control, value)
        return
    return

def handleGray(control, value):
    global _grayVal
    global _grayMixVal
    global _grayChanVal
    global _grayPlayVal
    global _focusedWindow
    global _isMIDIMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack

    if _focusedWindow == PIANO_ROLL:
        print("handling ochre piano roll knob")
        handlePianoGrayKnob(value)
        return

    if _focusedWindow == midi.widChannelRack:
        handleChannelGrayKnob(control, value)
        return
    if _focusedWindow == midi.widPlaylist:
        handlePlaylistGrayKnob(control, value)
        return
    if _focusedWindow == midi.widMixer:
        handleMixerGrayKnob(control, value)
        return
    
    return

def handleOrange(control, value):
    global _orangeVal
    global _orangeMixVal
    global _orangeChanVal
    global _orangePlayVal
    global _focusedWindow
    global _isMIDIMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack

    if _focusedWindow == midi.widChannelRack:
        handleChannelOrangeKnob(control, value)
        return
    if _focusedWindow == PIANO_ROLL:
        handlePianoOrangeKnob(control, value)
        return
    if _focusedWindow == midi.widPlaylist:
        handlePlaylistOrangeKnob(control, value)
        return
    if _focusedWindow == midi.widMixer:
        handleMixerOrangeKnob(control, value)
        return
    return

#-----------------------------------------------------------------------------------------------
#----------------------------------------KNOB-BUTTON-HANDLING-----------------------------------
#-----------------------------------------------------------------------------------------------

def handleBlueButton(control, value):
    global _focusedWindow
    global _isMIXERMODE
    global _isMIDIMODE
    global _isPLAYLISTMODE
    global _isPLUGINPICKING
    global _isBROWSING
    global _selectedRouteTrack
    global _selectedMixerTrack
    global _pianoFullScreen
    global _eqAmount
    global _eqSpice

    if ui.isInPopupMenu() or _isPLUGINPICKING or _isBROWSING:
        print("in menu entering")
        transport.globalTransport(midi.FPT_Enter, 1)
        if _isPLUGINPICKING or _isBROWSING: 
            ui.setFocused(_focusedWindow)
        _isPLUGINPICKING = False
        _isBROWSING = False
        ui.setHintMsg("menu navigation")
        return
    if _focusedWindow == PIANO_ROLL:
        print("in piano roll full screening")
        if _pianoFullScreen: _pianoFullScreen = False
        else: _pianoFullScreen = True
        transport.globalTransport(midi.FPT_Enter, 1)
        return

    if _focusedWindow == midi.widChannelRack:
        if _isMIDIMODE:
            print("midi mode disabled")
            channels.showCSForm(channels.selectedChannel(), 0)
            _isMIDIMODE = False
            ui.setHintMsg("control mode - channel rack")
        else:
            print("midi mode enabled")
            channels.showCSForm(channels.selectedChannel(), 1)
            ui.setHintMsg("midi mode")
            _isMIDIMODE = True
        _isPLAYLISTMODE = False
        _isMIXERMODE = False
        _isPLUGINPICKING = False
        _isBROWSING = False
    elif _focusedWindow == midi.widMixer:
        if _isMIXERMODE:
            print("mixer mode disabled")
            _isMIXERMODE = False
            ui.setFocused(midi.widMixer)
            ui.setHintMsg("control mode - mixer")
        else:
            print("mixer mode enabled")
            _selectedRouteTrack = _selectedMixerTrack
            buildSlotList(_selectedMixerTrack)
            _isMIXERMODE = True
            _eqSpice = 0
            _eqAmount = 0
            ui.setHintMsg("mixer mode")
        _isPLAYLISTMODE = False
        _isMIDIMODE = False
        _isPLUGINPICKING = False
        _isBROWSING = False
    elif _focusedWindow == midi.widPlaylist:
        if _isPLAYLISTMODE:
            print("playlist mode disabled")
            _isPLAYLISTMODE = False
            playlist.deselectAll()
            ui.setHintMsg("control mode - playlist")
        else:
            print("playlist mode enabled")
            _isPLAYLISTMODE = True
            ui.setHintMsg("playlist mode")
        _isMIXERMODE = False
        _isMIDIMODE = False
        _isPLUGINPICKING = False
        _isBROWSING = False
    return

def handleOchreButton(control, value):
    global _focusedWindow
    global _selectedMixerTrack
    global _selectedPlaylistTrack
    global _selectedMixerTrack
    global _selectedRouteTrack
    global _isPLUGINPICKING
    global _isBROWSING
    global _midiMODE
    global _isMIDIMODE
    global _isPLAYLISTMODE
    global _isMIXERMODE

    if ui.isInPopupMenu() or _isPLUGINPICKING or _isBROWSING:
        print("in menu escaping")
        transport.globalTransport(midi.FPT_Escape, 1)
        _isPLUGINPICKING = False
        _isBROWSING = False
        return

    if _isMIDIMODE:
        print("swapping to ochre control")
        _midiMODE = OCHRE_CONTROL
        return

    if _isPLAYLISTMODE:
        print("adding marker")
        arrangement.addAutoTimeMarker(arrangement.currentTime(False), patterns.getPatternName(patterns.patternNumber()))
        return

    if _isMIXERMODE:
        if _selectedMixerTrack == _selectedRouteTrack: return
        if mixer.getRouteSendActive(_selectedMixerTrack, _selectedRouteTrack):
            print("unrouting " + str(_selectedMixerTrack) + " to " + str(_selectedRouteTrack))
            mixer.setRouteTo(_selectedMixerTrack, _selectedRouteTrack, 0)
            mixer.setRouteTo(_selectedMixerTrack, 0, 1)
        else:
            print("routing " + str(_selectedMixerTrack) + " to " + str(_selectedRouteTrack))
            mixer.setRouteTo(_selectedMixerTrack, _selectedRouteTrack, 1)
            mixer.setRouteTo(_selectedMixerTrack, 0, 0)
        _selectedRouteTrack = _selectedMixerTrack
        return

    if _focusedWindow == midi.widChannelRack:
        print("muting channel: " + str(channels.selectedChannel()))
        channels.muteChannel(channels.selectedChannel())
    elif _focusedWindow == midi.widMixer:
        print("muting mixer track: " + str(_selectedMixerTrack))
        mixer.muteTrack(_selectedMixerTrack)
    elif _focusedWindow == midi.widPlaylist:
        print("muting playlist track: " + str(_selectedPlaylistTrack))
        playlist.muteTrack(_selectedPlaylistTrack)
    return

def handleGrayButton(control, value):
    global _focusedWindow
    global _selectedMixerTrack
    global _selectedPlaylistTrack
    global _isMIXERMODE
    global _midiMODE

    if _isMIDIMODE:
        print("swapping to gray control")
        _midiMODE = GRAY_CONTROL
        return

    if _isMIXERMODE:
        print("linking channel: " + str(channels.selectedChannel()) + " to mixer: " + str(_selectedMixerTrack))
        mixer.linkTrackToChannel(midi.ROUTE_ToThis)
        return
    if _focusedWindow == midi.widChannelRack:
        print("soloing channel: " + str(channels.selectedChannel()))
        channels.soloChannel(channels.selectedChannel())
    elif _focusedWindow == midi.widMixer:
        print("soloing mixer track: " + str(_selectedMixerTrack))
        mixer.soloTrack(_selectedMixerTrack)
    elif _focusedWindow == midi.widPlaylist:
        print("soloing playlist track: " + str(_selectedPlaylistTrack))
        playlist.soloTrack(_selectedPlaylistTrack)
    return

def handleOrangeButton(control, value):
    global _focusedWindow
    global _selectedMixerTrack
    global _selectedRouteTrack
    global _selectedPlaylistTrack
    global _isMIXERMODE
    global _isMIDIMODE
    global _isPLAYLISTMODE
    global _midiMODE
    global _isSELECTING
    global _hasSELECTED
    global _scrollSpeed
    global _scroll_cycle
    global _isPLUGINPICKING

    if _isMIDIMODE:
        print("swapping to orange control")
        _midiMODE = ORANGE_CONTROL
        return
    
    if _isPLAYLISTMODE:
        if _isSELECTING:
            _isSELECTING = False
            _hasSELECTED = True
            print("placing live loop end")
            arrangement.liveSelection(arrangement.currentTime(False), True)
        else:
            if _hasSELECTED:
                print("removing selected region")
                _hasSELECTED = False
                arrangement.liveSelection(arrangement.currentTime(False), False)
                arrangement.liveSelection(arrangement.currentTime(False), True)
                return
            _isSELECTING = True
            print("placing live loop start")
            arrangement.liveSelection(arrangement.currentTime(False), False)
        return

    if _isMIXERMODE:
        print("swapping to midi mode")
        if _isMIDIMODE:
            print("midi mode disabled")
            ui.escape()
            _isMIDIMODE = False
            ui.setHintMsg("control mode")
        else:
            print("midi mode enabled")
            ui.setHintMsg("midi mode")
            _isMIDIMODE = True
        _isPLAYLISTMODE = False
        _isMIXERMODE = False
        _isPLUGINPICKING = False
        return

    if _focusedWindow == midi.widChannelRack:
        print("adding pattern")
        handleChannelOrangeButton()
    elif _focusedWindow == midi.widMixer:
        print("arming track: " + str(_selectedMixerTrack) + " for recording")
        mixer.armTrack(_selectedMixerTrack)
    elif _focusedWindow == midi.widPlaylist:
        _scrollSpeed = next(_scroll_cycle)
        print("changing scroll speed to: " + str(_scrollSpeed))
    return

#-----------------------------------------------------------------------------------------------
#---------------------------------------PLAYLIST-KNOB-HANDLING----------------------------------
#-----------------------------------------------------------------------------------------------

def handlePlaylistBlueKnob(control, value):
    global _blueVal

    if value > _blueVal:
        _blueVal = value
        bluePlaylistKnob(JOG_UP)
    elif value < _blueVal:
        _blueVal = value
        bluePlaylistKnob(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            bluePlaylistKnob(JOG_UP)
        elif value == MIN_KNOB:
            bluePlaylistKnob(JOG_DOWN)
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))

    return

def handlePlaylistModeBlueKnob(control, value):
    global _blueVal

    if value > _blueVal:
        _blueVal = value
        bluePlaylistModeKnob(JOG_UP)
    elif value < _blueVal:
        _blueVal = value
        bluePlaylistModeKnob(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            bluePlaylistModeKnob(JOG_UP)
        elif value == MIN_KNOB:
            bluePlaylistModeKnob(JOG_DOWN)
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))

    return    

def handlePlaylistOchreKnob(control, value):
    global _ochreVal
    global _songLength

    _songLength = transport.getSongLength(-1)
    print("length: " + str(_songLength))
    if value > _ochreVal:
        _ochreVal = value
        ochrePlaylistKnob(JOG_UP)
    elif value < _ochreVal:
        _ochreVal = value
        ochrePlaylistKnob(JOG_DOWN)
    elif value == _ochreVal:
        if value == MAX_KNOB:
            ochrePlaylistKnob(JOG_UP)
        elif value == MIN_KNOB:
            ochrePlaylistKnob(JOG_DOWN)
        else:
            print("this shouldn't happen here")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    
    return

def handlePlaylistModeOchreKnob(control, value):
    global _ochreVal

    if value > _ochreVal:
        _ochreVal = value
        ochrePlaylistModeKnob(JOG_UP)
    elif value < _ochreVal:
        _ochreVal = value
        ochrePlaylistModeKnob(JOG_DOWN)
    elif value == _ochreVal:
        if value == MAX_KNOB:
            ochrePlaylistModeKnob(JOG_UP)
        elif value == MIN_KNOB:
            ochrePlaylistModeKnob(JOG_DOWN)
        else:
            print("this shouldn't happen here")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    
    return
    

def handlePlaylistGrayKnob(control, value):
    global _grayVal

    if value > _grayVal:
        _grayVal = value
        grayPlaylistKnob(JOG_UP)
    elif value < _grayVal:
        _grayVal = value
        grayPlaylistKnob(JOG_DOWN)
    elif value == _grayVal:
        if value == MAX_KNOB:
            grayPlaylistKnob(JOG_UP)
        elif value == MIN_KNOB:
            grayPlaylistKnob(JOG_DOWN)
        else:
            print("this shouldn't happen here")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    return

def handlePlaylistOrangeKnob(control, value):
    global _orangeVal

    if value > _orangeVal:
        _orangeVal = value
        orangePlaylistKnob(JOG_UP)
    elif value < _orangeVal:
        _orangeVal = value
        orangePlaylistKnob(JOG_DOWN)
    elif value == _orangeVal:
        if value == MAX_KNOB:
            orangePlaylistKnob(JOG_UP)
        elif value == MIN_KNOB:
            orangePlaylistKnob(JOG_DOWN)
        else:
            print("this shouldn't happen here")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    return

#-----------------------------------------------------------------------------------------------
#-----------------------------------------CHANNEL-KNOB-HANDLING---------------------------------
#-----------------------------------------------------------------------------------------------
def handleChannelBlueKnob(control, value):
    global _selectedGrid
    ui.crDisplayRect(_selectedGrid, channels.selectedChannel(), 4, 1, 5000)
    return  


def handleChannelOchreKnob(control, value):
    global _ochreVal
    global _selectedGrid
    if value > _ochreVal:
        print("jog ochre by 1")
        _ochreVal = value
        if _selectedGrid == MAX_GRID_LENGTH:
            _selectedGrid = 0
        else:
            _selectedGrid += 4
    elif value < _ochreVal:
        print("jog ochre by -1")
        _ochreVal = value
        if _selectedGrid == MIN_GRID_LENGTH:
            _selectedGrid = 0
        else:
            _selectedGrid -= 4
    elif value == _ochreVal:
        if value == MAX_KNOB:
            print("jog ochre by 1")
            if _selectedGrid == MAX_GRID_LENGTH:
                _selectedGrid = 0
            else:
                _selectedGrid += 4
        elif value == MIN_KNOB:
            print("jog ochre by -1")
            if _selectedGrid == MIN_GRID_LENGTH:
                _selectedGrid = 0
            else:
                _selectedGrid -= 4
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    
    ui.crDisplayRect(_selectedGrid, channels.selectedChannel(), 4, 1, 5000)
    return

def handleChannelGrayKnob(control, value):
    global _grayVal
    _grayVal = value

    print("setting channel volume to: " + str(value))
    channels.setChannelVolume(channels.selectedChannel(), value/MAX_KNOB)

    return

def handleChannelOrangeKnob(control, value):
    global _orangeVal
    
    if value > _orangeVal:
        _orangeVal = value
        orangeChannelKnob(JOG_UP)
    elif value < _orangeVal:
        _orangeVal = value
        orangeChannelKnob(JOG_DOWN)
    elif value == _orangeVal:
        if value == MAX_KNOB:
            orangeChannelKnob(JOG_UP)
        elif value == MIN_KNOB:
            orangeChannelKnob(JOG_DOWN)
        else:
            print("this shouldn't happen here")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))

    #_orangeVal = value

    #print("Setting channel pan to: " + str(value))
    #channels.setChannelPan(channels.selectedChannel(), value/MAX_KNOB)
    return

#-----------------------------------------------------------------------------------------------
#---------------------------------------CHANNEL-BUTTON-HANDLING---------------------------------
#-----------------------------------------------------------------------------------------------    
def handleChannelOrangeButton():
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


def handleChannelFour(control, value):
    global _selectedGrid
    global _selectedPianoGrid
    global _pianoFullScreen

    selected = _selectedGrid
    mult = 1

    if _pianoFullScreen: 
        selected = _selectedPianoGrid
        mult = 4

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
#-----------------------------------------------------------------------------------------------
#---------------------------------------MIXER-MODE-KNOB-HANDLING--------------------------------
#-----------------------------------------------------------------------------------------------    
def handleMixerBlueKnob(control, value):
    global _blueVal
    global _selectedInsert

    if value > _blueVal:
        print("jog blue by 1")
        _blueVal = value
        blueMixerKnob(JOG_UP)
    elif value < _blueVal:
        print("jog blue by -1")
        _blueVal = value
        blueMixerKnob(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            print("jog blue by 1")
            blueMixerKnob(JOG_UP)
        elif value == MIN_KNOB:
            print("jog blue by -1")
            blueMixerKnob(JOG_DOWN) 
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    return

def handleMixerOchreKnob(control, value):
    global _ochreVal

    if value > _ochreVal:
        _ochreVal = value
        ochreMixerKnob(JOG_UP, value)
    elif value < _ochreVal:
        _ochreVal = value
        ochreMixerKnob(JOG_DOWN, value)
    elif value == _ochreVal:
        if value == MAX_KNOB:
            ochreMixerKnob(JOG_UP, value)
        elif value == MIN_KNOB:
            ochreMixerKnob(JOG_DOWN, value)
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    
    return

def handleMixerGrayKnob(control, value):
    global _grayVal
    global _eqAmount

    if value > _grayVal:
        _grayVal = value
        _eqAmount += 1
        grayMixerKnob(JOG_UP, value)
    elif value < _grayVal:
        _grayVal = value
        _eqAmount -= 1
        grayMixerKnob(JOG_DOWN, value)
    elif value == _grayVal:
        if value == MAX_KNOB:
            _eqAmount += 1
            grayMixerKnob(JOG_UP, value)
        elif value == MIN_KNOB:
            _eqAmount -= 1
            grayMixerKnob(JOG_DOWN, value)
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    
    return


def handleMixerOrangeKnob(control, value):
    global _orangeVal
    global _eqSpice

    if value > _orangeVal:
        _orangeVal = value
        _eqSpice += 1
        orangeMixerKnob(JOG_UP, value)
    elif value < _orangeVal:
        _orangeVal = value
        _eqSpice -= 1
        orangeMixerKnob(JOG_DOWN, value)
    elif value == _orangeVal:
        if value == MAX_KNOB:
            _eqSpice += 1
            orangeMixerKnob(JOG_UP, value)
        elif value == MIN_KNOB:
            _eqSpice -= 1
            orangeMixerKnob(JOG_DOWN, value)
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    
    return


#-----------------------------------------------------------------------------------------------
#--------------------------------------PLAYLIST-KNOB---------------------------------------
#-----------------------------------------------------------------------------------------------

def bluePlaylistKnob(change):    
    global _selectedPlaylistTrack

    print("jog playlist track by: " + str(change))
    prev = _selectedPlaylistTrack
    playlist.deselectAll()
    updateSelected(change)
    playlist.selectTrack(_selectedPlaylistTrack)
    if prev == MIN_PLAYLIST_TRACK and _selectedPlaylistTrack == MAX_PLAYLIST_TRACK:
        for i in range(1,MAX_PLAYLIST_TRACK-4):
            transport.globalTransport(midi.FPT_Down, 1)
    elif prev == MAX_PLAYLIST_TRACK and _selectedPlaylistTrack == MIN_PLAYLIST_TRACK:
        for i in range(1,MAX_PLAYLIST_TRACK-4):
            transport.globalTransport(midi.FPT_Up, 1)
    elif _selectedPlaylistTrack > 5 and change == JOG_UP:
            transport.globalTransport(midi.FPT_Down, 1)
    elif _selectedPlaylistTrack > 4 and change == JOG_DOWN:
            transport.globalTransport(midi.FPT_Up, 1)

    return

def bluePlaylistModeKnob(change):
    print("jog playhead by: " + str(change))
    ui.jog(change)
    return

def ochrePlaylistKnob(change):
    global _songLength
    global _songPosition
    global _scrollSpeed
    print("jog playlist by: " + str(change))
    bar = transport.getSongPos(3) + change - 1
    pos = transport.getSongPos(2) + (change * (general.getRecPPB() * _scrollSpeed))
    ui.scrollWindow(midi.widPlaylist, bar, 1)
    print(bar)
    transport.setSongPos(pos, 2)
    _songPosition = pos
    return

def ochrePlaylistModeKnob(change):
    print("jumping marker by: " + str(change))
    arrangement.jumpToMarker(change, False)
    return

def grayPlaylistKnob(change):
    print("not implemented")
    global _selectedPlaylistTrack

    print("jog playlist track by: " + str(change))
    prev = _selectedPlaylistTrack
    #playlist.deselectAll()
    updateSelected(change)
    if not playlist.isTrackSelected(_selectedPlaylistTrack): playlist.selectTrack(_selectedPlaylistTrack)
    else: playlist.selectTrack(_selectedPlaylistTrack)
    if prev == MIN_PLAYLIST_TRACK and _selectedPlaylistTrack == MAX_PLAYLIST_TRACK:
        for i in range(1,MAX_PLAYLIST_TRACK-4):
            transport.globalTransport(midi.FPT_Down, 1)
    elif prev == MAX_PLAYLIST_TRACK and _selectedPlaylistTrack == MIN_PLAYLIST_TRACK:
        for i in range(1,MAX_PLAYLIST_TRACK-4):
            transport.globalTransport(midi.FPT_Up, 1)
    elif _selectedPlaylistTrack > 5 and change == JOG_UP:
            transport.globalTransport(midi.FPT_Down, 1)
    elif _selectedPlaylistTrack > 4 and change == JOG_DOWN:
            transport.globalTransport(midi.FPT_Up, 1)
    return

def orangePlaylistKnob(change):
    print("changing playlist zoom by: " + str(change))
    transport.globalTransport(midi.FPT_HZoomJog, change)
    return


#-----------------------------------------------------------------------------------------------
#-----------------------------------------MIXER-MODE-KNOB---------------------------------------
#-----------------------------------------------------------------------------------------------

def blueMixerKnob(change):
    global _isMIXERMODE
    global _activeSLOTS
    
    if _isMIXERMODE:
        #for slot in _activeSLOTS:
        transport.globalTransport(midi.FPT_MixerWindowJog, change)
    else:
        print("jogging mixer by: " + str(change))
        ui.jog(change)
    return

def ochreMixerKnob(change, value):
    global _selectedRouteTrack
    global _selectedMixerTrack
    if _isMIXERMODE: 
        print("jog mixer track by: " + str(change))
        updateSelectedRoute(change)
        mixer.selectTrack(_selectedRouteTrack)
        ui.miDisplayRect(_selectedMixerTrack, _selectedMixerTrack, 5000)
        return
    else:
        print("setting track volume to: " + str(value))
        mixer.setTrackVolume(_selectedMixerTrack, value/127, 1)
        return
    return   

def grayMixerKnob(change, value):
    global _eqAmount
    global _isMIXERMODE
    if _isMIXERMODE: 
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
    else:
        print("setting track pan to: " + str(value))
        mixer.setTrackPan(_selectedMixerTrack, normalizePolar(value), 1)
        return
    return

def orangeMixerKnob(change, value):
    global _eqSpice
    global _isMIXERMODE

    if _isMIXERMODE: 
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
    else:
        print("seperating stereo by: " + str(value))
        mixer.setTrackStereoSep(_selectedMixerTrack, normalizePolar(value), 1)
        return


def orangeChannelKnob(change):
    print("changing pattern by: " + str(change))
    transport.globalTransport(midi.FPT_PatternJog, change)

#-----------------------------------------------------------------------------------------------
#-----------------------------------------MENU-KNOB-HANDLE--------------------------------------
#-----------------------------------------------------------------------------------------------

def handleBlueMenu(value):
    global _blueVal
    global _selectedInsert

    if value > _blueVal:
        print("jog blue by 1")
        _blueVal = value
        ui.jog(JOG_UP)
    elif value < _blueVal:
        print("jog blue by -1")
        _blueVal = value
        ui.jog(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            print("jog blue by 1")
            ui.jog(JOG_UP)
        elif value == MIN_KNOB:
            print("jog blue by -1")
            ui.jog(JOG_DOWN) 
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(value))
    return

def handlePluginPicking(control, value):

    if control == blueKnob:
        bluePluginPicking(value)
    elif control == ochreKnob:
        ochrePluginPicking(value)
    
    return

def bluePluginPicking(value):
    global _blueVal

    if value > _blueVal:
        print("jog blue by 1")
        _blueVal = value
        ui.down(1)
    elif value < _blueVal:
        print("jog blue by -1")
        _blueVal = value
        ui.up(1)
    elif value == _blueVal:
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

def ochrePluginPicking(value):
    global _ochreVal

    if value > _ochreVal:
        print("jog ochre by 1")
        _ochreVal = value
        ui.right(1)
    elif value < _ochreVal:
        print("jog ochre by -1")
        _ochreVal = value
        ui.left(1)
    elif value == _ochreVal:
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

#-----------------------------------------------------------------------------------------------
#------------------------------------------HANDLE-PIANO-ROLL------------------------------------
#-----------------------------------------------------------------------------------------------    
def handlePianoOchreKnob(control, value):
    global _selectedGrid
    global _ochreVal
    global _pianoFullScreen
    global _selectedPianoGrid

    max_length = patterns.getPatternLength(patterns.patternNumber())

    if value > _ochreVal:
        print("jog ochre by 1")
        _ochreVal = value
        if _pianoFullScreen: transport.globalTransport(midi.FPT_Jog, 1)
        if _selectedGrid == MAX_GRID_LENGTH:
            _selectedGrid = 0
        else:
            _selectedGrid += 4 
    elif value < _ochreVal:
        print("jog ochre by -1")
        _ochreVal = value
        if _pianoFullScreen: transport.globalTransport(midi.FPT_Jog, -1)
        if _selectedGrid != MIN_GRID_LENGTH: _selectedGrid -= 4
    elif value == _ochreVal:
        if value == MAX_KNOB:
            print("jog ochre by 1")
            if _pianoFullScreen: transport.globalTransport(midi.FPT_Jog, 1)
            if _selectedGrid == MAX_GRID_LENGTH:
                _selectedGrid = 0
            else:
                 _selectedGrid += 4
        elif value == MIN_KNOB:
            print("jog ochre by -1")
            if _pianoFullScreen: transport.globalTransport(midi.FPT_Jog, -1)
            if _selectedGrid != MIN_GRID_LENGTH: _selectedGrid -= 4
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))

    _selectedPianoGrid = (transport.getSongPos(3) - 1)  * 16
    ui.crDisplayRect(_selectedGrid, channels.selectedChannel(), 4, 1, 5000) 
    return

def handlePianoGrayKnob(value):
    global _grayVal
    global _pianoFullScreen
    
    if value > _grayVal:
        print("jog gray by 1")
        _grayVal = value
        if not _pianoFullScreen: return #transport.globalTransport(midi.FPT_Jog, 1)  
        else: transport.globalTransport(midi.FPT_MoveJog, 1)
    elif value < _grayVal:
        print("jog gray by -1")
        _grayVal = value
        if not _pianoFullScreen: return #transport.globalTransport(midi.FPT_Jog, -1)  
        else: transport.globalTransport(midi.FPT_MoveJog, -1)
    elif value == _grayVal:
        if value == MAX_KNOB:
            print("jog gray by 1")
            if not _pianoFullScreen: return #transport.globalTransport(midi.FPT_Jog, 1)  
            else: transport.globalTransport(midi.FPT_MoveJog, 1)
        elif value == MIN_KNOB:
            if not _pianoFullScreen: return #transport.globalTransport(midi.FPT_Jog, -1)  
            else: transport.globalTransport(midi.FPT_MoveJog, -1)
        else:
            print("this shouldn't happen")
    else:
        print("unrecognized: " + str(value))
    
    return

def handlePianoOrangeKnob(control, value):
    global _orangeVal

    if value > _orangeVal:
        _orangeVal = value
        orangePianoKnob(JOG_UP)
    elif value < _orangeVal:
        _orangeVal = value
        orangePianoKnob(JOG_DOWN)
    elif value == _orangeVal:
        if value == MAX_KNOB:
            orangePianoKnob(JOG_UP)
        elif value == MIN_KNOB:
            orangePianoKnob(JOG_DOWN)
        else:
            print("this shouldn't happen here")
    else:
        print("unrecognized: " + str(control) + ", " + str(value))
    return

def orangePianoKnob(change):
    print("zooming piano roll")
    transport.globalTransport(midi.FPT_HZoomJog, change)
    return
#-----------------------------------------------------------------------------------------------
#------------------------------------------UPDATES-UTILS----------------------------------------
#-----------------------------------------------------------------------------------------------

def updateSelected(change):
    global _selectedInsert
    global _selectedMixerTrack
    global _selectedPlaylistTrack

    _selectedMixerTrack = mixer.trackNumber()
    if _selectedPlaylistTrack == MAX_PLAYLIST_TRACK and change > 0:
        _selectedPlaylistTrack = MIN_PLAYLIST_TRACK
    elif _selectedPlaylistTrack == MIN_PLAYLIST_TRACK and change < 0:
        _selectedPlaylistTrack = MAX_PLAYLIST_TRACK
    else:
        _selectedPlaylistTrack += change
    return

def updateSelectedRoute(change):
    global _selectedRouteTrack

    mixer.selectTrack(_selectedRouteTrack)
    _selectedRouteTrack += change
 
    return

def resetModes():
    global _isMIXERMODE
    global _isMIDIMODE
    global _isPLAYLISTMODE
    global _isPLUGINPICKING
    global _isBROWSING
    global _focusedWindow
    global _activeSLOTS

    print("resetting to control mode")
    
    if _focusedWindow == PIANO_ROLL:
        transport.globalTransport(midi.FPT_F7, 1)

    _isPLAYLISTMODE = False
    _isMIDIMODE = False
    _isMIXERMODE = False
    _isPLUGINPICKING = False
    _isBROWSING = False
    _activeSLOTS = []

    return

def setOchreMidi(event):
    event.midiChan = OCHRE_CHANNEL
    event.status = 180
    if event.data1 == blueKnob:
        event.data1 = OCHRE_CHANNEL+10
    elif event.data1 == ochreKnob:
        event.data1 = OCHRE_CHANNEL+11
    elif event.data1 == grayKnob:
        event.data1 = OCHRE_CHANNEL+12
    elif event.data1 == orangeKnob:
        event.data1 = OCHRE_CHANNEL+13
    else:
        print("unrecognized: " + str(event.data1) + ", " + str(event.data2))

    return event

def setGrayMidi(event):
    event.midiChan = GRAY_CHANNEL
    event.status = 180
    if event.data1 == blueKnob:
        event.data1 = GRAY_CHANNEL+10
    elif event.data1 == ochreKnob:
        event.data1 = GRAY_CHANNEL+11
    elif event.data1 == grayKnob:
        event.data1 = GRAY_CHANNEL+12
    elif event.data1 == orangeKnob:
        event.data1 = GRAY_CHANNEL+13
    else:
        print("unrecognized: " + str(event.data1) + ", " + str(event.data2))

    return event

def setOrangeMidi(event):
    event.midiChan = ORANGE_CHANNEL
    event.status = 180
    if event.data1 == blueKnob:
        event.data1 = ORANGE_CHANNEL+10
    elif event.data1 == ochreKnob:
        event.data1 = ORANGE_CHANNEL+11
    elif event.data1 == grayKnob:
        event.data1 = ORANGE_CHANNEL+12
    elif event.data1 == orangeKnob:
        event.data1 = ORANGE_CHANNEL+13
    else:
        print("unrecognized: " + str(event.data1) + ", " + str(event.data2))

    return event

def buildSlotList(index):
    global _activeSLOTS
    _activeSLOTS = []
    for i in range(0,10):
        if plugins.isValid(index, i):
            _activeSLOTS.append(i)
    print("building slot index: " + str(_activeSLOTS))

    return