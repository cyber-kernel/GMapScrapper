import csv
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------- CONFIGURATION ----------------- #
BASE_XPATH = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[{}]"
SCROLLABLE_XPATH = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'

# ----------------- GLOBAL VARIABLE ----------------- #
stop_scraping = False  # Flag to stop scraping when user presses Q

# ----------------- HELPER FUNCTIONS ----------------- #
def get_field_text(element, xpath):
    """ Extracts text from an element if present, otherwise returns 'Not found' """
    try:
        sub_element = element.find_element(By.XPATH, xpath)
        text = sub_element.text.strip()
        return text if text else "Not found"
    except Exception:
        return "Not found"

def get_element_href(element, xpath):
    """ Extracts href attribute from an element if present, otherwise returns 'Not found' """
    try:
        sub_element = element.find_element(By.XPATH, xpath)
        return sub_element.get_attribute("href") or "Not found"
    except Exception:
        return "Not found"

def extract_card_details(card_element):
    """ Extracts business details from a single search result card """
    try:
        name_xpath = ".//div[contains(@class, 'qBF1Pd')]"  # Business name
        phone_xpath = ".//span[contains(text(), 'Phone')]/following-sibling::span"  # Phone number
        website_xpath = ".//a[contains(@aria-label, 'Website')]"  # Website link

        name = get_field_text(card_element, name_xpath)
        phone = get_field_text(card_element, phone_xpath)
        website = get_element_href(card_element, website_xpath)

        return {
            "Company_Name": name,
            "Phone": phone,
            "Website": website
        }
    except Exception as e:
        print("Error extracting details:", e)
        return None

def scroll_scrollable_element(driver):
    """ Scrolls the scrollable element using JavaScript """
    try:
        scrollable = driver.find_element(By.XPATH, SCROLLABLE_XPATH)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable)
        time.sleep(2)  # Allow time for new content to load
        return True
    except Exception as e:
        print("Error scrolling:", e)
        return False

def listen_for_quit():
    """ Listens for user input to quit scraping """
    global stop_scraping
    while True:
        key = input().strip().lower()
        if key == 'q':
            stop_scraping = True
            break

# ----------------- MAIN SCRIPT ----------------- #
def main():
    global stop_scraping

    search_query = input("Enter your search query: ")
    file_name = input("Enter the CSV file name: ")

    # Ask the user how they want to filter the results
    print("\nChoose the type of leads to scrape:")
    print("1. Only leads WITHOUT a website")
    print("2. Only leads WITH a website")
    print("3. Scrape all leads (with & without a website)")
    
    try:
        filter_choice = int(input("Enter your choice (1/2/3): "))
        if filter_choice not in [1, 2, 3]:
            print("Invalid choice. Exiting.")
            return
    except ValueError:
        print("Invalid input. Exiting.")
        return

    try:
        num_leads = int(input("Enter the number of leads to scrape: "))
    except ValueError:
        print("Invalid number provided for leads.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # Run in headless mode for better performance
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

    # Wait for results to load
    time.sleep(5)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "QA0Szd"))
    )
    
    # Start the listener thread
    quit_listener = threading.Thread(target=listen_for_quit, daemon=True)
    quit_listener.start()
    
    results = []
    lead_count = 0  # Track leads that match the filter

    while lead_count < num_leads and not stop_scraping:
        try:
            # Find all visible cards
            cards = driver.find_elements(By.XPATH, BASE_XPATH.format('*'))

            for card in cards:
                if stop_scraping or lead_count >= num_leads:
                    break

                details = extract_card_details(card)

                if details:
                    # Apply user-selected filtering
                    if (
                        (filter_choice == 1 and details["Website"] == "Not found") or
                        (filter_choice == 2 and details["Website"] != "Not found") or
                        (filter_choice == 3)
                    ):
                        lead_count += 1
                        details["Lead_Index"] = lead_count
                        results.append(details)
                        print(f"Scraped Lead {lead_count}: {details}")
            
            # Scroll to load more results
            if not scroll_scrollable_element(driver):
                break

        except Exception as e:
            print(f"Error scraping leads: {e}")
            break

    # Save to CSV
    with open(file_name, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Lead_Index", "Company_Name", "Phone", "Website"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    driver.quit()
    print(f"Scraping complete. Data saved to {file_name}.")

if __name__ == "__main__":
    main()
