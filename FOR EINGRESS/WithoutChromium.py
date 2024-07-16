import time
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")

enrollInProgress = False
operationComplete = False

def run_id_script(timeout=10):
    global operationComplete
    start_time = time.time()
    try:
        time.sleep(2)
        print("Please press finger")
        time.sleep(2)
        ser.write("identify \n".encode('utf-8'))
        while not operationComplete:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(response)
                if "Returning" in response:
                    operationComplete = True
                    enrollInProgress = False
                    return
            elif time.time() - start_time > timeout:
                print("Identification timeout, returning to main loop.")
                return
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()


def run_deleteAll_script():
    global operationComplete
    try:
        ser.write("deleteAll \n".encode('utf-8'))
        while not operationComplete:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(response)
                if "Returning" in response:
                    operationComplete = True
                    enrollInProgress = False
                    time.sleep(3)
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

def run_deleteID_script():
    global operationComplete
    
    fingerprint_id = input("Fingerprint ID to delete: ")
    try:
        ser.write(f"StoredID {fingerprint_id}\n".encode('utf-8'))
        print(f"Sent 'StoredID {fingerprint_id}' command to Arduino")
        while not operationComplete:
            if ser.in_waiting > 0:
                instruction = ser.readline().decode('utf-8').rstrip()
                print(instruction)
                if "Success" in instruction:
                    time.sleep(1)
                    return
                elif "Failed" in instruction:
                    time.sleep(1)
                    return
                else:
                    print(instruction)
    except Exception as e:
        print("Error sending command to Arduino:", e)
        return False


def run_enroll_script():
    global enrollInProgress, operationComplete
    enrollInProgress = True
    try:
        ser.write("enroll \n".encode('utf-8'))
        while not operationComplete:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(response)
                if "Returning" in response:
                    operationComplete = True
                    enrollInProgress = False
                    
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()


def handle_serial_input(input_char):
    global enrollInProgress, operationComplete
    operationComplete = False  # Reset the operation complete flag
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
        if not enrollInProgress:
            run_deleteID_script()
    else:
        print("Invalid input")

def display_choices():
    print("Choose an option:")
    print("1: Enroll")
    print("2: Identify")
    print("3: Delete All")
    print("4: Delete fingerprint:")


try:
    time.sleep(3)
    while True:
        display_choices()
        if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(response)
                time.sleep(3)
                break
        else:
            manual_input = input("Enter your choice (1-4): ").strip()
            if manual_input:
                handle_serial_input(manual_input)
except KeyboardInterrupt:
    pass
finally:
    ser.close()
    print("Serial connection closed")
