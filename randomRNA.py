'''
Create a random RNA structure.
Structure is in dot-bracket, consensus secondary structure descriptor (CSSD) format as follows:

'(' and ')': helices closing a multi-branched structure
'<' and '>': base pairs of a terminal stem structure
',': unpaired nucleotides in multi-branch loops
'_': hairpin loop
'-': interior loop (or bulge)
'''

import random

# fills in fully unpaired (',') structure with a hairpin loop, base pairs and interior loops
# in case of assymetry, leaves an unpaired nucleotide
def makeBranch(structure):

	numberOfNucl = len(structure)

	# initialize hairpin loop location and length
	loopLength = int(numberOfNucl/4)
	loopLength = max(random.randint(loopLength - 3, loopLength + 3), 3)

	# constrain it to stay approximately in the middle
	loopPosition =  round(numberOfNucl/2 - loopLength/2, 0)
	loopPosition = random.randint(loopPosition - 1, loopPosition + 1)

	# make hairpin loop
	for index in range(loopPosition, loopPosition + loopLength):
		structure[index] = '_'

	# make base pairs and interior loops
	for index in range(loopPosition):

		# pairMirrorIndex is the mirrored to the hairpin loop nucleotide of index
		pairMirrorIndex = loopPosition  + loopLength + (loopPosition - index - 1)
		if pairMirrorIndex < numberOfNucl:

			# assign base pair right before hairpin loop and exit loop
			if structure[index + 1] == '_' or index == 0:
				structure[index] = '<'
				structure[pairMirrorIndex] = '>'

			# probability of a base pair vs an interior loop is typically 0.5
			basePairProb = round(random.random(), 0)
			# if previous nucleotide was paired, it's more probable to have a base pair again
			# so base pairing probability changes form 0.5 to ~0.86 (6/7)
			if structure[index - 1] == '<':
				basePairProb = round(random.randint(4,10)/10, 0)

			# if the mirrored nucleotide is no value assigned yet
			if structure[pairMirrorIndex] == ',':
				if basePairProb:
					structure[index] = '<'
					structure[pairMirrorIndex] = '>'
				else:
					structure[index] = '-'
					structure[pairMirrorIndex] = '-'

	return(structure)

# randomly add some extra unpaired nucleotides
def addUnpairedNucl(structure, numberOfUnpairedNucl):
    numberOfNucl = len(structure)
    for _ in range(numberOfUnpairedNucl):
        position = random.randint(0, numberOfNucl - 1)
        # make sure unpaired nucleotide is not inserted in closing helix or hairpin loops
        while structure[position] != '-' and structure[position] != '<' and structure[position] != '>':
            position = random.randint(0, numberOfNucl - 1)
        structure.insert(position, ',')
    print('Added extra unpaired nucleotides')

    return (structure)

def addPseudoknot(structure, numberOfPKs):
    if numberOfPKs == 0:
        return (structure)
        
    numberOfNucl = len(structure)
    # find 1st loop indices
    loopIndices = []
    for index in range(len(structure) - 1):
        if structure[index] == '_':
            loopIndices.append(index)
        if structure[index] == '_' and structure[index + 1] != '_':
            lastIndex = index
            break

    # add opening pseudoknot
    validLoopIndices = loopIndices[0:(len(loopIndices) - int(numberOfPKs/2))]
    startOfPk = validLoopIndices[random.randint(0, len(validLoopIndices) - 1)]
    for index in range(startOfPk, int(startOfPk + numberOfPKs/2)):
        structure[index] = '['
    
    # find 2nd loop indices
    loop2Indices = []
    metFirstLoop = False
    for index in range(lastIndex + 1, len(structure)):
        if structure[index - 1] == '_' and structure[index] != '_':
            metFirstLoop = True
        if metFirstLoop == True:
            if structure[index] == '_':
                loop2Indices.append(index)
                if structure[index + 1] != '_':
                    break
    
    # add closing pseudoknot
    print (validLoopIndices)
    validLoopIndices = loop2Indices[0:(len(loop2Indices) - int(numberOfPKs/2))]
    startOfPk = validLoopIndices[random.randint(0, len(validLoopIndices) - 1)]
    for index in range(startOfPk, int(startOfPk + numberOfPKs/2)):
        structure[index] = ']'
     
    print('Added pseudoknot')
    return (structure)

# creates a random RNA structure with determined number of nucleotides and hairpin loops
def createRandomRNAstructure(numberOfNucl, numberOfLoops):
    # set probability of adding extra unpaired nucleotides to ~0.14 (1/7)
    willAddUnpairedNucl = round(random.randint(0,6)/10, 0)
    if willAddUnpairedNucl:
        # define number of unpaired nucleotides and randomize it a bit
        numberOfUnpairedNucl = int(numberOfNucl/22)
        numberOfUnpairedNucl = min(random.randint(numberOfUnpairedNucl - 2, numberOfUnpairedNucl + 2), 1)
        numberOfNucl -= numberOfUnpairedNucl

    #  will a pseudoknot be added?
    numberOfPKs = 0
    if numberOfLoops > 1:
        # set probability of adding a pseudoknot to 0.5 (5/10)  
        willAddPKs = round(random.randint(1,10)/10, 0)
        if willAddPKs:
            # set number of pseudoknot nucleotides between 2 and 4 at random
            numberOfPKs = random.randint(2, 4) * 2

    # initialize structure with unpaired nucleotides
    structure = [','] * numberOfNucl

    # add unstructured nucleotides
    numberOfUnstruct = random.randint(1,10)
    for index in range(numberOfUnstruct):
        structure[index] = ':'
        structure[numberOfNucl - index - 1] = ':'
    
    # set number of total nucleotides and number of nucleotides in closing helices
    numberOfHlxNucl = int(numberOfNucl/10)
    numberOfHlxNucl = max(random.randint(numberOfHlxNucl - 2, numberOfHlxNucl + 2), 1)
    # make opening and closing helices
    for index in range(numberOfHlxNucl - numberOfUnstruct):
        structure[index + numberOfUnstruct] = '('
        structure[numberOfNucl - index - 1 - numberOfUnstruct] = ')'

    # crop closing helices
    startPoint = numberOfHlxNucl
    endPoint = numberOfNucl - numberOfHlxNucl -1

    # add hairpin loops to structure
    if numberOfLoops == 1:
        # fill structure of croped subsequence
        loop = makeBranch(structure[startPoint:endPoint])
        # recombine all subsequences
        structure = structure[0:startPoint] + loop + structure[endPoint:len(structure)]

    elif numberOfLoops == 2:
        # create 2 subsequences indices (crop closing helices)
        seqBreakPoint = int(len(structure)/2)
        # fill each subsequence individually
        loop1 = makeBranch(structure[startPoint:seqBreakPoint])
        loop2 = makeBranch(structure[(seqBreakPoint):endPoint])
        # recombine all subsequences
        structure = structure[0:startPoint] + loop1 + loop2 + structure[endPoint:len(structure)]
    else:
        # create 2 subsequences indices (crop closing helices)
        seqBreakPoint1 = int(len(structure)/3)
        seqBreakPoint2 = int(len(structure)/3*2)
        # fill each subsequence individually
        loop1 = makeBranch(structure[startPoint:seqBreakPoint1])
        loop2 = makeBranch(structure[(seqBreakPoint1):seqBreakPoint2])
        loop3 = makeBranch(structure[(seqBreakPoint2):endPoint])
        # recombine all subsequences
        structure = structure[0:startPoint] + loop1 + loop2 + loop3 + structure[endPoint:len(structure)]

    # add unpaired nucleotides to the sequence
    if willAddUnpairedNucl:
        structure = addUnpairedNucl(structure, numberOfUnpairedNucl)
    
    # add pseudoknots to the sequence
    if numberOfLoops > 1:
        structure = addPseudoknot(structure, numberOfPKs)

    # convert it to string and print messages
    strStructure = ''.join(structure)
    print('RNA structure:', strStructure)
    print('Number of hairpin loops: ', numberOfLoops)
    print('Number of nucleotides: ', len(structure))

    return (strStructure, numberOfLoops)

# calculate distance from first paired nucleotides of a branch for each nucleotide
def findDistances(structure):

    # initialize dinstances list
    distances = [0] * len(structure)

    foundEnd = False
    nextPartStartIndex = 0
    
    while not foundEnd:

        # find next center
        for index in range(nextPartStartIndex, len(structure) - 1):
            if structure[index] == '<' or structure[index] == ')':
                center = index
                if structure[index] == ')':
                    foundEnd = True
                break

        # fill till first paired nucleotides of next branch or end helix is found
        for index in range(nextPartStartIndex, len(structure) - 1):
            if not foundEnd:
                # keep previous distance if hairpin or internal loop or pseudoknot
                if structure[index] == '_' or structure[index] == '[' or structure[index] == ']':
                    distances[index] = prevDistance
                    # break if found loop
                    if structure[index + 1] != '_':
                        nextPartStartIndex = index + 1
                        break
                # fill in distance otherwise
                else:
                    distances[index] = abs(index - center)
                    prevDistance = distances[index]
            # fill distance for closing helix nucleotides
            else:
                distances[index] = abs(index - center)
                prevDistance = distances[index]

    # # fill in last one
    distances[len(structure)-1] = prevDistance + 1

    # remap to 0-127 values (in order to comply with midi messages)
    maxVal = max(distances)
    distances = [int(round(i*127/maxVal, 0)) for i in distances]

    return (distances)
