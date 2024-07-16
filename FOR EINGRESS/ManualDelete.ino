#include "FPS_GT511C3.h"
#include "SoftwareSerial.h"

int counter = 0;
FPS_GT511C3 fps(4, 5); // (Arduino SS_RX = pin 4, Arduino SS_TX = pin 5)
bool enrollInProgress = false;
void setup() {
  Serial.begin(115200);  // Start serial communication at 115200 baud
  fps.Open();
}

int storedID;  // Initialize storedID to -1 or another appropriate default value

void loop() {
  Blink();  // Function to blink an LED or perform any other periodic task
  if (Serial.available() > 0) {  // Check if there is data available to read from serial
    String message = Serial.readStringUntil('\n');  // Read the incoming message until newline character
    // Check for different commands in the received message
    if (message.indexOf("enroll") != -1) {
      Enroll();  // Function to handle enrollment process
    } else if (message.indexOf("identify") != -1) {
      enrollInProgress = true;  // Set a flag indicating identification process is in progress
      Identify();  // Function to handle identification process
    } else if (message.indexOf("deleteAll") != -1) {
      DeleteAll();  // Function to delete all stored biometric data
    } else if (message.indexOf("isIdentifying") != -1) {
      enrollInProgress = true;  // Set a flag indicating identification process is in progress
    } else if (message.startsWith("StoredID")) {
      // Extract the ID from the message
      String idString = message.substring(8);  // Assuming "StoredID " takes 8 characters
      storedID = idString.toInt();  // Convert string to integer and store in storedID
      DeleteFingerprint();
    }
  }
}

// void DeleteFingerprint(){
//   bool existentID = true;
//   existentID = fps.CheckEnrolled(storedID);
//   if (existentID == false){
//     Serial.println("Failed");
//     return;
//   }
//   else{
//   fps.DeleteID(storedID);
//   Serial.println("Success");
//   delay(2000);
//   Serial.println("Returning");
//   return;
//   }

  
// }

void DeleteFingerprint(){
 bool deletedID = false;
 if(fps.DeleteID(storedID) == true){
  Serial.println("Success");
 }
 else if(fps.DeleteID(storedID) == false){
  Serial.println("Failed");
  }
  return;
}

void DeleteAll(){
 fps.Open();
fps.DeleteAll();
Serial.println("Deleted All fingerprints");
Serial.println("Returning");
return;
}

void Enroll() {

fps.Open();
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
            fps.Close();
            enrollInProgress = false;
            return;
          }
          Serial.print("ID: ");
          Serial.println(enrollid); // Display the enrolled ID
          Serial.print("Enrolling Successful");
          fps.Close();
          enrollInProgress = false;
          Serial.print("Returning");
          return;
        } else {
          Serial.print("Enrolling Failed with error code: ");
          Serial.println(iret);
          Serial.print("Returning");
          fps.Close();
          enrollInProgress = false;
          return;
        }
      } 
      else Serial.println("Failed to capture third finger");
      Serial.print("Returning");
          fps.Close();
          enrollInProgress = false;
          return;
    } 
    else Serial.println("Failed to capture second finger");
    Serial.print("Returning");
          fps.Close();
          enrollInProgress = false;
          return;
  } 
  else Serial.println("Failed to capture first finger");
  Serial.print("Returning");
          fps.Close();
          enrollInProgress = false;
          return;


}

void Identify(){
   fps.Open();
  fps.SetLED(true);
  if (fps.IsPressFinger())
  {
    fps.CaptureFinger(false);
    int id = fps.Identify1_N();
    if (id <200) 
    {
      Serial.print("ID:");
      Serial.println(id);
      Serial.println("Returning");
      return;
    }
    else
    {//if unable to recognize
      Serial.println("Finger not found");
      Serial.println("Returning");
      return;
    }
  }
  else
  {
    Serial.println("Please press finger");
  }
  delay(100);
}

void Blink(){
   fps.Open();
        fps.SetLED(false);
        delay(1000);
        fps.SetLED(true);
        delay(1000);
}
