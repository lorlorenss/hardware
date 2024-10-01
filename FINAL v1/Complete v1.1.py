import subprocess
import time
import RPi.GPIO as GPIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import serial
import re


chromedriver_path = '/usr/bin/chromedriver'

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')  # Required for running as root in Linux
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for running as root in Linux
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
# Initialize webdriver
driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=chrome_options)

# Open a webpage
driver.get('https://jairoeingressdui.azurewebsites.net/landingPage')

time.sleep(3)

driver.fullscreen_window()

GPIO.setmode(GPIO.BCM)

RELAY_PIN = 18  # GPIO pin for the relay
BUTTON_PIN = 15  # GPIO pin for the button

GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize
ser.reset_input_buffer()
print("Serial OK")

previous_url = None
shutdown_triggered = False  # Flag to track if shutdown has been triggered
enrollInProgress = False
operationComplete = False

def get_current_url():
    try:
        current_url = driver.current_url
        return current_url
    except Exception as e:
        print("Error getting current URL:", e)
        return None

def run_enroll_script():
    global enrollInProgress, operationComplete
    enrollInProgress = True
    operationComplete = False  # Reset operationComplete flag
    try:
        ser.write("enroll \n".encode('utf-8'))
        while not operationComplete:
            if ser.in_waiting > 0:
                instruction = ser.readline().decode('utf-8').rstrip()
                print(instruction)
                
                if "Returning" in instruction:
                    operationComplete = True
                    enrollInProgress = False
                    time.sleep(3)
                else:
                    input_instruction(instruction)
    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

def lock_door():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Door locked")

def unlock_door():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("Door unlocked")

def shutdown_pi():
    global shutdown_triggered
    print("Shutting down Raspberry Pi...")
    for i in range(10, 0, -1):
        print(f"Shutting down in {i} seconds...")
        if get_current_url() == "https://jairoeingressdui.azurewebsites.net/landingPage":
            print("Shutdown canceled.")
            shutdown_triggered = False
            return
        time.sleep(1)
    subprocess.run(['sudo', 'shutdown', 'now'])

def run_id_script(timeout=5):
    global operationComplete
    operationComplete = False  # Reset operationComplete flag
    start_time = time.time()
    try:
        print("Please press finger")
        time.sleep(1)
        ser.write("identify \n".encode('utf-8'))
        while not operationComplete:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(response)  # This should print "ID: <enrollid> Enrolling Successful"
                match = re.search(r'ID:(\d+)', response)
                if match:
                    verifiedid = match.group(1)
                    input_verified_id(verifiedid)  # Use the function to input verified ID
                
                if "Returning" in response:
                    operationComplete = True
                    enrollInProgress = False
                    return

                elif "Finger not found" in response:
                    input_verified_id("Error")

            elif time.time() - start_time > timeout:
                print("Identification timeout, returning to main loop.")
                operationComplete = True
                enrollInProgress = False
                input_verified_id("Timeout")
                return

    except KeyboardInterrupt:
        print("Keyboard interrupt!, Closing communication")
        ser.close()

def input_verified_id(verifiedid):
    try:
        input_element = driver.find_element(By.CLASS_NAME, 'hidden-input')
        input_element.send_keys(verifiedid)
        input_element.send_keys(Keys.ENTER)
        # print(f"Successfully inputted ID: {verifiedid}")
    except Exception as e:
        print("Error inputting verified ID:", e)

def input_instruction(instruction):
    try:
        input_element = driver.find_element(By.CLASS_NAME, 'hidden-input')
        input_element.send_keys(instruction)
        input_element.send_keys(Keys.ENTER)
        # print(f"Successfully inputted instruction: {instruction}")
    except Exception as e:
        print("Error inputting instruction:", e)

def input_DeleteStatus(status):
    try:
        input_element = driver.find_element(By.CLASS_NAME, 'hidden-input')
        input_element.send_keys(status)
        input_element.send_keys(Keys.ENTER)
    except Exception as e:
        print("Error inputting status:", e)

def storeID():
    try:
        # Wait for the <h2> element containing "Fingerprint ID:"
        h2_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Fingerprint ID:')]"))
        )
        
        # Retrieve the text from the <h2> element
        instruction = h2_element.text
        # Optionally, you can print the instruction to verify
        print(f"Instruction displayed: {instruction}")
        
        # Check if the instruction contains "Fingerprint ID:"
        if "Fingerprint ID:" in instruction:
            # Extract the ID from the instruction
            fingerprint_id = extract_fingerprint_id(instruction)
            
            # Send command to the Arduino with the extracted ID
            send_to_arduino(fingerprint_id)
            return
        else:
            print("Instruction does not contain 'Fingerprint ID:'.")
        
    except TimeoutException:
        print("Timeout: Element with 'Fingerprint ID:' not found.")
    except Exception as e:
        print("Error processing instruction:", e)

def extract_fingerprint_id(instruction):
    # Extract the numeric ID from the instruction, assuming it's after "Fingerprint ID: "
    # Example: "Fingerprint ID: 123"
    parts = instruction.split(":")
    if len(parts) == 2:
        return parts[1].strip()  # Trim spaces around the ID
    else:
        return None  # Handle cases where ID extraction fails

def send_to_arduino(fingerprint_id):
    try:
        ser.write(f"StoredID {fingerprint_id}\n".encode('utf-8'))
        print(f"Sent 'StoredID {fingerprint_id}' command to Arduino")
        while True:
            if ser.in_waiting > 0:
                instruction = ser.readline().decode('utf-8').rstrip()
                print(instruction)
                if "Success" in instruction:
                    time.sleep(1)
                    input_DeleteStatus(instruction)
                    return
                elif "Failed" in instruction:
                    time.sleep(1)
                    input_DeleteStatus(instruction)
                    return
    except Exception as e:
        print("Error sending command to Arduino:", e)
        return False

def reboot_pi():
    print("Rebooting Raspberry Pi...")
    for i in range(3, 0, -1):
        print(f"Rebooting in {i} seconds...")
        if get_current_url() == "https://jairoeingressdui.azurewebsites.net/landingPage":
            print("Shutdown canceled.")
            shutdown_triggered = False
            return
        time.sleep(1)
    subprocess.run(['sudo', 'reboot'])

try:
    # Lock the door initially
    lock_door()
    time.sleep(3)
    # Main loop
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            input_instruction("emergency")
            time.sleep(0.2)
            continue

        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').rstrip()
            print(response)
            time.sleep(3)
            break

        current_url = get_current_url()
        if current_url:
            if current_url != previous_url:
                if current_url.endswith("/landingPage"):
                    print("Landing page opened!")
                    lock_door()  # Lock the door if landing page or another page is open
                    if shutdown_triggered:
                        print("Shutdown canceled.")
                        shutdown_triggered = False
                elif current_url.endswith("/delete"):
                    print("Waiting for Fingerprint ID:")
                    storeID()  
                elif current_url.endswith("/confirmation"):
                    print("Running Identify script...")
                    run_id_script()
                elif current_url.endswith("/registration"):
                    print("Running enroll script...")
                    run_enroll_script()
                elif current_url.endswith("/afterLoginPage"):
                    print("Someone Logged In")
                    unlock_door()  # Unlock the door if after login page is open
                elif current_url.endswith("/emergency"):
                    print("Emergency door lock pressed")
                    unlock_door()
                elif current_url.endswith("/welcomeInterns"):
                    print("Intern RFID Tapped")
                    unlock_door()
                elif "/shutdown" in current_url and not shutdown_triggered:
                    shutdown_pi()
                    shutdown_triggered = True
                elif "/reboot" in current_url:
                    reboot_pi()
                previous_url = current_url

        time.sleep(1)  # Check every 1 second

except KeyboardInterrupt:
    pass  # Do nothing on keyboard interrupt
finally:
    ser.close()
    print("Serial connection closed")
    driver.quit()
