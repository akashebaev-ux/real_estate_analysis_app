"""
Real Estate Analysis App

This script:
- Connects to Google Sheets using gspread
- Creates or opens a worksheet named with today's date
- Uses Selenium WebDriver to open a real estate website
- Prepares data for storage in Google Sheets

Selenium is used to automate the browser and collect
real estate data such as prices, locations, and links.
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds3.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('real_estate_analysis_app')

today = datetime.now().strftime("%Y-%m-%d")

# Creates or opens a worksheet in Google Sheets named with today's date.

try:
    TODAY_WS = SHEET.worksheet(today)
except:
    TODAY_WS = SHEET.add_worksheet(
        title=today,
        rows="10000",
        cols="20"
    )

driver = webdriver.Chrome()

MAX_PAGES=10
# max_pages is set to 10 to limit the number of pages scraped for testing purposes.

all_data=[]

page=1

while page<=MAX_PAGES:
    """
    Iterate through Krisha.kz apartment listing pages and collect card data.

    For each page:
        - Open the page using Selenium
        - Find all elements with class 'a-card'
        - Extract header, price, location, link, and full card text
        - Store extracted data in all_data list

    The loop continues until MAX_PAGES is reached.

    Notes
    -----
    Cards missing required elements are skipped.
    """

    url=f"https://krisha.kz/prodazha/kvartiry/almaty/?page={page}"

    driver.get(url)

    print("Page",page)

# The website krisha.kz is a popular real estate listing site in Kazakhstan, 
# where users can find apartments for sale in Almaty. The script opens this
# website using Selenium WebDriver to prepare for data extraction. This website doesn't
# have blockers and is accessible for scraping, making it a suitable choice for 
# collecting real estate data.


    cards = driver.find_elements(By.CLASS_NAME,"a-card")
 
    for card in cards:
        
        try:

            header=card.find_element(By.CLASS_NAME,"a-card__header").text
            price=card.find_element(By.CLASS_NAME,"a-card__price").text
            location=card.find_element(By.CLASS_NAME,"a-card__subtitle").text
            link=card.find_element(By.TAG_NAME,"a").get_attribute("href")

            combined_text=card.text

            all_data.append([
            header,
            price,
            location,
            link,
            combined_text
            ])

        except:
            continue

    page+=1