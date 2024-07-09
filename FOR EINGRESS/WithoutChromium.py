import time
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")

enrollInProgress = False
operationComplete = False

# def run_id_script():
#     global operationComplete
#     try:
#         ser.write("identify \n".encode('utf-8'))
#         while not operationComplete:
#             if ser.in_waiting > 0:
#                 response = ser.readline().decode('utf-8').rstrip()
#                 print(response)
#                 if "Returning" in response:
#                     operationComplete = True
#                     time.sleep(3)
#                     return
#     except KeyboardInterrupt:
#         print("Keyboard interrupt!, Closing communication")
#         ser.close()

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
                    time.sleep(3)
                    return
            elif time.time() - start_time > timeout:
                print("Identification timeout, returning to main loop.")
                return
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

# def run_id_script(timeout=5):
#     global operationComplete
#     start_time = time.time()
#     try:
#         ser.write("identify \n".encode('utf-8'))
#         while not operationComplete:
#             if ser.in_waiting > 0:
#                 while ser.in_waiting <= 0:
#                     response = ser.readline().decode('utf-8').rstrip()
#                     print(response)
#                     if "Returning" in response:
#                         operationComplete = True
#                         time.sleep(3)
#                         return
#             elif time.time() - start_time > timeout:
#                 print("Identification timeout, returning to main loop.")
#                 return
#     except KeyboardInterrupt:
#         print("Keyboard interrupt!, Closing communication")
#         ser.close()




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
                    time.sleep(3)
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

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
                    time.sleep(3)
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

# def run_enroll_script():
#     global enrollInProgress, operationComplete
#     enrollInProgress = True
#     try:
#         ser.write("enroll \n".encode('utf-8'))
#         while not operationComplete:
            
#             if ser.in_waiting > 0:
#                 response = ser.readline().decode('utf-8').rstrip()
#                 print(f"Response: {response}")
#                 if "Returning" in response:
#                     operationComplete = True
#                     time.sleep(3)
#     except KeyboardInterrupt:
#         print("Keyboard interrupt!, Closing communication")
#         ser.close()

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
