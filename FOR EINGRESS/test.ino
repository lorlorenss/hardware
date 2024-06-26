int counter = 0;
#include "FPS_GT511C3.h"
#include "SoftwareSerial.h"
FPS_GT511C3 fps(4, 5); // (Arduino SS_RX = pin 4, Arduino SS_TX = pin 5)

void setup() {
  Serial.begin(115200);  // Start serial communication at 115200 baud
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');  // Read until newline
    if (message.indexOf("biometric") != -1) {  // Check if the word "biometric" exists
      runBiometricFunction();  // Run the specific function
    }
    else if (message.indexOf("enroll") != -1) {  // Check if the word "enroll" exists
      Enroll();  // Run the specific function
    }
  }
}

void runBiometricFunction() {
  String response = "Biometric function executed " + String(counter);
  counter++;
  Serial.println(response);  // Send a response back
}

void Enroll() {
  // Enroll test

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

  fps.SetLED(true); // turn on the LED inside the fps
  delay(100);
  fps.SetLED(false); // turn off the LED inside the fps
  delay(100);
  if (bret != false) {
    fps.SetLED(true); // turn on the LED inside the fps
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
          Serial.println("Enrolling Successful");
        } else {
          Serial.print("Enrolling Failed with error code:");
          Serial.println(iret);
        }
      } else Serial.println("Failed to capture third finger");
    } else Serial.println("Failed to capture second finger");
  } else Serial.println("Failed to capture first finger");

  // Send completion message
  Serial.println("Enroll process complete");
}
