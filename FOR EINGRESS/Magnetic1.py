import subprocess
import requests
import json
import time
import RPi.GPIO as GPIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By




chromedriver_path = '/usr/bin/chromedriver'

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')  # Required for running as root in Linux
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for running as root in Linux

# Initialize webdriver
driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=chrome_options)

# Example: Open a webpage
driver.get('https://192.168.42.64.com')
time.sleep(5)  # Adjust this delay as needed

GPIO.setmode(GPIO.BCM)

RELAY_PIN = 18  # GPIO pin for the relay
BUTTON_PIN = 15  # GPIO pin for the button

GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Automatically run 'firefox --remote-debugging-port=9222 --kiosk' in the command prompt=subprocess.Popen(['firefox', '--remote-debugging-port=9222','--kiosk'], shell=False)
#subprocess.Popen(['firefox', '--remote-debugging-port=9222','--kiosk'], shell=False)
#subprocess.Popen(['chromium-browser', '--remote-debugging-port=9222', '--start-fullscreen'], shell=False)
#subprocess.Popen(['chromium-browser', '--remote-debugging-port=9222'], shell=False)
#print("CMD Firefox debugging started!")

previous_url = None
shutdown_triggered = False  # Flag to track if shutdown has been triggered

def get_current_url():
    try:
        # Fetching Firefox's active tab URL using Firefox Remote Debugging Protocol
        response = requests.get('http://127.0.0.1:9222/json')
        response.raise_for_status()
        tabs = json.loads(response.text)
        
        # Extracting the URL of the active tab
        for tab in tabs:
            if tab['url'] != "about:blank":
                return tab['url']
        
        # Return None if no URL is found
        return None
    
    except Exception as e:
        print("Error:", e)
        return None

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

try:
    # Lock the door initially
    lock_door()

    # Main loop
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Emergency exit button pressed, unlocking door...")
            unlock_door()
            time.sleep(10)
            lock_door()
            continue

        current_url = get_current_url()
        if current_url:
            if current_url != previous_url:
                if current_url.endswith("/landingPage"):
                    print("Landing page opened!")
                    lock_door()  # Lock the door if landing page or another page is open
                    if shutdown_triggered:
                        print("Shutdown canceled.")
                        shutdown_triggered = False
                elif current_url.endswith("/afterLoginPage"):
                    subprocess.run(['python3', 'test.py'], capture_output=True, text=True)
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
