/*
WOW
prerequisite liraries:
MIDI_controller-3.1.0
MIDIUSB
*/

#include <MIDI_Controller.h> // Include the library

// Create a new instance of the class 'Analog', called 'potentiometer', on pin A0, 
// that sends MIDI messages with controller 7 (channel volume) on channel 1
// (pin, midiCC, channel)
Analog potentiometer1(A0, 1, 1);
Analog potentiometer2(A1, 2, 1);
// (digital in, note, channel, velocity)
Digital button1(2, 60, 1, 127);
Digital button2(3, 61, 1, 127);
Digital button3(4, 62, 1, 127);
Digital button4(5, 63, 1, 127);

void setup() {}

void loop() {
  // Refresh the MIDI controller (check whether the potentiometer's input has changed since last time, if so, send the new value over MIDI)
  MIDI_Controller.refresh();
}
