import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


#uncomment when it wont fullscreen. replace the step1
# chromium_command = [
#     "chromium-browser",
#     "--remote-debugging-port=9222",
#     "--start-fullscreen",
#     "--user-data-dir=/tmp/chrome_dev"  # Use a separate user data directory
# ]

# # Start Chromium
# subprocess.Popen(chromium_command)

# # Step 1: Start Chromium with Remote Debugging in Fullscreen Mode
subprocess.Popen(['chromium-browser', '--remote-debugging-port=9222', '--start-fullscreen'], shell=False)

# Give Chromium a few seconds to start
time.sleep(5)

# Step 2: Connect Selenium to the Debugging Port
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
chrome_options.add_argument('--no-sandbox')  # Required for running as root in Linux
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for running as root in Linux

# Path to ChromeDriver
chromedriver_path = '/usr/bin/chromedriver'

# Initialize webdriver with Chrome options
driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=chrome_options)

# Step 3: Use Selenium to Navigate to the Landing Page
driver.get('http://192.168.42.64:4200/landingPage')

# Example of interacting with the page
print(driver.title)

# Optional: Close the browser after interaction
# driver.quit()
