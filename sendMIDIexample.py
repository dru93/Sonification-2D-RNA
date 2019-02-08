import mido
import time
import random

# append midi message to midi track and send it to midi port
def sendQuickMessage(message, port):
    midiTrack.append(message)
    if port:
        port.send(message)

# create a MIDI track
midiTrack = mido.MidiTrack()

# create midi file containing the above midi track
theMidiFile = mido.MidiFile()
theMidiFile.tracks.append(midiTrack)

# open a MIDI port
port = mido.open_output('loopMIDI Port 1')

MIDImessage = mido.Message('note_on', note = 60)
sendQuickMessage(MIDImessage, port)

# close the midi port
port.close()