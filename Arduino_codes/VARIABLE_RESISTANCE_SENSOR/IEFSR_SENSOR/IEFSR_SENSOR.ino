int tmp=0;
float threshold = 0.10;


// the setup routine runs once when you press reset:
void setup() {
// initialize serial communication at 9600 bits per second:
Serial.begin(9600);
}


// the loop routine runs over and over again forever:

void loop() {

// read the input on analog pin 0:
int sensorValue = analogRead(A0);
int sensorValue_1 = analogRead(A1);
int difference = sensorValue - sensorValue_1 ;
// Convert the analog reading (which goes from 0 – 1023) to a voltage (0 – 5V):
float voltage = difference * (5.0 / 1023.0);
//Serial.println(voltage);
if (voltage > threshold)
{
 tmp = tmp + 1;
}

if(tmp == 1)
 {
  Serial.println(1); // print out the value you read when first reading of some weigth;
  tmp = tmp + 1;
 }
else
{
  if (tmp > 1 && voltage <= threshold)
  {
    tmp = 0;
    Serial.println(0); // print out the value you read when first reading of some weigth;
  }
}
delay(1500);
}

