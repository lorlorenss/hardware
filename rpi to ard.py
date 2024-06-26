import serial
import time

# Configure the serial connection
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")


#Actual code:
try:
    while True:
        time.sleep(0.01)
        ser.write("Hello from Rpi\n".encode('utf-8'))
       
except KeyboardInterrupt:
    print("Keyboard interrupt!, Closing communication")
    ser.close()
    