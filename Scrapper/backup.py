import csv
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------- CONFIGURATION ----------------- #
# Relative XPaths for details extraction
NAME_XPATH            = ".//div[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1"
PHONE_XPATH_NO_WEBSITE = ".//div[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[5]/button/div/div[2]/div[1]"
ALTERNATE_PHONE_XPATH = ".//div[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[6]/button/div/div[2]/div[1]"
ADDRESS_XPATH         = ".//div[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]/div[1]"
WEBSITE_XPATH         = ".//div[@id='QA0Szd']//div[7]/div[5]/a/div/div[2]/div[1]"

# Relative XPath template for clicking listing cards (starting index 3, then 5, 7, …)
LISTING_XPATH_TEMPLATE = ".//div[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[{}]/div/a"

# ----------------- HELPER FUNCTIONS ----------------- #
def get_field(driver, xpath):
    """
    Wait for an element using XPath and return its text.
    If not found, return "Not found".
    """
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        text = element.text.strip()
        return text if text else "Not found"
    except Exception:
        return "Not found"

def extract_lead_details(driver):
    """
    Extracts lead details concurrently.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_name    = executor.submit(get_field, driver, NAME_XPATH)
        future_website = executor.submit(get_field, driver, WEBSITE_XPATH)
        future_address = executor.submit(get_field, driver, ADDRESS_XPATH)
        
        name    = future_name.result()
        website = future_website.result()
        address = future_address.result()
        
        # Choose phone XPath based on whether a website is found
        phone_xpath = ALTERNATE_PHONE_XPATH if website != "Not found" else PHONE_XPATH_NO_WEBSITE
        phone = get_field(driver, phone_xpath)
    
    return {
        "Company_Name": name,
        "Address": address,
        "Phone": phone,
        "Website": website
    }

# ----------------- MAIN SCRIPT ----------------- #
def main():
    search_query = input("Enter your search query: ")
    try:
        num_leads = int(input("Enter the number of leads to scrape: "))
    except ValueError:
        print("Invalid number provided for leads.")
        return

    # Setup Chrome WebDriver with headless mode
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    
    time.sleep(3)
    
    # Open Google Maps and perform search
    driver.get("https://www.google.com/maps")
    time.sleep(4)
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="searchboxinput"]'))
    )
    search_box.clear()
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    
    # Allow search results to load
    time.sleep(10)
    
    csv_file = "leads.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ["Lead_Index", "Company_Name", "Address", "Phone", "Website"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        file.flush()
        
        # Process listings from the side panel. Listing cards start at index 3 and increase by 2.
        listing_index = 3
        for lead in range(num_leads):
            try:
                listing_xpath = LISTING_XPATH_TEMPLATE.format(listing_index)
                listing_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, listing_xpath))
                )
                listing_element.click()
                time.sleep(3)  # Wait for the sidebar details to load
                
                # Scroll the sidebar to ensure all details load
                sidebar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='QA0Szd']"))
                )
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                time.sleep(2)
                
                details = extract_lead_details(driver)
                details["Lead_Index"] = lead + 1
                writer.writerow(details)
                file.flush()
                print(f"Scraped Lead {lead + 1}: {details}")
                
                # Increment listing index by 2 for next card
                listing_index += 2
                time.sleep(2)
            except Exception as e:
                print(f"Error at lead {lead + 1}: {e}")
                continue
    
    driver.quit()
    print(f"Scraping complete. Data saved to {csv_file}.")

if __name__ == "__main__":
    main()
