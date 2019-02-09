# Sonification of secondary RNA structure

Run `createMIDIclip.py` to create a random  RNA secondary structure in CSSD format (`randomRNA.py` is called) and create a MIDI file containing information concerning how the sonnified RNA should sound like.

A MIDI port is also available and transfers all MIDI information saved on the MIDI file created.
This option is possible by entering any positive value at the `Select playback speed:` message.
The integer inputted will then reflect the speed of a note succeding the next one.

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