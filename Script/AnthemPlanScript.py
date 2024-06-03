from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import requests

# Set up the web driver using WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the webpage
driver.get('https://shop.anthem.com/medicare/shop/landing?brand=ABCBS')

try:
    # Enter the ZIP code
    zip_code_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'oss-text-zip-2__input'))
    )
    zip_code_input.send_keys('10024')
    zip_code_input.send_keys(Keys.RETURN)

    # Wait for the ZIP code input to be processed
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.psActiveOption'))
    )

    # Wait for the "View All Plans" button to be clickable
    view_all_plans_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-analytics="viewAllPlansButton"]'))
    )
    view_all_plans_button.click()

    # Add a delay to ensure the data is loaded
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
    )

    # Click the "View Plan Documents" button
    view_plan_documents_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[aria-label="View Plan Documents for Anthem Veteran Select (HMO)"]'))
    )
    view_plan_documents_button.click()

    # Click the "Plan Details" button
    plan_details_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.wcs-ec-heading-content'))
    )
    plan_details_button.click()

    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    # Find the Evidence of Coverage link
    evidence_of_coverage_link = None
    for link in soup.find_all('a', class_='title'):
        if 'Evidence of Coverage' in link.get_text():
            evidence_of_coverage_link = link.get('href')
            break

    # Print the Evidence of Coverage link
    if evidence_of_coverage_link:
        print(f"Evidence of Coverage URL: {evidence_of_coverage_link}")
    else:
        print("Evidence of Coverage document not found.")

finally:
    # Close the web driver
    driver.quit()
