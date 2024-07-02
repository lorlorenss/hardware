#include <FPS_GT511C3.h>
#include "FPS_GT511C3.h"
#include "SoftwareSerial.h"


FPS_GT511C3 fps(4, 5); // (Arduino SS_RX = pin 4, Arduino SS_TX = pin 5)


void setup()
{
	Serial.begin(9600); //set up Arduino's hardware serial UART
	delay(100);
	fps.Open();         //send serial command to initialize fps
	fps.SetLED(true);   //turn on LED so fps can see fingerprint
}

void loop()
{
	// Identify fingerprint test
	if (fps.IsPressFinger())
	{
		fps.CaptureFinger(false);
		int id = fps.Identify1_N();

		if (id <200) //<- change id value depending model you are using
		{//if the fingerprint matches, provide the matching template ID
			Serial.print("Verified ID:");
			Serial.println(id);
		}
		else
		{//if unable to recognize
			Serial.println("Finger not found");
		}
	}
	else
	{
		Serial.println("Please press finger");
	}
	delay(100);
}
