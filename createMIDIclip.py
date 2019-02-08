'''
Create a random RNA structure.
Structure is in dot-bracket, consensus secondary structure descriptor (CSSD) format as follows:

'(' and ')': helices closing a multi-branched structure
'<' and '>': base pairs of a terminal stem structure
',': unpaired nucleotides in multi-branch loops
'_': hairpin loop
'-': interior loop (or bulge)

Then create MIDI file to Sonify the generated structure
'''

import mido
import time
import random
import randomRNA

# defines which notes of each octave will be allowed to play
def selectNotes(scale = 'Minor', key = 0):
    scales = {
        'Chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'Major': [0, 2, 4, 5, 7, 9, 11],
        'Minor': [0, 2, 3, 5, 7, 8, 10], # natural minor
        'Minor Pentatonic': [0, 3, 5, 7, 10],
        'Major Pentatonic': [0, 2, 4, 7, 9],
        'Whole Tone': [0, 2, 4, 6, 8, 10],
        'Hirajoshi': [0, 2, 3, 7, 8] # according to Kostka & Payne
    }
    
    notes = scales[scale]
    notes = transposeScale(notes,key)
    print('Scale:', noteNames[key], scale)
    return(notes)

# transpose note list l to key C+step(0-11)
def transposeScale(l, step):
    transposed = []
    for note in l:
        note += step
        if note > 11:
            note -= 12
        transposed.append(note)
    return transposed

# adds a note to midi track
def inputNote(notes, note, octave, noteLength, willNotePlay, intervals, sendToPort):
    if willNotePlay:
        noteToInput = min(note + octave*12, 127)

        # add note to midi track and send it to midi port
        midiTrack.append(mido.Message('note_on', note = noteToInput))
        if sendToPort:
            port.send(mido.Message('note_on', note = noteToInput))

        # keep a list with the added notes (values 0-127)
        notesAdded = [-1] * len(intervals)
        for index in range(len(intervals)):
            interval = intervals[index]
            if interval != 0:
                # find the note in scale
                notesAdded[index] = findIncriment(notes, note, octave, noteLength, interval)
                # add note to midi track and send it to midi port
                midiTrack.append(mido.Message('note_on', note = notesAdded[index]))
                if sendToPort:
                    port.send(mido.Message('note_on', note = notesAdded[index]))

        if sendToPort:
            time.sleep(sendToPort)

        # send note off messages
        midiTrack.append(mido.Message('note_off', note = noteToInput, time = noteLength))
        if sendToPort:
            port.send(mido.Message('note_off', note = noteToInput, time = noteLength))
        # send note off messages for all intevals
        for index in range(len(notesAdded)):
            # if a note was added
            if notesAdded[index] >= 0:
                midiTrack.append(mido.Message('note_off', note = notesAdded[index]))
                if sendToPort:
                    port.send(mido.Message('note_off', note = notesAdded[index]))

        noteToString = noteNames[noteToInput - octave*12] + str(octave)
    else:
        # input pause in midi track
        midiTrack.append(mido.Message('note_off', time = noteLength))
        if sendToPort:
            time.sleep(sendToPort)
        noteToString = '-'

    print(noteToString, end = ' ')
    return noteToString

# find incremented note depending on the step and the root note
def findIncriment(notes, note, octave, noteLength, step):
    if abs(step) >= len(notes):
        if step > 0:
            octave += int(step/len(notes))
        else:
            octave -= int(abs(step)/len(notes))
        step = step % len(notes)

    rootNoteIndex = notes.index(note)
    if rootNoteIndex + step >= len(notes):
        noteToInput = rootNoteIndex + step - len(notes)
    else:
        noteToInput = rootNoteIndex + step

    # fix octaves
    if note > notes[noteToInput] and step > 0:
        octave += 1
    if note < notes[noteToInput] and step < 0: # negative step
        octave -= 1
        
    noteToInput = min(notes[noteToInput] + octave*12, 127)      

    return (noteToInput)

# append midi message to midi track and send it to midi port
def sendQuickMessage(message, port):
    midiTrack.append(message)
    if port:
        port.send(message)

# initialize midi track, midi file and midi port
def initializeMido():

    sendToPort = float(input('Select live playspeed to midi port in seconds per note (float from 0 to 1): '))

    # create midi track
    midiTrack = mido.MidiTrack()
    
    # create midi file containing the above midi track
    theMidiFile = mido.MidiFile()
    theMidiFile.tracks.append(midiTrack)
    
    # create midi port to directly send midi data
    port = 0
    if  sendToPort:
        # default port to look into
        port = 'loopMIDI Port 1'
        # if that port is not available
        while port not in mido.get_output_names():
            print('Select one of the following ports available to send midi data:')
            print(mido.get_output_names())
            port = input()
        print ('Succesfully opened midi port')
        port = mido.open_output(port)
    
    return (sendToPort, midiTrack, port, theMidiFile)

if __name__ == "__main__":

    # set mido stuff
    sendToPort, midiTrack, port, theMidiFile = initializeMido()

    # create a random RNA structure with 100-200 nucleotides and 1-3 hairpin loops
    wuss, numberOfLoops = randomRNA.createRandomRNAstructure(random.randint(100, 200),3)# random.randint(1,3))

    # calculate distance from beginning of branch for each nucleotide
    distances = randomRNA.findDistances(wuss)

    # strategies calculating the next note to be inputed in midi track
    strategies = {'(': 'Up', '<': 'Up', ')': 'Down', '>': 'Down', '_': 'Pause', ':': 'Pause',
                    '-' :'Stable', ',': 'Disharmony', '[': 'Pseudoknot', ']': 'Pseudoknot'}
    noteNames = {0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'}

    # choose scale
    notes = selectNotes()

    noteLength = int(1920/16) # 1920 = whole note

    # set highest and lowest octave to be played
    octaveH = 8
    octaveL = 2

    notesNum = len(wuss)

    # initialize shit
    prevNote = 0 # index of previous note of the scale of MIDI sequence
    prevOct = octaveL # previous octave of MIDI sequence
    
    # input first note (the root note of the selected scale always)
    inputNote(notes, notes[0], octaveL, noteLength, True, [0, 0, 0], sendToPort)
    sendQuickMessage(mido.Message('aftertouch', value = 0), port)

    # pseudoknots midi track
    midiTrack2 = mido.MidiTrack()
    theMidiFile2 = mido.MidiFile()
    theMidiFile2.tracks.append(midiTrack2)
    # initialize previous to first pseudoknot note to input
    prevPKnote = notes[0] + (octaveL + 2)*12 - 7

    # iterate through all nucleotides
    for index in range(notesNum):

        # starting state for all nucleotides: play one note with no intervals added
        willNotePlay = True
        intervals = [0, 0, 0]
        hasSeenPK = False
        
        # send control change depending on distance
        sendQuickMessage(mido.Message('control_change', control = 20, value = distances[index]), port)    

        # add increments for base pairs
        if wuss[index] == '-':
            intervals = [2, -2, 4]

        # add midi control changes and octaves in closing helix
        if wuss[index] == '(':
            sendQuickMessage(mido.Message('aftertouch', value = 0), port)
            # add octaves in beginning and end of closing helix
            if wuss[index + 1] != '(':
                intervals = [2*len(notes), 3*len(notes), 4*len(notes)]
        elif wuss[index] == ')':
            sendQuickMessage(mido.Message('aftertouch', value = 127), port)
            # add octaves in beginning and end of closing helix
            if wuss[index - 1] != ')':
                intervals = [2*len(notes), 3*len(notes), 4*len(notes)]
        else:
            sendQuickMessage(mido.Message('aftertouch', value = 63), port)
        
        # select strategy depending on how the nucleotide is structured
        playMode = strategies[wuss[index]]

        # select note to play depending on strategy   
        if playMode == 'Up':
            if prevNote == len(notes)-1: # if prev note was last of scale
                noteToInput = notes[0] # go to first note of scale
                prevNote = 0
                if octaveH - octaveL > 0: # if there are more octaves
                    if octaveH != prevOct: # if the highest octave isn't reached yet
                        octaveToInput = prevOct + 1 # go up an octave
                        prevOct += 1
                    else: # if we already are at the highest octave
                        octaveToInput = octaveL # cycle back to the lowest octave
                        prevOct = octaveL
            else:
                noteToInput = notes[prevNote + 1]
                octaveToInput = prevOct
                prevNote += 1

        elif playMode == 'Down':
            if prevNote == 0: # if prev note was first of scale
                noteToInput = notes[-1] # go to last note of scale
                prevNote = len(notes) - 1
                if octaveH - octaveL > 0: # if there are more octaves
                    if octaveL != prevOct: # if the lowest octave isn't reached yet
                        octaveToInput = prevOct - 1 # go down an octave
                        prevOct -= 1
                    else: # if we already are at the lowest octave
                        octaveToInput = octaveH # cycle back to the highest octave
                        prevOct = octaveH
            else:
                noteToInput = notes[prevNote - 1]
                octaveToInput = prevOct
                prevNote -= 1
            
        elif playMode == 'Stable':
            noteToInput = notes[prevNote]
            octaveToInput = prevOct

        elif playMode == 'Pause':
            noteToInput = notes[prevNote]
            octaveToInput = prevOct
            willNotePlay = False

        elif playMode == 'Disharmony':
            allNotes = list(range(0,12))
            notInScaleNotes = [x for x in allNotes if x not in notes]
            if notInScaleNotes: # in case of chromatic scale there is no disharmony
                noteToInput = notInScaleNotes[random.randint(0,len(notInScaleNotes)-1)]
            else:
                noteToInput = notes[random.randint(0,len(notes) - 1)]
            octaveToInput = min(prevOct + 2, 8)
        
        elif playMode == 'Pseudoknot':
            willNotePlay = False
            if wuss[index] == '[':
                # add 5th from previous PK note
                PKnote = prevPKnote + 7
            elif wuss[index] == ']':
                if wuss[index - 1] != ']':
                    PKnote = prevPKnote
                else:
                    # subtract 4th from previous PK note
                    PKnote = prevPKnote - 7
            prevPKnote = PKnote
            midiTrack2.append(mido.Message('note_on', note = PKnote, time = noteLength))
            # midiTrack2.append(mido.Message('note_off', time = noteLength))
            if wuss[index] == ']':
                midiTrack2.append(mido.Message('note_off', note = PKnote, time = noteLength))
            if sendToPort:
                port.send(mido.Message('note_on', note = PKnote, channel = 1))
                if wuss[index] == ']':
                    time.sleep(sendToPort)
                    port.send(mido.Message('note_off', note = PKnote, channel = 1))
      
        # pause pseudoknot tracks
        if playMode != 'Pseudoknot':
            midiTrack2.append(mido.Message('note_off', time = noteLength))

        # scale play in range (octave, octave + 1) so that root note is always 1st
        if noteToInput < notes[0]:
            octaveToInput += 1

        # input note to midi track
        inputNote(notes, noteToInput, octaveToInput, noteLength, 
                                willNotePlay, intervals, sendToPort)        

    # close midi ports
    if sendToPort:
        port.close()

    # save midi file
    theMidiFile.save('thisIsAnRNAstructure.mid')
    theMidiFile2.save('thisIsAnRNAstructurePKs.mid')