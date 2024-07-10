
#define ENROLL_TIME 5000 //milliseconds
#define PRINTS_MAX 200 //200=GT_521F32 3000=GT_521F52

#include <GT_521F.h>

//Uncomment for Software Serial
SoftwareSerial mySerial (4, 5);
GT_521F fps(mySerial); 

//Uncomment for Hardware Serial
//GT_521F fps(Serial1); 

void setup()
{
  delay(5000);
  Serial.begin(9600);
  while(!fps.begin(9600))
  {
    Serial.print(".");
  }
  int openStatus = fps.open(true);
  if(openStatus == NO_ERROR) {
    // Print extra info from SRAM data buffer
    Serial.print("\nDevice information:\n");
    for(uint8_t i=0; i<24; i++) {
      if(fps.dataBuf[i] < 0x10) {
        Serial.print(0x00, HEX);
        Serial.flush();
      }
      Serial.print(fps.dataBuf[i], HEX);
      Serial.flush();
    }
  } else {
    Serial.print("\nInitialization failed!\nstatus: ");
    Serial.print(openStatus, HEX);
    Serial.flush();
  }

}

void loop()
{
  if(Serial.available()!=0)
  {        
    String message = Serial.readStringUntil('\n');

      if (message.indexOf("enroll") != -1) {
     
        uint16_t State = FingerPrintEnrollment();
        if(State==NO_ERROR)
        {
          Serial.print("Add Finger Success ID: ");
          Serial.println(fps.getEnrollCount()-1);
        }
        else
        {
          Serial.print("Add Finger Fail ERROR: ");
          Serial.println(State);
        }

      }
      else if (message.indexOf("identify") != -1) {
          uint16_t openStatus = fps.open(true);
          if(openStatus == NO_ERROR) 
          {
            uint16_t checkLED = fps.cmosLed(true);
            if(checkLED == NO_ERROR)
            { 
              Serial.println("Place finger you want to check on Sensor");
              uint32_t FingerCountTime = millis();
              uint16_t checkFinger = FINGER_IS_NOT_PRESSED;
              while((checkFinger==FINGER_IS_NOT_PRESSED) && ((millis() - FingerCountTime)<ENROLL_TIME))
              {
                delay(100); 
                checkFinger = fps.isPressFinger();                 
              }
              if(checkFinger == FINGER_IS_PRESSED)
              {
                Serial.println("-FINGER IS PRESSED");
                checkFinger = fps.captureFinger();
                if(checkFinger == NO_ERROR)
                {
                  Serial.println("-FINGER CAPTURED");
                  checkFinger = fps.identify();
                  if(checkFinger < PRINTS_MAX)
                  {
                    fps.cmosLed(false);
                    Serial.print("-FINGER FOUND ID: ");
                    Serial.println(checkFinger);
                  }
                  else
                  {
                    Serial.println("-FINGER NOT FOUND");
                  }
                }
                else
                {
                  Serial.println("-FINGER CAPTURE FAILED");
                }
              }
              else
              {
                Serial.print("-FINGER FAIL: ");
                Serial.println(checkFinger,HEX);
              }
            }
            else
            {
              Serial.print("-LED FAIL: ");
              Serial.println(checkLED,HEX);
            }
          } 
          else 
          {
            Serial.print("-Initialization failed!\nstatus: ");
            Serial.print(openStatus, HEX);
            Serial.println();
          }
      }
       else if (message.indexOf("deleteAll") != -1) {
        uint16_t State = fps.deleteAll();
        if(State==NO_ERROR)
        {
          Serial.println("-All Prints Deleted");
        }  
        else
        {
           Serial.print("-Delete Failed: "); 
           Serial.println(State,HEX);    
        }
      }
      else
      {
        Serial.print(check);
        Serial.println("-Option Invalid");

      }
    }
}



uint8_t FingerPrintEnrollment()
{
  uint8_t enrollState = NO_ERROR;
  uint16_t enrollid = 0;
  uint32_t enrollTimeOut = 0;
  enrollState = fps.open(false);
  if(enrollState == NO_ERROR)
  {
    Serial.println("Starting Enrollment");
    enrollState = ID_IS_ENROLLED;
    while (enrollState == ID_IS_ENROLLED)
    {
      enrollState = fps.checkEnrolled(enrollid);
      if (enrollState==ID_IS_ENROLLED) 
      {
        enrollid++;
      }
      else if(enrollState != ID_IS_NOT_ENROLLED)
      {
        Serial.print("ID Error: "); 
        Serial.print(enrollid); 
        Serial.print(" : ");
        Serial.println(enrollState,HEX); 
      }
      delay(1);
    }
    if(enrollState == ID_IS_NOT_ENROLLED)
    {
      Serial.print("ID Cleared: "); 
      Serial.println(enrollid);
      enrollState = fps.enrollStart(enrollid);
      if(enrollState == NO_ERROR)
      {
        enrollState = fps.cmosLed(true);
        if(enrollState==NO_ERROR)
        {
          for(int i = 1;i<4;i++)
          {
            enrollState = fps.cmosLed(true);
            enrollTimeOut = millis();
            Serial.print(i);
            Serial.println(" - Place Same Finger on sensor");
            enrollState = FINGER_IS_NOT_PRESSED;
            while((enrollState != FINGER_IS_PRESSED) && ((millis()-enrollTimeOut)<ENROLL_TIME))
            {
              delay(100);
              enrollState = fps.isPressFinger();
            }                    
            if(enrollState == FINGER_IS_PRESSED)
            {
              Serial.println("FINGER IS PRESSED");
              enrollState = NO_ERROR;
              enrollState = fps.captureFinger(1);
              if(enrollState==NO_ERROR)
              {
                Serial.println("Finger Captured");
                enrollState = fps.enrollFinger(i);
                if(enrollState == NO_ERROR)
                {  
                  Serial.println("Finger Enrolled");
                }
                else
                {
                  Serial.print("Enroll Failed: ");
                  Serial.println(enrollState,HEX);
                }                
              }
              else
              {
                Serial.print("Capture Failed: ");
                Serial.println(enrollState,HEX);
                break;
              }
              enrollTimeOut = millis();
              Serial.println("Remove Finger");
              enrollState = FINGER_IS_PRESSED;
              while((enrollState == FINGER_IS_PRESSED) && ((millis()-enrollTimeOut)<ENROLL_TIME))
              {
                enrollState = fps.isPressFinger();
                delay(5);
              } 
              fps.cmosLed(false);
              if((millis()-enrollTimeOut)>ENROLL_TIME)
              {
                Serial.println("Did not Remove Finger: TimeOut");
                break;
              }
              enrollState = NO_ERROR;              
            }
            else
            {
              Serial.println("Finger pressed TimeOut");
              break;
            }
            fps.cmosLed(false);
            delay(1000);
          } //End of For loop
          
          if(enrollState == NO_ERROR)
          {
            Serial.println("DONE");
          }
        }
      }
      else
      {
        Serial.print("Enrolling Start Failed: "); 
        Serial.println(enrollState,HEX);
      }
    }
    else
    {
      Serial.print("Enrolling ID Fail: "); 
      Serial.println(enrollState,HEX); 
    }
  }
  else
  {
    Serial.print("Enrolling Fail: "); 
    Serial.println(enrollState,HEX); 
  }
  fps.cmosLed(false);
  return enrollState;
}
