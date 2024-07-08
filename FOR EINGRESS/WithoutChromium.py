import time
import serial
import re

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")

enrollInProgress = False

def run_id_script():
    try:
        while True:
            time.sleep(1)
            ser.write("identify \n".encode('utf-8'))

            while ser.in_waiting <= 0:
                time.sleep(0.01)
            
            response = ser.readline().decode('utf-8').rstrip()
            print(response)  # This should print "ID: <enrollid> Enrolling Successful"

            # Parse the enrollid from the response
            match = re.search(r'ID:(\d+)', response)
            break

    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

def run_deleteAll_script():
    try:
        while True:
            time.sleep(1)
            ser.write("deleteAll \n".encode('utf-8'))

            while ser.in_waiting <= 0:
                time.sleep(0.01)
            
            response = ser.readline().decode('utf-8').rstrip()
            print(response)  # This should print "ID: <enrollid> Enrolling Successful"

            # Parse the enrollid from the response
            match = re.search(r'ID:(\d+)', response)
            break
            

    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

def run_enroll_script():
    global enrollInProgress
    enrollInProgress = True
    try:
        while True:
            time.sleep(1)
            ser.write("enroll \n".encode('utf-8'))
            while ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(f"Response: {response}")
                if "Returning" in response:
                    print("Enroll completed")
                    enrollInProgress = False
                    time.sleep(3)
                    return
                elif "Failed" in response:
                    print("Enrollment failed")
                    enrollInProgress = False
                    time.sleep(3)
                    return
                elif "/landingPage" in response or "/registration" in response:
                    print("Unexpected page redirection")
                    enrollInProgress = False
                    time.sleep(3)
                    return
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()



def handle_serial_input(input_char):
    global enrollInProgress
    if input_char == '1':
        if not enrollInProgress:
            run_enroll_script()
        else:
            print("Enrollment already in progress")
    elif input_char == '2':
        if not enrollInProgress:
            run_id_script()
    elif input_char == '3':
        if not enrollInProgress:
            run_deleteAll_script()
    elif input_char == '4':
        enrollInProgress = False
        print("Setting enroll in progress to false")
    else:
        print("Invalid input")

def display_choices():
    print("Choose an option:")
    print("1: Enroll")
    print("2: Identify")
    print("3: Delete All")
    print("4: Reset Enroll Status")

try:
    # Main loop
    while True:
        display_choices()
        
        # Check if there's input from serial
        if ser.in_waiting > 0:
            input_char = ser.read().decode('utf-8').strip()
            handle_serial_input(input_char)
        else:
            # If no serial input, wait for manual input
            manual_input = input("Enter your choice (1-4): ").strip()
            if manual_input:
                handle_serial_input(manual_input)

except KeyboardInterrupt:
    pass  # Do nothing on keyboard interrupt
finally:
    ser.close()
    print("Serial connection closed")
