import serial
import time

# Configure the serial connection
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")

# Actual code:
try:
    while True:
        time.sleep(1)
        print("Send message to Arduino")
        ser.write("enroll \n".encode('utf-8'))

        while ser.in_waiting <= 0:
            time.sleep(0.01)
        response = ser.readline().decode('utf-8').rstrip()
        print(response)  # This should print "Enroll process complete"

except KeyboardInterrupt:
    print("Keyboard interrupt!, Closing communication")
    ser.close()
