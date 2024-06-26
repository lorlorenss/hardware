int counter = 0;

void setup() {
  Serial.begin(115200);  // Start serial communication at 9600 baud
}

void loop() {
if(Serial.available()>0){
  String message = Serial.readStringUntil('\n');
  message = message + " " +String(counter) + "Hello from arduino" 
  +" "+String(counter) ;
  counter++;
  Serial.println(message);
}
}
