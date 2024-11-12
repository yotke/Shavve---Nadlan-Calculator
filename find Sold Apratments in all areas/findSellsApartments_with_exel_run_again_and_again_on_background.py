import signal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# List to store row data for Excel
data_list = []
output_file = "output.xlsx"

# Initialize the Chrome WebDriver in headless mode
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Runs Chrome in headless mode
options.add_argument("--disable-gpu")  # Disables GPU for headless Chrome
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

def save_data_to_excel():
    """Save collected data to an Excel file on exit."""
    df = pd.DataFrame(data_list, columns=['Date', 'Address', 'Gush', 'Type', 'Rooms', 'Floor', 'Size', 'Price', 'Trend', 'Additional'])
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Data has been saved to {output_file}")

def handle_exit(signum, frame):
    """Handle process exit, save data to Excel, and quit driver."""
    print("Closing and saving data...")
    save_data_to_excel()
    driver.quit()
    exit(0)

# Attach signal handlers for termination signals
signal.signal(signal.SIGINT, handle_exit)  # Handles Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # Handles termination

try:
    # Navigate to the website
    driver.get("https://www.nadlan.gov.il/")
    
    # Wait for the search box to be present
    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "SearchString"))
    )
    search_box.send_keys("תל אביב יפו")
    
    # Find the submit button by id and click it
    submit_button = driver.find_element(By.ID, "submitSearchBtn")
    submit_button.click()

    # Wait for the initial table to load
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "tableRow"))
    )

    previous_html = ""
    scrolling = True
    retries = 0  # To avoid infinite scrolling if no new data loads

    while scrolling and retries < 5:
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Locate and extract information within specified divs
        view_container = soup.find("div", {"class": "viewContainer", "ui-view": "MainView"})
        table_content = view_container.find("div", {"class": "tableBody"}) if view_container else None

        # Extract table rows and add to data list
        if table_content:
            rows = table_content.find_all("div", {"class": "tableRow"})
            for row in rows:
                columns = row.find_all("div", {"class": "tableCol"})
                row_data = [col.get_text(strip=True) for col in columns]
                data_list.append(row_data)
                print("Row Data:", row_data)  # Print each row for confirmation

        # Scroll down to load more rows
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new rows to load
        time.sleep(5)  # Adjust this if loading takes longer

        # Check if new content is loaded
        current_html = driver.page_source
        if current_html == previous_html:
            retries += 1  # Increment retry counter if no new content is loaded
        else:
            retries = 0  # Reset retries if new content is loaded
            previous_html = current_html

        # Stop scrolling if no new data is loaded after several attempts
        scrolling = retries < 5

finally:
    # Ensure data is saved and driver is quit on exit
    handle_exit(None, None)
