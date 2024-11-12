from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()  # No need to specify path if chromedriver is in /usr/local/bin

try:
    # Navigate to the website
    driver.get("https://www.nadlan.gov.il/")
    
    # Find the search bar by id and enter "תל אביב יפו"
    search_box = driver.find_element("id", "SearchString")
    search_box.send_keys("תל אביב יפו")
    
    # Find the submit button by id and click it
    submit_button = driver.find_element("id", "submitSearchBtn")
    submit_button.click()

    # Wait for the table to load by waiting for an element in the table to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tableRow"))
    )

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

finally:
    # Close the driver
    driver.quit()
