# GMapScrapper

GMapScrapper is a Python-based web scraper that extracts business details such as company name, phone number, and website from Google Maps search results using Selenium.

## Features
- Automates Google Maps search and extracts business details
- Saves the extracted data into a CSV file
- Scrolls through search results to fetch multiple leads
- Uses Selenium for browser automation

## Requirements
Ensure you have the following installed:
- Python 3.x
- Google Chrome
- ChromeDriver (compatible with your Chrome version)
- Required Python packages

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/cyber-kernel/GMapScrapper.git
   cd GMapScrapper
   ```

2. Create and activate a virtual environment (recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```sh
   python scraper.py
   ```
2. Enter the search query when prompted (e.g., "restaurants in New York").
3. Enter the number of leads to scrape.
4. The extracted data will be saved to `leads.csv`.

## Configuration
You can modify the `BASE_XPATH` in `scraper.py` to adapt to potential Google Maps changes.

## Troubleshooting
- If the script does not scroll properly, ensure your ChromeDriver is updated.
- If Google detects automation, consider adding a delay (`time.sleep`) or using proxies.

## License
This project is licensed under the MIT License.

## Contributing
Feel free to fork the project and submit a pull request with improvements!

## Author
[Cyber Kernel](https://github.com/cyber-kernel)

