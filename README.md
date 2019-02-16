# Sonification of RNA secondary structure

Pure Data and Ableton Live are optionally required. Check:
- [https://puredata.info](https://puredata.info/)
- [https://www.ableton.com](https://www.ableton.com/)

Also, a (virtual) MIDI port is optionally required.

### Using virtual MIDI buses

- If running in a windows environment check:
[https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)

- In a Unix environment check:
[https://wiki.debian.org/AlsaMidi](https://wiki.debian.org/AlsaMidi)

- Mac offers native virtual MIDI driver


A MIDI port transfers MIDI information that is then saved to the MIDI file created.
This MIDI information dictates the sounds that will play depending on the RNA secondary structure sequence imported.

## Steps to do if you wanna hear any sounds

1. Open Pure Data and load `sonification-template.pd`, or open Ableton Live and load `sonification-template.als`

2. Run `python createMID.py` in a terminal. If there are no input arguments, a random  RNA secondary structure in CSSD format will be created (`randomRNA.py` is called), else you can input as an argument any specific .txt file located in the 'RNA structures' directory you want to sonify. A MIDI file containing information concerning how the sonnified RNA should sound like will be saved. The same MIDI information will also be passed through any open MIDI ports.


3. If step 1 was bypassed but still wanna hear something, import the .mid files generated in the previous step here: [https://onlinesequencer.net/import](https://onlinesequencer.net/import)
   
## Audio mappings

### Pitch frequency

| CSSD symbol | Nucleobase         | Pitch         |
| :--------:  |:------------------:| :------------:|
| `(`         | helix opening      | pitch up      |
| `)`         | helix closing      | pitch down    |
| `<`         | base pair opening  | pitch up      |
| `>`         | base pair closing  | pitch down    |
| `[`         | pseudoknot opening | arpeggio up   |
| `]`         | pseudoknot closing | arpeggio down |
| `-`         | interior loop      | stay idle     |
| `_`         | hairpin loop       | pause         |
| `,`         | unpairing          | dissonance    |

### Space

- Sound direction: Depending on sequence index
  
- Reverb: Depending on index distance from structure center

## Pure Data patch

1. Record MIDI
2. Store MIDI info in arrays
3. Generate audio engine
4. Playback MIDI info
5. Record/explore audio

![Pure data patch](/images/pdPatch.png)
