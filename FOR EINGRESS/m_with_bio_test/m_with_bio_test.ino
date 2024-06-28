#include "FPS_GT511C3.h"
#include "SoftwareSerial.h"

int counter = 0;
FPS_GT511C3 fps(4, 5); // (Arduino SS_RX = pin 4, Arduino SS_TX = pin 5)

void setup() {
  Serial.begin(115200);  // Start serial communication at 115200 baud
  fps.Open();
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');  // Read until newline
    if (message.indexOf("enroll") != -1) {  // Check if the word "biometric" exists
      Enroll();  // Run the specific function
    } else if (message.indexOf("identify") != -1) {  // Check if the word "enroll" exists
      Identify();  // Run the specific function
    }
    else if (message.indexOf("blink") != -1) {  // Check if the word "enroll" exists
      Blink();  // Run the specific function
    }
  }
}

void DeleteAll(){
fps.DeleteAll();
Serial.println("Deleted All fingerprints");
}


void runBiometricFunction() {
  String response = "Biometric function executed " + String(counter);
  counter++;
  Serial.println(response);  // Send a response back
}

void Enroll() {
  // Enroll test
  fps.SetLED(true); // turn on the LED inside the fps

  // find open enroll id
  int enrollid = 0;
  bool usedid = true;
  while (usedid == true) {
    usedid = fps.CheckEnrolled(enrollid);
    if (usedid == true) enrollid++;
  }
  fps.EnrollStart(enrollid);

  // enroll
  Serial.print("Press finger to Enroll #");
  Serial.println(enrollid);
  while (fps.IsPressFinger() == false) delay(100);
  bool bret = fps.CaptureFinger(true);
  int iret = 0;
  if (bret != false) {
    Serial.println("Remove finger");
    fps.Enroll1();
    while (fps.IsPressFinger() == true) delay(100);
    Serial.println("Press same finger again");
    while (fps.IsPressFinger() == false) delay(100);
    bret = fps.CaptureFinger(true);
    if (bret != false) {
      Serial.println("Remove finger");
      fps.Enroll2();
      while (fps.IsPressFinger() == true) delay(100);
      Serial.println("Press same finger yet again");
      while (fps.IsPressFinger() == false) delay(100);
      bret = fps.CaptureFinger(true);
      if (bret != false) {
        Serial.println("Remove finger");
        iret = fps.Enroll3();
        if (iret == 0) {
          // Enrollment was successful, print the ID
          int id = fps.Identify1_N();
          if (id < 200) {  // Change id value depending on the model you are using
            // if the fingerprint matches, provide the matching template ID
            Serial.print("Verified ID: ");
            Serial.println(id);
          }
          Serial.print("ID: ");
          Serial.println(enrollid); // Display the enrolled ID
          Serial.print("Enrolling Successful");
        } else {
          Serial.print("Enrolling Failed with error code: ");
          Serial.println(iret);
        }
      } else Serial.println("Failed to capture third finger");
    } else Serial.println("Failed to capture second finger");
  } else Serial.println("Failed to capture first finger");
}

void Identify(){
  fps.SetLED(true);
  if (fps.IsPressFinger())
  {
    fps.CaptureFinger(false);
    int id = fps.Identify1_N();
    
       /*Note:  GT-521F52 can hold 3000 fingerprint templates
                GT-521F32 can hold 200 fingerprint templates
                 GT-511C3 can hold 200 fingerprint templates. 
                GT-511C1R can hold 20 fingerprint templates.
       Make sure to change the id depending on what
       model you are using */
    if (id <200) //<- change id value depending model you are using
    {//if the fingerprint matches, provide the matching template ID
      Serial.print("ID:");
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

void Blink(){
  Serial.println("blink function started");
  while (true){
  fps.SetLED(true);
  delay(1000);
  fps.SetLED(false);
  delay(1000);
  }
 
}