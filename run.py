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


# Selenium is a powerful tool for web scraping and browser automation. 
# In this project, Selenium is used to navigate to the real estate listing website.

import pandas as pd
import numpy as np

# Pandas helps me organize and analyze my scraped data easier. 
# In my project, pandas turns raw Selenium data into a clean table.

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

"""
Creates a Pandas DataFrame from scraped real estate data.

Each row represents one flat listing with:
- header (title)
- price
- location
- link
- combined_text
"""
df = pd.DataFrame(
all_data,
columns=[
"header",
"price",
"location",
"link",
"combined_text"
]
)

"""
The code belowe: extract the number of rooms from the flat header and convert it to numeric format.
"""

df["rooms"] = df["header"].str.extract(
    r"(\d+)\s*[- ]?\s*ком"
)

# () - Extract this part
# \d+ - One or more digits (1, 2, 10, etc.)
# \s* - Optional whitespace
# [- ]? - Optional separator (space or dash)
# ком - The word "ком" (short for "комната" meaning "room")

df["rooms"] = pd.to_numeric(
    df["rooms"],
    errors="coerce"
)

# errors="coerce" converts non-numeric values to NaN, which is useful for filtering later.

if rooms_input:

    df = df[
        df["rooms"] == int(rooms_input)
    ]

"""
Remove duplicate flat listings based on the link column.
Ensures each property appears only once in the dataset.
"""
df = df.drop_duplicates(subset=["link"])




"""
Clean and convert price data.

This code:
1. Removes all non-numeric characters from the 'price' column
   (such as spaces, currency symbols, and text).
2. Stores the cleaned values in a new column called 'price_clean'.
3. Converts the cleaned prices into numeric format.
4. Invalid or missing values are converted to NaN.
"""
df["price_clean"] = df["price"].str.replace(
r"[^\d]",
"",

# [] - Matches any character in the set
# ^ inside brackets = NOT
# \d = any digit (0-9)
# [^\d] - Matches any character that is NOT a digit (0-9)
regex=True
)

df["price_clean"] = pd.to_numeric(
df["price_clean"],
errors="coerce"
)


"""
Extract and convert apartment size in square meters.

This code:
1. Searches the 'combined_text' column for apartment sizes
   like "45 m²" or "60м²".
2. Extracts the numeric size value using a regular expression.
3. Stores the result in a new column called 'sqm'.
4. Converts the extracted values into numeric format.
5. Invalid or missing values are converted to NaN.
"""
df["sqm"] = df["combined_text"].str.extract(
r"(\d+\.?\d*)\s?[mм]²"
)

# \d+ - One or more digits (e.g., 45, 60)
# \.? - optional decimal point (for sizes like 45.5)
# \d* - optional decimals
# \s? - optional whitespace
# [mм]- Latin m or Russian м
# ² - square meters symbol

df["sqm"] = pd.to_numeric(
df["sqm"],
errors="coerce"
)

