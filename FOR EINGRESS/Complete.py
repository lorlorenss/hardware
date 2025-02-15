import subprocess
import time
import RPi.GPIO as GPIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import serial
import re

chromedriver_path = '/usr/bin/chromedriver'

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')  # Required for running as root in Linux
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for running as root in Linux

# Initialize webdriver
driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=chrome_options)

# Open a webpage
driver.get('http://192.168.42.64:4200/landingPage')

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
        if get_current_url() == "http://192.168.1.2:4200/landingPage":
            print("Shutdown canceled.")
            shutdown_triggered = False
            return
        time.sleep(1)
    subprocess.run(['sudo', 'shutdown', 'now'])

def run_id_script(timeout=10):
    global operationComplete
    operationComplete = False  # Reset operationComplete flag
    start_time = time.time()
    try:
        time.sleep(2)
        print("Please press finger")
        time.sleep(2)
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
        print(f"Successfully inputted ID: {verifiedid}")
    except Exception as e:
        print("Error inputting verified ID:", e)

def input_instruction(instruction):
    try:
        input_element = driver.find_element(By.CLASS_NAME, 'hidden-input')
        input_element.send_keys(instruction)
        input_element.send_keys(Keys.ENTER)
        print(f"Successfully inputted instruction: {instruction}")
    except Exception as e:
        print("Error inputting instruction:", e)

try:
    # Lock the door initially
    lock_door()
    time.sleep(3)
    # Main loop
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Emergency exit button pressed, unlocking door...")
            unlock_door()
            time.sleep(10)
            lock_door()
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
                elif current_url.endswith("/confirmation"):
                    print("Running Identify script...")
                    run_id_script()
                elif current_url.endswith("/registration"):
                    print("Running enroll script...")
                    run_enroll_script()  # Run ID.py script to get verified ID
                elif current_url.endswith("/afterLoginPage"):
                    print("Someone Logged In")
                    unlock_door()  # Unlock the door if after login page is open
                elif "/shutdown" in current_url and not shutdown_triggered:
                    shutdown_pi()  # Shutdown Raspberry Pi if /shutdown URL is detected
                    shutdown_triggered = True
                previous_url = current_url

        time.sleep(1)  # Check every 1 second

except KeyboardInterrupt:
    pass  # Do nothing on keyboard interrupt
finally:
    ser.close()
    driver.quit()
