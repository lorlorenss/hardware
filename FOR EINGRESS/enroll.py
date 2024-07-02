import serial
import time
import re
import pyautogui
import os

# Configure the serial connection
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")

# Function to simulate keyboard input
def simulate_keyboard_input(text):
    pyautogui.typewrite(text)

# Function to press Enter
def press_enter():
    pyautogui.press('enter')
    
# Actual code:
try:
    while True:
        time.sleep(1)
        #print("Send message to Arduino")
        ser.write("enroll \n".encode('utf-8'))

        while ser.in_waiting <= 0:
            time.sleep(0.01)
        
        response = ser.readline().decode('utf-8').rstrip()
        print(response)  # This should print "ID: <enrollid> Enrolling Successful"

        # Parse the enrollid from the response
        match = re.search(r'ID:(\d+)', response)
        if match:
            verifiedid = match.group(1)
            print(f"Verified Id: {verifiedid}")
            
            simulate_keyboard_input(verifiedid)
            time.sleep(0.1)  # Wait for 100 milliseconds
            press_enter()
            time.sleep(1)
            sys.exit(1)
except KeyboardInterrupt:
    print("Keyboard interrupt!, Closing communication")
    ser.close()


