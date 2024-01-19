#include <Wire.h>
#include "Adafruit_VL6180X.h"

Adafruit_VL6180X vl = Adafruit_VL6180X();

void setup() {
  // wait until serial port and device are ready
  Serial.begin(115200);

  while (!Serial)
    delay(1);

  if (!vl.begin())
    while (1);
}

void loop() {
  // report distance once per second
  uint8_t range = vl.readRange();
  uint8_t status = vl.readRangeStatus();

  if (status == VL6180X_ERROR_NONE)
    Serial.println(range);

  delay(50);
}