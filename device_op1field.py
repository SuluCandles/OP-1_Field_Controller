#name= OP-1 Field

from op1field_constants import *
import midi
import transport
import device
import ui
import channels
import patterns
import mixer
import playlist
import plugins
import general

#Globals to keep track of
_isSYNTHMODE = False
_isMIXERMODE = False
_isCHANNELMODE = False
_isPLAYLISTMODE = False
_isINSERTMODE = False
_blueVal = 0
_blueMixVal = 0
_blueChanVal = 0
_bluePlayVal = 0
_ochreVal = 0
_ochreMixVal = 0
_ochreChanVal = 0
_ochrePlayVal = 0
_grayVal = 0
_grayMixVal = 0
_grayChanVal = 0
_grayPlayVal = 0
_orangeVal = 0
_orangeMixVal = 0
_orangeChanVal = 0
_orangePlayVal = 0
_focusedWindow = midi.widPlaylist
_selectedMixerTrack = 0
_selectedInsert = 0
_selectedPlaylistTrack = 0
_selectedRouteTrack = 0

#-----------------------------------------------------------------------------------------------
#-------------------------------------------MIDI-STUFF------------------------------------------
#-----------------------------------------------------------------------------------------------

def OnInit():
    global _isSYNTHMODE
    print("Please be in Synth Mode!")
    _isSYNTHMODE = True
    return

def OnDeInit():
    print("goodbye :)")
    return

def OnMidiIn(event):
    global _isSYNTHMODE
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
    isKeyboard = True
    
    if _isSYNTHMODE:
        if event.status == CONTROL_STATUS and event.data1 == CONTROL_KEY:
            _isSYNTHMODE = False
            print("Swapping to Control Mode!")
            event.handled = True
            return
        else:
            OnSynthMidiIn(event)
            return
    else:
        for list in AVAILABLE_BUTTONS:
            if event.data1 in list:
                isKeyboard = False
                break
        if isKeyboard and event.status != CONTROL_STATUS:
            print("Keyboard Pressed")
            return
        else:
            OnControlMidiIn(event)

def OnSysEx(event):
    print("Uncaught SysEx Message! Status: " + str(event.status))
    print("Handling anyways: what did you do lol? " + str(event.data1) + ", " + str(event.data2))
    event.handled = True
    return


#-----------------------------------------------------------------------------------------------
#-------------------------------------------CONTROL-VS-SYNTH------------------------------------
#-----------------------------------------------------------------------------------------------

def OnSynthMidiIn(event):
    if event.status in [midi.MIDI_START,midi.MIDI_STOP,midi.MIDI_CONTINUE,midi.MIDI_SYSTEMMESSAGE]:
        if transport.isPlaying():
            if event.status == midi.MIDI_START:
                print("Shouldn't ever happen")
            elif event.status == midi.MIDI_STOP:
                print("Pausing playback...")
                transport.start()
            elif event.status == midi.MIDI_CONTINUE:
                print("Wrong Pause Button")
        else:
            if event.status == midi.MIDI_START:
                print("Starting playback...")
                transport.start()
            elif event.status == midi.MIDI_STOP:
                print("Stopping playback...")
                transport.stop()
            elif event.status == midi.MIDI_CONTINUE:
                print("Continuing playback...")
                transport.start()
        event.handled = True
    else:
        device.processMIDICC(event)
    return

def OnControlMidiIn(event):
    global _isCHANNELMODE
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
            handleFour(control, value)
        elif control in opSPECIAL:
            handleSpecial(control, value)
        elif control in opKNOBBUTTON:
            handleKnobButton(control, value)
        elif control in opKNOBS:
            if _isCHANNELMODE:
                print("Assignable MIDI")
                device.processMIDICC(event)
            else:
                handleKnobs(control, value)
        else:
            print("Unrecognized: " + str(control) + ", " + str(value))

    return

#-----------------------------------------------------------------------------------------------
#-------------------------------------------Main-Handling---------------------------------------
#-----------------------------------------------------------------------------------------------

def handleTransport(control, value):
    if value == 0:
        return
    
    print("Transport")
    if transport.isPlaying():
        if control == playButton:
            print("Wrong Pause Button")
            transport.start()
        elif control == stopButton:
            print("Pausing playback...")
            transport.start()
    else:
        if control == playButton:
            print("Starting playback...")
            transport.start()
        elif control == stopButton:
            print("Returning to start")
            transport.stop()
        elif control == recButton:
            print("Recording Enabled")
            transport.record()
        else:
            print("Unrecognized: " + str(control) + "," + str(value))
    return

def handleMacro(control, value):
    print("Macro button pressed")
    return

def handleFour(control, value):
    print("Four button pressed")
    return

def handleEdit(control, value):
    global _focusedWindow
    if value == 0:
        return
    
    if control == liftButton:
        print("Cutting...")
        transport.globalTransport(midi.FPT_Cut, 1)
    elif control == dropButton:
        print("Pasting...")
        transport.globalTransport(midi.FPT_Paste, 1)
    elif control == cutButton:
        print("tool")
        if _focusedWindow == midi.widPlaylist:
            transport.globalTransport(midi.FPT_Menu, 2)
            return
        transport.globalTransport(midi.FPT_ItemMenu, 2)
    return

def handleSpecial(control, value):
    if value == 0:
        return
    
    if control == tempoButton:
        print("Metronome pressed")
        transport.globalTransport(midi.FPT_Metronome, 1)
    elif control == seqButton:
        print("Opening Piano Roll")
        transport.globalTransport(midi.FPT_F7, 1)
    elif control == micButton:
        print("Emulating Escape")
        transport.globalTransport(midi.FPT_Escape, 1)
    elif control == comButton:
        print("Emulating Enter")
        transport.globalTransport(midi.FPT_Enter, 1)
    return

def handleControl(control, value):
    global _focusedWindow

    if value == 0:
        return
    print("Control button pressed")    
    if control == synthButton:
        print("Opening Plugin Picker")
        transport.globalTransport(midi.FPT_F8, 1)
        return
    elif control == drumButton:
        print("Focusing Channel Rack")
        _focusedWindow = midi.widChannelRack
    elif control == tapeButton:
        print("Focusing Playlist")
        _focusedWindow = midi.widPlaylist
    elif control == mixerButton:
        print("Focusing Mixer")
        _focusedWindow = midi.widMixer
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))
    if not ui.getVisible(_focusedWindow):
        ui.showWindow(_focusedWindow)
    ui.setFocused(_focusedWindow)
    resetModes()
    return

def handleKnobButton(control, value):
    if value == 0:
        return
    print("Knob pressed")
    if control == blueButton:
        handleBlueButton(control, value)
    elif control == ochreButton:
        handleOchreButton(control, value)
    elif control == grayButton:
        handleGrayButton(control, value)
    elif control == orangeButton:
        handleOrangeButton(control, value)
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))
    return

def handleKnobs(control, value):
    print("Knob tweaked")
    if control == blueKnob:
        handleBlue(control, value)
    elif control == ochreKnob:
        handleOchre(control, value)
    elif control == grayKnob:
        handleGray(control, value)
    elif control == orangeKnob:
        handleOrange(control, value)
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))
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
    global _isCHANNELMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _isINSERTMODE
    global _selectedMixerTrack
    global _selectedInsert

    if _isMIXERMODE:
        if _isINSERTMODE:
            print("Handling Blue Insert Knob")
            handleInsertBlueKnob(control, value)
            return
        else:
            print("Setting Volume of Mixer Track: " + str(_selectedMixerTrack))
            mixer.setTrackVolume(_selectedMixerTrack, value/127)
            return
    if _focusedWindow == midi.widPlaylist:
        print("Handling Blue Playlist Knob")
        handlePlaylistBlueKnob(control, value)
        return
    if value > _blueVal:
        print("Jog Blue by 1")
        _blueVal = value
        ui.jog(JOG_UP)
    elif value < _blueVal:
        print("Jog Blue by -1")
        _blueVal = value
        ui.jog(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            print("Jog Blue by 1")
            ui.jog(JOG_UP)
        elif value == MIN_KNOB:
            print("Jog Blue by -1")
            ui.jog(JOG_DOWN) 
        else:
            print("This shouldn't happen")
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))
    if _focusedWindow == midi.widMixer:
        updateSelected(0)
    return

def handleOchre(control, value):
    global _ochreVal
    global _ochreMixVal
    global _ochreChanVal
    global _ochrePlayVal
    global _focusedWindow
    global _isCHANNELMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack
    global _selectedPlaylistTrack

    if _isMIXERMODE:
        mixer.setTrackPan(_selectedMixerTrack, value/127)
        return
    if _focusedWindow == midi.widPlaylist:
        handlePlaylistOchreKnob(control, value)
        return
    elif _focusedWindow == midi.widChannelRack:
        if value > _ochreVal:
            print("Jog ochre by 1")
            _ochreVal = value
            ui.jog2(JOG_UP)
        elif value < _ochreVal:
            print("Jog ochre by -1")
            _ochreVal = value
            ui.jog2(JOG_DOWN)
        elif value == _ochreVal:
            if value == MAX_KNOB:
                print("Jog ochre by 1")
                ui.jog2(JOG_UP)
            elif value == MIN_KNOB:
                print("Jog ochre by -1")
                ui.jog2(JOG_DOWN) 
            else:
                print("This shouldn't happen")
        else:
            print("Unrecognized: " + str(control) + ", " + str(value))
    if _focusedWindow == midi.widMixer:
        updateSelected(0)
    return

def handleGray(control, value):
    global _grayVal
    global _grayMixVal
    global _grayChanVal
    global _grayPlayVal
    global _focusedWindow
    global _isCHANNELMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack

    if _isMIXERMODE:
        mixer.setTrackStereoSep(_selectedMixerTrack, value/127)
        return
    return

def handleOrange(control, value):
    global _orangeVal
    global _orangeMixVal
    global _orangeChanVal
    global _orangePlayVal
    global _focusedWindow
    global _isCHANNELMODE
    global _isMIXERMODE
    global _isPLAYLISTMODE
    global _selectedMixerTrack

    if _isMIXERMODE:
        if value > _orangeVal:
            _orangeVal = value
            orangeMixerKnob(JOG_UP)
        elif value < _orangeVal:
            _orangeVal = value
            orangeMixerKnob(JOG_DOWN)
        elif value == _orangeVal:
            if value == MAX_KNOB:
                orangeMixerKnob(JOG_UP)
            elif value == MIN_KNOB:
                orangeMixerKnob(JOG_DOWN)
            else:
                print("This shouldn't happen")
        else:
            print("Unrecognized: " + str(control) + ", " + str(value))
    
    return

#-----------------------------------------------------------------------------------------------
#----------------------------------------KNOB-BUTTON-HANDLING-----------------------------------
#-----------------------------------------------------------------------------------------------

def handleBlueButton(control, value):
    global _focusedWindow
    global _isMIXERMODE
    global _isCHANNELMODE
    global _isPLAYLISTMODE
    global _selectedRouteTrack
    global _selectedMixerTrack

    if ui.isInPopupMenu():
        print("In menu entering")
        transport.globalTransport(midi.FPT_Enter, 1)
        return

    if _focusedWindow == midi.widChannelRack:
        if _isCHANNELMODE:
            print("Channel Mode Disabled")
            channels.showCSForm(channels.selectedChannel(), 0)
            _isCHANNELMODE = False
        else:
            print("Channel Mode Enabled")
            channels.showCSForm(channels.selectedChannel(), 1)
            _isCHANNELMODE = True
        _isPLAYLISTMODE = False
        _isMIXERMODE = False
    elif _focusedWindow == midi.widMixer:
        if _isMIXERMODE:
            print("Mixer Mode Disabled")
            _isMIXERMODE = False
        else:
            print("Mixer Mode Enabled")
            _selectedRouteTrack = _selectedMixerTrack
            _isMIXERMODE = True
        _isPLAYLISTMODE = False
        _isCHANNELMODE = False
    elif _focusedWindow == midi.widPlaylist:
        if _isPLAYLISTMODE:
            print("Playlist Mode Disabled")
            _isPLAYLISTMODE = False
        else:
            print("Playlist Mode Enabled")
            _isPLAYLISTMODE = True
        _isMIXERMODE = False
        _isCHANNELMODE = False
    return

def handleOchreButton(control, value):
    global _focusedWindow
    global _selectedMixerTrack
    global _selectedPlaylistTrack
    global _isINSERTMODE
    global _selectedMixerTrack

    if ui.isInPopupMenu():
        print("In menu escaping")
        transport.globalTransport(midi.FPT_Escape, 1)
        return

    if _isMIXERMODE:
        print("Swapping to Insert Mode!")
        _isINSERTMODE = True
        if plugins.isValid(_selectedMixerTrack, _selectedInsert):
            print("Valid")
        return


    if _focusedWindow == midi.widChannelRack:
        print("Muting Channel: " + str(channels.selectedChannel()))
        channels.muteChannel(channels.selectedChannel())
    elif _focusedWindow == midi.widMixer:
        print("Muting Mixer Track: " + str(_selectedMixerTrack))
        mixer.muteTrack(_selectedMixerTrack)
    elif _focusedWindow == midi.widPlaylist:
        print("Muting Playlist Track: " + str(_selectedPlaylistTrack))
        playlist.muteTrack(_selectedPlaylistTrack)
    return

def handleGrayButton(control, value):
    global _focusedWindow
    global _selectedMixerTrack
    global _selectedPlaylistTrack
    global _isMIXERMODE

    if _isMIXERMODE:
        print("Linking Channel: " + str(channels.selectedChannel()) + " to Mixer: " + str(_selectedMixerTrack))
        mixer.linkTrackToChannel(midi.ROUTE_ToThis)
        return
    if _focusedWindow == midi.widChannelRack:
        print("Soloing Channel: " + str(channels.selectedChannel()))
        channels.soloChannel(channels.selectedChannel())
    elif _focusedWindow == midi.widMixer:
        print("Soloing Mixer Track: " + str(_selectedMixerTrack))
        mixer.soloTrack(_selectedMixerTrack)
    elif _focusedWindow == midi.widPlaylist:
        print("Soloing Playlist Track: " + str(_selectedPlaylistTrack))
        playlist.soloTrack(_selectedPlaylistTrack)
    return

def handleOrangeButton(control, value):
    global _focusedWindow
    global _selectedMixerTrack
    global _selectedRouteTrack
    global _selectedPlaylistTrack
    global _isMIXERMODE

    if _isMIXERMODE:
        if mixer.getRouteSendActive(_selectedMixerTrack, _selectedRouteTrack):
            print("Unrouting " + str(_selectedMixerTrack) + " to " + str(_selectedRouteTrack))
            mixer.setRouteTo(_selectedMixerTrack, _selectedRouteTrack, 0)
        else:
            print("Routing " + str(_selectedMixerTrack) + " to " + str(_selectedRouteTrack))
            mixer.setRouteTo(_selectedMixerTrack, _selectedRouteTrack, 1)
        return
    if _focusedWindow == midi.widChannelRack:
        channels.soloChannel(channels.selectedChannel())
    elif _focusedWindow == midi.widMixer:
        print("Arming Track: " + str(_selectedMixerTrack) + " for recording")
        mixer.armTrack(_selectedMixerTrack)
    elif _focusedWindow == midi.widPlaylist:
        playlist.soloTrack(_selectedPlaylistTrack)
    return

#-----------------------------------------------------------------------------------------------
#-----------------------------------PLAYLIST-MODE-KNOB-HANDLING---------------------------------
#-----------------------------------------------------------------------------------------------

def handlePlaylistBlueKnob(control, value):
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
            print("This shouldn't happen")
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))

def handlePlaylistOchreKnob(control, value):
    global _ochreVal

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
            print("This shouldn't happen here")
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))
    
    return

def handlePlaylistGrayKnob(control, value):

    return

def handlePlaylistOrangeKnob(control, value):

    return

#-----------------------------------------------------------------------------------------------
#--------------------------------------INSERT-MODE-KNOB-HANDLING--------------------------------
#-----------------------------------------------------------------------------------------------

def handleInsertBlueKnob(control, value):
    global _blueVal
    global _selectedInsert

    if value > _blueVal:
        print("Jog Blue by 1")
        _blueVal = value


    elif value < _blueVal:
        print("Jog Blue by -1")
        _blueVal = value
        ui.jog(JOG_DOWN)
    elif value == _blueVal:
        if value == MAX_KNOB:
            print("Jog Blue by 1")
            ui.jog(JOG_UP)
        elif value == MIN_KNOB:
            print("Jog Blue by -1")
            ui.jog(JOG_DOWN) 
        else:
            print("This shouldn't happen")
    else:
        print("Unrecognized: " + str(control) + ", " + str(value))
    return

#-----------------------------------------------------------------------------------------------
#--------------------------------------PLAYLIST-MODE-KNOB---------------------------------------
#-----------------------------------------------------------------------------------------------

def bluePlaylistKnob(change):    
    global _selectedPlaylistTrack

    print("Jog playlist track by: " + str(change))
    
    playlist.deselectAll()
    updateSelected(change)
    playlist.selectTrack(_selectedPlaylistTrack)

    return

def ochrePlaylistKnob(change):
    print("Job playlist by: " + str(change))
    ui.jog(change)
    return

def grayPlaylistKnob(change):

    return

def orangePlaylistKnob(change):

    return

#-----------------------------------------------------------------------------------------------
#-----------------------------------------MIXER-MODE-KNOB---------------------------------------
#-----------------------------------------------------------------------------------------------

def blueMixerKnob(change):

    return

def ochreMixerKnob(change):

    return   

def grayMixerKnob(change):

    return

def orangeMixerKnob(change):
    global _selectedRouteTrack

    print("Jog playlist track by: " + str(change))
    updateSelectedRoute(change)
    mixer.selectTrack(_selectedRouteTrack)

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
    global _isCHANNELMODE
    global _isPLAYLISTMODE

    print("Resetting to Control Mode")
    _isPLAYLISTMODE = False
    _isCHANNELMODE = False
    _isMIXERMODE = False

    return