import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup Chrome WebDriver
driver = webdriver.Chrome()
driver.get("https://www.google.com/maps")
time.sleep(5)  # Adjust sleep time as necessary to ensure page loads

# Define the XPath for the scrollable element
scroll_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'

# Locate the element using the provided XPath
element = driver.find_element(By.XPATH, scroll_xpath)

# Get and print the initial scrollTop value
initial_scrollTop = driver.execute_script("return arguments[0].scrollTop;", element)
print("Initial scrollTop:", initial_scrollTop)

# Scroll to the bottom of the element
driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", element)
time.sleep(3)  # Wait a few seconds to observe the scroll

# Get and print the new scrollTop value
final_scrollTop = driver.execute_script("return arguments[0].scrollTop;", element)
print("Final scrollTop:", final_scrollTop)

driver.quit()
