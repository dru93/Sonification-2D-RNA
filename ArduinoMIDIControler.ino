/*
liraries:
MIDI_controller-3.1.0
MIDIUSB
*/

#include <MIDI_Controller.h> // Include the library

// Create a new instance of the class 'Analog', called 'potentiometer-', on A0-A2, 
// that send MIDI messages with controller 1-3 (channel volume) on channel 9
// potentiometer-(pin, midiCC, channel)
Analog potentiometer1(A0, 1, 9);
Analog potentiometer2(A1, 2, 9);
Analog potentiometer3(A2, 3, 9);

// Create a new instance of the class 'Digital', called 'button-', on 2-5, 
// that sends MIDI notes (60-63) on channel 9
// button-(digital in, note, channel, velocity)
Digital button1(2, 60, 9, 127);
Digital button2(3, 61, 9, 127);
Digital button3(4, 62, 9, 127);
Digital button4(5, 63, 9, 127);

void setup() {}

void loop() {
  // Refresh the MIDI controller (check whether the potentiometer's input has changed since last time, if so, send the new value over MIDI)
  MIDI_Controller.refresh();
}
