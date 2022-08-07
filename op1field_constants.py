blueKnob = 1
ochreKnob = 2
grayKnob = 3
orangeKnob = 4

opKNOBS = [blueKnob, ochreKnob, grayKnob, orangeKnob]

blueButton = 59
ochreButton = 60
grayButton = 61
orangeButton = 62

opKNOBBUTTON = [blueButton, ochreButton, grayButton, orangeButton]

micButton = 48
comButton = 49
seqButton = 26
helpButton = 5
tempoButton = 6

opSPECIAL = [micButton, comButton, seqButton, helpButton, tempoButton]

synthButton = 7
drumButton = 8
tapeButton = 9
mixerButton = 10

opCONTROL = [synthButton, drumButton, tapeButton, mixerButton]

oneButton = 11
twoButton = 12
threeButton = 13
fourButton = 14

opFOUR = [oneButton, twoButton, threeButton, fourButton]

opOne = 50
opTwo = 51
opThr = 52
opFor = 21
opFiv = 22
opSix = 23
opSev = 24
opEit = 25

opMACROS = [opOne, opTwo, opThr, opFor, opFiv, opSix, opSev, opEit]

liftButton = 15
dropButton = 16
cutButton = 17

opEDIT = [liftButton, dropButton, cutButton]

recButton = 38
playButton = 39
stopButton = 40

opTRANSPORT = [recButton, playButton, stopButton]

AVAILABLE_BUTTONS = [opTRANSPORT, opEDIT, opMACROS, opFOUR, opCONTROL, opSPECIAL, opKNOBS]

CONTROL_KEY = 12
CONTROL_STATUS = 180
KEYBOARD_STATUS = 148

MAX_KNOB = 127
MIN_KNOB = 0

MAX_GRID_LENGTH = 508
MIN_GRID_LENGTH = 0

MAX_PLAYLIST_TRACK = 32
MIN_PLAYLIST_TRACK = 1

JOG_UP = 1
JOG_DOWN = -1

PIANO_ROLL = 55
MIDI_PORT = 5

OCHRE_CONTROL = 0
GRAY_CONTROL = 1
ORANGE_CONTROL = 2

CHANNEL_CONTROLS = [OCHRE_CONTROL, GRAY_CONTROL, ORANGE_CONTROL]

OCHRE_CHANNEL = 12
GRAY_CHANNEL = 40
ORANGE_CHANNEL = 78

SCROLL_SPEED = [1, .5, .25, .25 * .25]

def normalizePolar(value):
    result = 2 * ((value - 0) / 127) - 1
    return result