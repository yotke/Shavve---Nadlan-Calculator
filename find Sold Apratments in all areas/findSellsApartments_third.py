from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

try:
    # Navigate to the website
    driver.get("https://www.nadlan.gov.il/")
    
    # Find the search bar by id and enter "תל אביב יפו"
    search_box = driver.find_element("id", "SearchString")
    search_box.send_keys("תל אביב יפו")
    
    # Find the submit button by id and click it
    submit_button = driver.find_element("id", "submitSearchBtn")
    submit_button.click()

    # Wait for the initial table to load
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "tableRow"))
    )

    previous_html = ""
    scrolling = True
    
    while scrolling:
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Locate and extract information within specified divs
        view_container = soup.find("div", {"class": "viewContainer", "ui-view": "MainView"})
        map_description = view_container.find("div", {"class": "mapDescription"}) if view_container else None
        table_content = view_container.find("div", {"class": "tableBody"}) if view_container else None

        # Extract details from map description and table content
        if map_description:
            print("Map Description:", map_description.get_text(strip=True))
        
        if table_content:
            rows = table_content.find_all("div", {"class": "tableRow"})
            for row in rows:
                columns = row.find_all("div", {"class": "tableCol"})
                row_data = [col.get_text(strip=True) for col in columns]
                print("Row Data:", row_data)

        # Scroll down to load more rows
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new rows to load
        time.sleep(3)  # Adjust this if loading takes longer

        # Check if new content is loaded
        current_html = driver.page_source
        if current_html == previous_html:
            scrolling = False  # Stop if no new content is loaded
        else:
            previous_html = current_html

finally:
    # Close the driver
    driver.quit()
