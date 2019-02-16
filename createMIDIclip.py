'''
Input arguments: filename of RNA structure to sonify
-Create MIDI data to sonify the generated structure

MIDI port channels (0-16) routing:
0: main melody pitch, midi CCs
1: pseudoknots pitch
2: steady pulse
3: main melody velocity
4: pseudoknots melody velocity
'''

import os
import sys
import mido
import time
import math
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

    # send pulse
    if sendToPort:
        port.send(mido.Message('note_on', note = 60, channel = 2))
    
    # send main melody velocity to channel 3
    if willNotePlay:
        port.send(mido.Message('note_on', velocity = 127, channel = 3))
    else:
        port.send(mido.Message('note_off', velocity = 0, channel = 3))

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

    sendToPort = 0.01 # float(input('Select live playspeed to midi port in seconds per note (float from 0 to 1): '))

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
            print('Select one of the following ports available to send MIDI data:')
            print(mido.get_output_names())
            port = input()
        port = mido.open_output(port)
    
    return (sendToPort, midiTrack, port, theMidiFile)

# find distance between min and max notes played
def findMaxNoteDistance(wuss):
    maxDist = 0
    dist = 0
    notesNum = len(wuss)
    for index in range(notesNum):
        if wuss[index] == '(' or wuss[index] == '<':
            dist += 1
        elif wuss[index] == ')' or wuss[index] == '>':
            dist -= 1
        if dist > maxDist:
            maxDist = dist

    return maxDist

# determine first note played by putting the whole sequence in 
# the middle of the piano keyboard
def findFirstNote(maxDist, notes):
    firstNote = 0
    octaveLow = 0
    # never happens with 200 nucleotides
    if maxDist > 127:
        print('Memory issues :/')
        sys.exit()
    else:
        # choose C chromatic scalee if notes of current scale are not enough
        if len(notes) * 8 < maxDist:
            notes = selectNotes('Chromatic', 0)
        # |oooo|oooo|oooo|oooo|
        firstPosition = int(maxDist + ((len(notes) * 8) - maxDist)/2)

        octaLow = int(firstPosition / len(notes))
        firstNote = notes[int(firstPosition % len(notes))]
        
    return firstNote, octaveLow

if __name__ == '__main__':

    # make RNA structures directory
    if not os.path.exists('RNA structures/'):
        os.makedirs('RNA structures/')

    # if no arguments were passed or want to sonify something at random
    if len(sys.argv) == 1 or sys.argv[1] == 'random':
        filename = 'RNA structures/random.txt'
        # create a random RNA structure with 100-200 nucleotides and 1-3 hairpin loops
        wuss, numberOfLoops = randomRNA.createRandomRNAstructure(random.randint(100, 200), random.randint(1,3))
        f = open('RNA structures/random.txt','w+')
        f.write(wuss)
        f.close()
    else:
        filename = 'RNA structures/' + sys.argv[1] + '.txt'

    f = open(filename, 'r')
    wuss = f.read()
    f.close()

    # set mido stuff
    sendToPort, midiTrack, port, theMidiFile = initializeMido()

    # calculate distance from beginning of branch for each nucleotide
    distances = randomRNA.findDistances(wuss)

    notesNum = len(wuss)

    # strategies calculating the next note to be inputed in midi track
    strategies = {'(': 'Up', '<': 'Up', ')': 'Down', '>': 'Down', '_': 'Pause', ':': 'Pause',
                    '-' :'Stable', ',': 'Disharmony', '[': 'Pseudoknot', ']': 'Pseudoknot'}
    noteNames = {0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'}

    # choose a scale
    notes = selectNotes('Minor', random.randint(0, 11))

    noteLength = int(1920/16) # 1920 = whole note

    # set highest and lowest octave to be played
    octaveH = 8
    octaveL = 2

    # initialize shit
    prevNote = 0 # index of previous note of the scale of MIDI sequence
    prevOct = octaveL # previous octave of MIDI sequence
    
    # maxDist = findMaxNoteDistance(wuss)
    # prevNote, prevOct = findFirstNote(maxDist, notes)
    # print('First note:', prevNote)

    # # input first note (the root note of the selected scale always)
    # inputNote(notes, prevNote, octaveL, noteLength, True, [0, 0, 0], sendToPort)

    # pseudoknots midi track
    midiTrackPK = mido.MidiTrack()
    theMidiFilePK = mido.MidiFile()
    theMidiFilePK.tracks.append(midiTrackPK)
    # initialize previous to first pseudoknot note to input
    prevPKnote = notes[0] + (octaveL + 2)*12 - 7

    # iterate through all nucleotides
    for index in range(notesNum):

        # starting state for all nucleotides: play one note with no intervals added
        willNotePlay = True
        intervals = [0, 0, 0]

        # add increments in start end positions of interior loops
        if wuss[index] == '-' and wuss[index + 1] != '-':
            intervals = [2, -2, 4]

        # add octaves in start end positions of helix
        if wuss[index] == '(' and  wuss[index + 1] != '(':
            intervals = [2*len(notes), 3*len(notes), 4*len(notes)]
        elif wuss[index] == ')' and wuss[index - 1] != ')':
            intervals = [2*len(notes), 3*len(notes), 4*len(notes)]
        
        # select strategy depending on how the nucleotide is structured
        playMode = strategies[wuss[index]]
        # exception for first after loop
        if wuss[index - 1] == '_' and wuss[index] != '_':
            # exception for pseudoknots
            if wuss[index] != '[' and wuss[index] != ']':
                playMode = 'Stable' 

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
            # send main melody velocity to channel 
            port.send(mido.Message('note_on', velocity = 127, channel = 4))

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
            midiTrackPK.append(mido.Message('note_on', note = PKnote, time = noteLength))
            # midiTrackPK.append(mido.Message('note_off', time = noteLength))
            if wuss[index] == ']':
                midiTrackPK.append(mido.Message('note_off', note = PKnote, time = noteLength))
            if sendToPort:
                port.send(mido.Message('note_on', note = PKnote, channel = 1, velocity = 127))
      
        # pause pseudoknot tracks
        if playMode != 'Pseudoknot':
            midiTrackPK.append(mido.Message('note_off', time = noteLength))

        # scale play in range (octave, octave + 1) so that root note is always 1st
        if noteToInput < notes[0]:
            octaveToInput += 1

        # input note to midi track
        inputNote(notes, noteToInput, octaveToInput, noteLength, 
                                willNotePlay, intervals, sendToPort)        

        # send control change depending on position
        # midi CC 21: pan
        if index == 0:
            panValue = 0
        elif index == notesNum - 1:
            panValue = 1
        else:
            panValue = index / notesNum # map linearly to 0-1
            panValue = 1 / (1 + math.exp(-10*(panValue - 0.5))) # transform to sigmoid (scale factor 10)
        panValue = int(round(panValue * 127, 0)) # remap to 0-127
        sendQuickMessage(mido.Message('control_change', control = 21, value = panValue), port)

        # send control change depending on distance
        # midi CC 20: distances
        sendQuickMessage(mido.Message('control_change', control = 20, value = distances[index]), port)
  

    # close midi ports
    if sendToPort:
        port.close()

    # save midi files to 'MIDI files' folder
    if not os.path.exists('MIDI files/'):
        os.makedirs('MIDI files/')
    theMidiFile.save('MIDI files/thisIsAnRNAstructure.mid')
    theMidiFilePK.save('MIDI files/thisIsAnRNAstructurePKs.mid')