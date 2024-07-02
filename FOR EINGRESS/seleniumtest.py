from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# Path to chromedriver executable
chromedriver_path = '/usr/bin/chromedriver'

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')  # Required for running as root in Linux
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for running as root in Linux

# Initialize webdriver
driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=chrome_options)

# Open YouTube
driver.get('https://www.youtube.com')

# Wait for page to load
time.sleep(5)  # Adjust this delay as needed

# Find the search input element and search for "python"
search_box = driver.find_element(By.NAME, 'search_query')  # Assuming name attribute is 'search_query'
search_box.send_keys('python')
search_box.send_keys(Keys.RETURN)

# Wait for search results to load
time.sleep(5)  # Adjust this delay as needed

# Example: Click on the first video in search results (if needed)
# video_element = driver.find_element(By.CSS_SELECTOR, 'ytd-video-renderer')
# video_element.click()

# Close the browser window
driver.quit()
