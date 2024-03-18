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

 /*
  * this script was modified by Elio and Carlos from the Hacker Fab to control a gripper. 
  * We want to read the current from the gripper so we can tell when it stalls and we've gripped a chip.
  * The raw readings aren't great so we use a moving sum to average the last 50 readings.
  * To do: set a threshold to tell whether the motor is stalled or not.
  */

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 11;    // variable to store the servo position
int i = 1;
int j = 0;
int sum = 0;
int readingLen = 50;
int readings[50];
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
  j += 1;
  //j is just main loop increment so we can sample faster than write.
  //generate triangle wave and write to servo, 10 to 90 degrees
    if (j % 5 == 0){
      if (pos == 10){
      i = 1;
    }
      if (pos == 90){
      i = -1;
    }
    pos += i;
    myservo.write(pos); // tell servo to go to position in variable 'pos'
  }
               
  // Read a value from the INA169 board
  sensorValue = analogRead(SENSOR_PIN);
  readings[j%readingLen] = sensorValue; //update new reading in array
  sum = sum + sensorValue; // update sum
  sum = sum - readings[(j+1)%readingLen]; //remove value from 100 readings ago
  
  // Remap the ADC value into a voltage number (5V reference)
  //sensorValue = (sensorValue * VOLTAGE_REF) / 1023;

  // Follow the equation given by the INA169 datasheet to
  // determine the current flowing through RS. Assume RL = 10k
  //Is = (Vout x 1k) / (RS x RL)
  //current = sensorValue / (10 * RS);
  
  // Output value (in amps) to the serial monitor to 3 decimal
  // places
  Serial.println(sum);
  
  //Serial.println(" A");

  // Delay program for a few milliseconds
  delay(10);                      // waits 15 ms for the servo to reach the position
  }
