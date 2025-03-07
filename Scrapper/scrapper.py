import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------- CONFIGURATION ----------------- #
BASE_XPATH = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[{}]/div/div[2]/div[4]/"
CSV_FILE = "leads.csv"
# XPath of the scrollable container (as tested in DevTools)
SCROLLABLE_XPATH = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'

# ----------------- HELPER FUNCTIONS ----------------- #
def get_field_text(driver, xpath):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        text = element.text.strip()
        return text if text else "Not found"
    except Exception:
        return "Not found"

def get_element_href(driver, xpath):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        href = element.get_attribute("href")
        return href if href else "Not found"
    except Exception:
        return "Not found"

def extract_card_details(driver, card_index):
    current_base = BASE_XPATH.format(card_index)
    website_xpath = current_base + "div[2]/div[1]/a"
    phone_xpath   = current_base + "div[1]/div/div/div[2]/div[4]/div[2]/span[2]/span[2]"
    name_xpath    = current_base + "div[1]/div/div/div[2]/div[1]/div[2]"
    
    name = get_field_text(driver, name_xpath)
    phone = get_field_text(driver, phone_xpath)
    website = get_element_href(driver, website_xpath)
    
    return {
        "Company_Name": name,
        "Phone": phone,
        "Website": website
    }

def scroll_scrollable_element(driver):
    """
    Scrolls the scrollable element by setting its scrollTop to its scrollHeight.
    """
    try:
        scrollable = driver.find_element(By.XPATH, SCROLLABLE_XPATH)
        # Execute JS to scroll the element to the bottom
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable)
        print("Scrolled the scrollable element using JS.")
        time.sleep(2)  # Allow time for new content to load
    except Exception as e:
        print("Error scrolling scrollable element:", e)

# ----------------- MAIN SCRIPT ----------------- #
def main():
    search_query = input("Enter your search query: ")
    try:
        num_leads = int(input("Enter the number of leads to scrape: "))
    except ValueError:
        print("Invalid number provided for leads.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get("https://www.google.com/maps")
    time.sleep(3)
    
    # Enter search query
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchboxinput"))
    )
    search_box.clear()
    search_box.send_keys(search_query)
    time.sleep(2)  # Allow input to register

    # Press ENTER and click the search button
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    search_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "searchbox-searchbutton"))
    )
    search_button.click()

    # Wait for results to load
    time.sleep(5)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "QA0Szd"))
    )
    
    results = []
    listing_index = 3  # Starting card index
    
    for lead in range(num_leads):
        try:
            details = extract_card_details(driver, listing_index)
            details["Lead_Index"] = lead + 1
            results.append(details)
            print(f"Scraped Lead {lead + 1}: {details}")
            listing_index += 2
            time.sleep(2)
            
            # After every 5 leads, scroll the scrollable element using JS
            if (lead + 1) % 5 == 0:
                print("Scrolling the scrollable element...")
                scroll_scrollable_element(driver)
        except Exception as e:
            print(f"Error at lead {lead + 1}: {e}")
            listing_index += 2
            continue

    # Save to CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Lead_Index", "Company_Name", "Phone", "Website"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    driver.quit()
    print(f"Scraping complete. Data saved to {CSV_FILE}.")

if __name__ == "__main__":
    main()

# ----------------- END OF SCRIPT ----------------- #