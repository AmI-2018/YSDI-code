#include <Bridge.h>
#include <HttpClient.h>
#include <YunClient.h>
#include <SPI.h>

/// GLOBAL VARIABLES ///
int tmp=0; // auxiliary temporary variable
float threshold = 0.10; // refernce threshold needed to evaluate our data

/// IPAddress of the Raspberry server(192,168,0,21); ///
IPAddress rasp_server(192,168,1,84); // specify destination server IP of Raspberry

YunClient client;

///// FUNCTIONS' PROTOTYPES /////////////////////////////////////////////////////////////////////////

void send_to_rasp(int); // function to generate HTTP request to raspberry server with POST method

/////////////////////////////////////////////////////////////////////////////////////////////////////


/// SET-UP FUNCTION

void setup() {
  // put your setup code here, to run once:
  Bridge.begin();
  Serial.begin(9600); // Baud-rate --> D = 9,66 Ksymbols/s

}

// LOOP FUNCTION


void loop() {

// read the input on analog pins 0 and 1:
int sensorValue = analogRead(A0);
int sensorValue_1 = analogRead(A1);
int difference = sensorValue - sensorValue_1 ; // evaluate the voltage difference between the sensor and the resistor
// Convert the analog reading (which goes from 0 – 1023) to a voltage (0 – 5V):
float voltage = difference * (5.0 / 1023.0);
int value=0;

//Serial.println(voltage);

if (voltage > threshold)
{
 tmp = tmp + 1;
}

if(tmp == 1)
 {
  value = 1;
  send_to_rasp(value); // send a message to the server informing it when first reading of some weigth greater than threshold;
  tmp = tmp + 1;
 }
else
{
  if (tmp > 1 && voltage <= threshold)
  {
    tmp = 0;
    value=0;
    Serial.println(threshold);
    send_to_rasp(value); // send to raspberry infromation that a null weight is read --> nobody sits on the chair
  }
}
delay(1500); // delay the next iteration of the loop by 1.5 milliseconds
}

//////////////////// SEND TO RASP FUNCTION /////////////////////////////////

void send_to_rasp(int value)
{
  String JsonData = "{\"value\": ";
  JsonData = JsonData + value;
  JsonData = JsonData + "}";
  Serial.println(threshold);
  client.connect("192.168.1.84", 8080);
  if(client.connected()) // open socket on port 8080
  { 
        Serial.println("Connected");  // serial print --> debugging purpose      
        client.println("POST /arduino HTTP/1.1"); // maybe specify resource
        client.println("Host:192.168.1.84"); // SPECIFY HOST!!!!
        client.print("Content-Length: ");
        client.println(JsonData.length());
        client.println("User-Agent: Arduino/1.0");
        client.println("Accept: application/json");
        Serial.println(JsonData.length());
        client.println("Content-Type: application/json");
        client.println("Connection: close");
        client.println();
        client.println(JsonData);
         
   } 
    
  else // if connection fails
  {
      Serial.println("connection failed");
      Serial.println();
      Serial.println("disconnecting.");
      client.stop();
   }
}


