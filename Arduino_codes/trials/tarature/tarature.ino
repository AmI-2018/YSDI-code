#include <HX711.h>

HX711 scale(A1, A0);    // parameter "gain" is ommited; the default value 128 is used by the library



void setup() {
  Serial.begin(9600);
  Serial.print(scale.get_scale());
  scale.set_scale();
  scale.tare();
  scale.set_scale(194.f);
  //Serial.print(scale.get_units(10));
};

void loop() {
 
};
