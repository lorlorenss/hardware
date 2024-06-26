int counter = 0;

void setup() {
  Serial.begin(115200);  // Start serial communication at 115200 baud
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');  // Read until newline
    if (message.indexOf("biometric") != -1) {  // Check if the word "biometric" exists
      runBiometricFunction();  // Run the specific function
    }
  }
}

void runBiometricFunction() {
  String response = "Biometric function executed " + String(counter);
  counter++;
  Serial.println(response);  // Send a response back
}
