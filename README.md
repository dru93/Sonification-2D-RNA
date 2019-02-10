# Sonification of secondary RNA structure

Pure Data and Ableton Live are optionally required. Check:
- [https://puredata.info](https://puredata.info/)
- [https://www.ableton.com](https://www.ableton.com/)

Also, a (virtual) MIDI port has to be available in the machine running these scripts.
If running in a windows environment check:
- [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)

A MIDI port transfers MIDI information that is then saved to the MIDI file created.
This MIDI information dictates the sounds that will play depending on the RNA secondary structure sequence imported.

## Steps to do if you wanna hear any sounds

1. Open Pure Data and load the `read-midi-port.pd` patch (optional)
2. Open Ableton Live and load the template (optional)
3. Run `createMIDIclip.py` to create a random  RNA secondary structure in CSSD format (`randomRNA.py` is called) and create a MIDI file containing information concerning how the sonnified RNA should sound like.

Sonification rules:

| CSSD symbol | Nucleotide action  | Sonification  |
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

- Audio is panned depending on if a helix is opening or closing.
- Distance of each nucleotide from center is calculated and assigned to reverb mix.