/*
 11-14-2013
 SparkFun Electronics 2013
 Shawn Hymel

 This code is public domain but you buy me a beer if you use this 
 and we meet someday (Beerware license).

 Description:

 This sketch shows how to use the SparkFun INA169 Breakout
 Board. As current passes through the shunt resistor (Rs), a
 voltage is generated at the Vout pin. Use an analog read and
 some math to determine the current. The current value is
 displayed through the Serial Monitor.

 Hardware connections:

 Uno Pin    INA169 Board    Function

 +5V        VCC             Power supply
 GND        GND             Ground
 A0         VOUT            Analog voltage measurement

 VIN+ and VIN- need to be connected inline with the positive
 DC power rail of a load (e.g. an Arduino, an LED, etc.).

 */

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
// Constants
const int SENSOR_PIN = A0;  // Input pin for measuring Vout
const int RS = 1;          // Shunt resistor value (in ohms)
const int VOLTAGE_REF = 5;  // Reference voltage for analog read

// Global Variables
float sensorValue;   // Variable to store value from analog read
float current;       // Calculated current value

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  // Initialize serial monitor
  Serial.begin(9600);

}

void loop() {
  for (pos = 10; pos <= 90; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
      // Read a value from the INA169 board
    sensorValue = analogRead(SENSOR_PIN);

    // Remap the ADC value into a voltage number (5V reference)
    //sensorValue = (sensorValue * VOLTAGE_REF) / 1023;

    // Follow the equation given by the INA169 datasheet to
    // determine the current flowing through RS. Assume RL = 10k
    //Is = (Vout x 1k) / (RS x RL)
    //current = sensorValue / (10 * RS);

    // Output value (in amps) to the serial monitor to 3 decimal
    // places
    Serial.println(sensorValue);
    //Serial.println(" A");

    // Delay program for a few milliseconds
    delay(20);                      // waits 15 ms for the servo to reach the position
  }
  for (pos = 90; pos >= 10; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
                          // waits 15 ms for the servo to reach the position
      // Read a value from the INA169 board
    sensorValue = analogRead(SENSOR_PIN);

    // Remap the ADC value into a voltage number (5V reference)
    //sensorValue = (sensorValue * VOLTAGE_REF) / 1023;

    // Follow the equation given by the INA169 datasheet to
    // determine the current flowing through RS. Assume RL = 10k
    // Is = (Vout x 1k) / (RS x RL)
    //current = sensorValue / (10 * RS);

  // Output value (in amps) to the serial monitor to 3 decimal
  // places
    Serial.println(sensorValue);
    //Serial.println(" A");

  // Delay program for a few milliseconds
    delay(20);
  }
}

