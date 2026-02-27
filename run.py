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

"""
Selenium waiting tools.

Used to wait for webpage elements to load before scraping.
Improves scraper reliability.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.by import By


# Selenium is a powerful tool for web scraping and browser automation. 
# In this project, Selenium is used to navigate to the real estate listing website.

import pandas as pd
import numpy as np

# Pandas helps me organize and analyze my scraped data easier. 
# In my project, pandas turns raw Selenium data into a clean table.

# ==============================
# USER INPUT
# ==============================

country_input = input("Enter the country: ").strip().lower()

city_input = input("Enter the city: ").strip().lower()

rooms_input = input("Rooms desired: ").strip()

location_input = input("Preferred district: ").strip()

price_input = input("Maximum budget: ").strip()


# ==============================
# VALIDATION
# ==============================
"""
Validate supported country and city.
Program exits if unsupported values are entered.
"""
if country_input != "kazakhstan":
    print("Currently only Kazakhstan supported.")
    exit()

if city_input != "almaty":
    print("Currently only Almaty supported.")
    exit()


city_slug = "almaty"


# Budget conversion 
try:
    max_price = int(price_input)
except:
    max_price = 500000000

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

    if rooms_input:

        url = f"https://krisha.kz/prodazha/kvartiry/{city_slug}/?das[live.rooms]={rooms_input}&page={page}"

    else:
        url = f"https://krisha.kz/prodazha/kvartiry/{city_slug}/?page={page}"

    driver.get(url)

    print("Page",page)

    try:

        WebDriverWait(driver,10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME,"a-card")
            )
        )

    except:

        print("No more pages.")
        break

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

driver.quit()
#Close browser properly after scraping to free up system resources.


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

# Check if DataFrame is empty after scraping. If no listings were found, print a message and exit.
if df.empty:

    print("No listings found.")
    exit()

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
Filter listings by preferred location.

If the user specifies a district or area, this code
keeps only listings where the 'location' column
contains the entered text.

The comparison is case-insensitive and ignores
missing values.
"""
if location_input:

    df = df[
        df["location"].str.lower().str.contains(
        location_input.lower(),
        na=False
        )
    ]

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


df = df[
df["price_clean"] <= max_price
]
# Filter out listings that exceed the user's maximum budget to focus on relevant properties.

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



"""
Calculate price per square meter.

This code divides the cleaned apartment price by the
apartment size in square meters and stores the result
in the 'price_per_m2' column.
"""
df=df[df["sqm"]>0]
# Filter out listings with zero or negative size to avoid division errors.

df["price_per_m2"] = (
df["price_clean"]/df["sqm"]
)


"""
Filter unrealistic listings.

Keep only apartments where the price per square meter
is greater than 100000 to remove incorrect or invalid data.
"""
df = df[df["price_per_m2"] > 100000]



"""
Remove price per square meter outliers using the IQR method.

This code:
1. Calculates the first quartile (Q1) and third quartile (Q3)
   of the price_per_m2 column.
2. Computes the interquartile range (IQR).
3. Filters out values outside the range:
   Q1 - 1.5 * IQR to Q3 + 1.5 * IQR.
4. Keeps only listings within the normal price range.
"""
Q1 = df["price_per_m2"].quantile(0.25)

# Finds the 25% percentile
# Lower price range

Q3 = df["price_per_m2"].quantile(0.75)

# Finds the 75% percentile
# Upper price range

IQR = Q3-Q1

df = df[
(df["price_per_m2"]>=Q1-1.5*IQR) &
(df["price_per_m2"]<=Q3+1.5*IQR)
]
# Remove apartments with extremely low or extremely high price per m².
# This helps to focus on realistic listings and improve analysis accuracy.





"""
Calculate investment scores based on price per square meter.

This code:
1. Calculates the mean and standard deviation of price_per_m2.
2. Computes a z-score to measure how each listing compares
   to the average price per square meter.
3. Creates an undervaluation score where cheaper properties
   receive higher scores.
4. Creates a liquidity score based on relative price per m²,
   where lower prices result in higher liquidity scores.
"""
mean = df["price_per_m2"].mean()
# The mean (average) price per square meter across all listings.

std = df["price_per_m2"].std()
# Standard deviation = average distance from the mean

if std and not np.isnan(std):
    df["z_score"]=(df["price_per_m2"]-mean)/std
# Z-score is a number that shows how far a value is 
# from the mean (average), measured in standard deviations.
else:
    df["z_score"]=0

df["undervaluation_score"]=-df["z_score"]

max_m2=df["price_per_m2"].max()

# safe liquidity score calculation that avoids division by zero
if max_m2 and not np.isnan(max_m2):
    df["liquidity_score"]=(max_m2-df["price_per_m2"])/max_m2
else:
    df["liquidity_score"]=0
# Liquidity score is higher for cheaper properties, indicating they may sell faster.


"""
Calculate location-based and investment scores.

This section:

CENTER SCORE:
1. Defines keywords representing central districts.
2. Checks whether each listing location contains
   one of the center keywords.
3. Assigns a center_score:
   - 1 = central location
   - 0 = non-central location
   """
center_keywords = [
"Самал",
"Достык",
"Абая",
"Коктем",
"Орбита",
"Медеу"
]

df["center_score"] = df["location"].apply(
lambda x: any(
k.lower() in x.lower()
for k in center_keywords
)
).astype(int)


"""
INVESTMENT SCORE:
Combines multiple factors into a single score:
   - undervaluation_score (cheaper properties score higher)
   - liquidity_score (more affordable properties score higher)
   - center_score (central locations score higher)

Higher investment_score indicates a potentially
better investment opportunity.
"""
df["investment_score"] = (

df["undervaluation_score"]
+
df["liquidity_score"]
+
3*df["center_score"] # Center location is weighted more heavily in the investment score.

)

df=df.fillna(0)
# Replace any remaining NaN values with 0 to ensure all listings have valid scores.
# Replace missing values and show the best investments first.

df=df.sort_values(
by="investment_score",
ascending=False
)


"""
Write analyzed real estate data to today's worksheet.

This code:
1. Clears the current worksheet to remove old data.
2. Adds a header row with column names.
3. Uploads the processed DataFrame rows to Google Sheets.
4. Stores key metrics such as sqm, price per m²,
   z-score, liquidity score, center score,
   and investment score.
"""
TODAY_WS.clear()
# Removes old data.

TODAY_WS.append_row([
"header","price","location","link",
"sqm","price_per_m2",
"z_score","liquidity_score",
"center_score","investment_score"
])
# Creates table headers.

TODAY_WS.append_rows(
df[[
"header","price","location","link",
"sqm","price_per_m2",
"z_score","liquidity_score",
"center_score","investment_score"
]].values.tolist()
)

# Sends your DataFrame to Google Sheets.
# .values.tolist() converts the DataFrame into a format Google Sheets understands.





"""
Display market statistics and top investment listings.

This section:

MARKET SUMMARY:
1. Calculates average price, average apartment size,
   and average price per square meter.
2. Prints a summary of the real estate market.

TOP LISTINGS:
3. Selects the top investment opportunities.
4. Prints detailed information for up to 5 listings,
   including header, location, price, size,
   price per square meter, and link.
"""
# PRINT SUMMARY

avg_price = df["price_clean"].mean()
avg_sqm = df["sqm"].mean()
avg_price_m2 = df["price_per_m2"].mean()

print("\n📊 MARKET SUMMARY\n")

print(f"Average price: {avg_price:,.0f} ₸")
print(f"Average size: {avg_sqm:.1f} m²")
print(f"Average price per m²: {avg_price_m2:,.0f} ₸")


# PRINT TOP 5

TOP_N=min(5,len(df))

for _,row in df.head(TOP_N).iterrows():

    print("------------")
    print("Header:",row["header"])
    print("Location:",row["location"])
    print("Price:",f"{row['price_clean']:,.0f} ₸")
    print("Size:",f"{row['sqm']:.1f} m²")
    print("Price per m²:",f"{row['price_per_m2']:,.0f} ₸")
    print("Link:",row["link"])


print("Saved to Google Sheets")