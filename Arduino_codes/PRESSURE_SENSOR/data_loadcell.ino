/*AMI 2018 YSDI
 
 -This function has to decide if the Arduino has to send a zero or a one to the raspberry

*/
 
#include "HX711.h"  //You must have this library in your arduino library folder
 
#define DOUT  3
#define CLK  2
#define N 4
HX711 scale(DOUT, CLK);

// Functions' prototypes
void communicate_data(void);
 
//Change this calibration factor as per your load cell once it is found you many need to vary it in thousands
float calibration_factor = 336355 ;  
float reading[N];
int count=0;
int flag;//this variable is used as  a flag: =1 means that a variation wrt the threshold has been detected; =0 means that nothing has benn detected 
//=============================================================================================
//                         SETUP
//=============================================================================================

   
void setup() {
	
  Serial.begin(9600);
  Serial.println("HX711 Calibration");
  Serial.println("Remove all weight from scale");
  Serial.println("After readings begin, place known weight on scale");
  Serial.println("Press a,s,d,f to increase calibration factor by 10,100,1000,10000 respectively");
  Serial.println("Press z,x,c,v to decrease calibration factor by 10,100,1000,10000 respectively");
  Serial.println("Press t for tare");
  scale.set_scale();
  scale.tare(); //Reset the scale to 0
 
  long zero_factor = scale.read_average(); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);
  
  for(i=0;i<N;i++)
  {
	 reading[i] = 0;
  }

}
 
//=============================================================================================
//                         LOOP
//=============================================================================================
void loop() {
 
  scale.set_scale(calibration_factor); //Adjust to this calibration factor
 
  Serial.print("Reading: ");
  Serial.print(scale.get_units(), 3);
  Serial.print(" kg"); //Change this to kg and re-adjust the calibration factor if you follow SI units like a sane person
  Serial.print(" calibration_factor: ");
  Serial.print(calibration_factor);
  Serial.println();
 
reading[count]= scale.get_units();    
if (count == (N-1))
	{ //we want to sample N values
      communicate_data();
	  if (flag == 1)
	  {
		serial.print(flag)//SEND A 1 TO THE RASPBERRY
	  }
	  count=-1;//resetting the counter variable
	}
count++;
 
  if(Serial.available())
  {
    char temp = Serial.read();
    if(temp == '+' || temp == 'a')
      calibration_factor += 10;
    else if(temp == '-' || temp == 'z')
      calibration_factor -= 10;
    else if(temp == 's')
      calibration_factor += 100;  
    else if(temp == 'x')
      calibration_factor -= 100;  
    else if(temp == 'd')
      calibration_factor += 1000;  
    else if(temp == 'c')
      calibration_factor -= 1000;
    else if(temp == 'f')
      calibration_factor += 10000;  
    else if(temp == 'v')
      calibration_factor -= 10000;  
    else if(temp == 't')
      scale.tare();  //Reset the scale to zero
  }
  delay(3500);
}
//=============================================================================================
//Defining communicate_data function
void communicate_data()
{
	float threshold =0.010;//THIS HAS TO BE CHECKED IN LBA TO GET SOME REASONABLE VALUES
	for(i=0;i<N-1;i++){
	if((abs(reading[i]-reading[i+1]))>threshold)
	{
		flag=1;
		return;
	}
	else
	{
		flag=0;	
	}
	}
	return;	
}





















