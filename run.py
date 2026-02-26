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

driver.get("https://krisha.kz/prodazha/kvartiry/almaty/")

# The website krisha.kz is a popular real estate listing site in Kazakhstan, 
# where users can find apartments for sale in Almaty. The script opens this
# website using Selenium WebDriver to prepare for data extraction. This website doesn't
# have blockers and is accessible for scraping, making it a suitable choice for 
# collecting real estate data.