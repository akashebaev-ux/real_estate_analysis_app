import subprocess
# subprocess is used to run external commands from within
# the Python script.
# In this case, it's used to install the necessary Playwright
# browser dependencies before running the scraper.
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from playwright.sync_api import sync_playwright
from deep_translator import GoogleTranslator
import pandas as pd
import numpy as np
# Pandas helps me organize and analyze my scraped data easier.
from gspread_formatting import (
    CellFormat, TextFormat, Color, format_cell_range, set_frozen
)
# gspread-formatting is a library that allows you to apply formatting
# to Google Sheets using gspread.
from pyfiglet import figlet_format
# pyfiglet is a fun library that creates ASCII art text.
# I use it to print a cool title when the program starts.


# CONSTANTS
CITY_SLUG = "almaty"
MAX_PAGES = 2
MIN_DEFAULT = 20_000_000
MAX_DEFAULT = 500_000_000
# max_pages is set to 2 to limit the number of pages scraped.
CENTER_KEYWORDS = [
    "Самал",
    "Достык",
    "Абая",
    "Коктем",
    "Орбита",
    "Медеу"
    ]


def handle_attempts(attempts, last_value):
    """
    Handles behavior after 3 incorrect attempts.
     If the user has made 3 incorrect attempts, they are prompted
     to either continue with the last entered value or exit the program.
     This function returns the last entered value if the user chooses
     to continue, or exits the program if they choose to exit.
     If the number of attempts is less than 3, it simply returns None
     to allow the user to keep trying.
     """
    if attempts >= 3:
        choice = input(
            "Too many incorrect attempts. Continue anyway? (y/n): "
        ).strip().lower()
        if choice == "y":
            return last_value
        else:
            print("Exiting program.")
            exit()
    return None


def get_valid_country():
    """
    This function prompts the user to enter a country
    name and validates the input.
    It ensures that only letters are allowed, the
    length does not exceed 10 characters, and currently
    only "Kazakhstan" is accepted. The user has up to 3
    attempts to enter valid input, after which they can
    choose to continue or exit the program.
    """
    attempts = 0
    print("Enter the country (only Kazakhstan is available):")
    while True:
        country = input("> ").strip().lower()
        if not country.isalpha():
            print("Only letters allowed. No numbers or symbols.")
            attempts += 1
        elif len(country) > 10:
            print("Maximum 10 letters allowed.")
            attempts += 1
        elif country != "kazakhstan":
            print("Currently only Kazakhstan supported.")
            print("Please type: kazakhstan")
            attempts += 1
        else:
            return country
        result = handle_attempts(attempts, "Kazakhstan")
        if result is not None:
            print(
                "Because you did not enter a valid country after 3 attempts, "
                "the default value ('Kazakhstan') will be applied."
            )
            return result


def get_valid_city():
    """
    This function prompts the user to enter a
    city name and validates the input.
    It ensures that only letters are allowed, the
    length does not exceed 10 characters, and currently
    only "Almaty" is accepted. The user has up to 3 attempts
    to enter valid input, after which they can choose to
    continue or exit the program.
    """
    attempts = 0
    print("Enter the city (only Almaty is available):")
    while True:
        city = input("> ").strip().lower()
        if not city.isalpha():
            print("Only letters allowed. No numbers or symbols.")
            attempts += 1
        elif len(city) > 10:
            print("Maximum 10 letters allowed.")
            attempts += 1
        elif city != "almaty":
            print("Currently only Almaty supported.")
            print("Please type: almaty")
            attempts += 1
        else:
            return city
        result = handle_attempts(attempts, "Almaty")
        if result is not None:
            print(
                "Because you did not enter a valid city after 3 attempts, "
                "the default value ('Almaty') will be applied."
            )
            return result


def get_valid_rooms():
    """
    This function prompts the user to enter the number of rooms
    desired and validates the input.
    It ensures that only numbers are allowed, the value is between
    1 and 10, and the user has up to 3 attempts to enter valid input.
    After 3 incorrect attempts, the user can choose to continue with
    the last input or exit the program.
    """
    attempts = 0
    print("Number of rooms desired (1-10):")
    while True:
        rooms = input("> ").strip()
        if rooms == "":
            print(
                "Input cannot be empty. "
                "Please enter a number between 1 and 10."
            )
            attempts += 1
        elif not rooms.isdigit():
            print(
                "Only numbers are allowed. "
                "Please enter a number between 1 and 10."
            )
            attempts += 1
        else:
            rooms = int(rooms)
            if not 1 <= rooms <= 10:
                print(
                    "Maximum number of rooms allowed is 10."
                    "Please enter a number between 1 and 10."
                )
                attempts += 1
            else:
                return rooms
        result = handle_attempts(attempts, 1)
        if result is not None:
            print(
                "Because you did not enter a valid number after 3 attempts, "
                "the default value (1 room) will be applied."
            )
            return result


def get_valid_location():
    """
    This function prompts the user to enter a preferred location
    (center or outskirts) and validates the input.

    The user has up to 3 attempts. After 3 failed attempts,
    they can choose to continue or exit the program.
    """
    attempts = 0

    print("Preferred location (center / outskirts):\n"
          "(only one word - center or outskirts allowed)")

    while True:
        location = input("> ").strip().lower()

        if not location.isalpha():
            print("Only letters allowed. No numbers or symbols.")
            attempts += 1
        elif len(location) > 10:
            print("Error: Maximum length is 10 characters.")
            attempts += 1
        elif location not in ["center", "outskirts"]:
            print("Error: Only 'center' or 'outskirts' are allowed.")
            attempts += 1
        else:
            return location

        result = handle_attempts(attempts, "center")
        if result is not None:
            print(
                "Because you did not enter a valid location after 3 attempts, "
                "the default value ('center') will be applied."
            )
            return result


def get_valid_price():
    """
    This function prompts the user to enter a budget for real estate
    and validates the input.
    It ensures that only numeric values are accepted. If the user enters a
    value below the defined minimum (20 million KZT), it defaults to that
    minimum. After 3 invalid attempts, the user can choose to continue
    or exit the program.
    """
    attempts = 0
    while True:
        price = input(
            "Enter your budget (between 20 million and 500 million KZT).\n"
            f"Note: Any value below {MIN_DEFAULT} KZT "
            f"will be set to the default minimum of {MIN_DEFAULT} KZT.\n"
        ).strip()
        if not price.isdigit():
            print("Only numbers are allowed.")
            attempts += 1
            result = handle_attempts(attempts, MAX_DEFAULT)
            if result is not None:
                print(
                    f"Because you did not enter a valid number"
                    f"after 3 attempts, "
                    f"the default value ({MAX_DEFAULT} KZT) will be applied."
                )
                return result
            continue
        price = int(price)
        if price < MIN_DEFAULT:
            print(
                f"Entered value is below the minimum.\n"
                f"The default minimum of {MIN_DEFAULT} KZT will be used."
            )
            return MIN_DEFAULT
        if price > MAX_DEFAULT:
            print(
                f"Entered value is above the maximum.\n"
                f"The default maximum of {MAX_DEFAULT} KZT will be used."
            )
            return MAX_DEFAULT
        return price


def get_user_input():
    """
    Collect and validate user input for real estate search criteria.
    This function prompts the user to enter their preferences for country,
    city, number of rooms, preferred location, and budget.
    """
    print(f"""{figlet_format("Real Estate App")}
            Real Estate Analysis App
            --------------------------------
            This app helps you find the best real estate investment
            opportunities in Almaty, Kazakhstan.
            Please enter your search criteria below.
            """)
    country = get_valid_country()
    city = get_valid_city()
    rooms = get_valid_rooms()
    location = get_valid_location()
    price = get_valid_price()
    return country, city, rooms, location, price


def translate_text(text, target="en"):
    """
    Translate text to the target language using GoogleTranslator.
    This function takes a string of text and translates it into the
    specified target language (default is English).
    """
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except Exception:
        return text


def parse_price(price_input):
    """
    Parse and validate price input. Returns an integer or default value
    if invalid.This function attempts to convert the user's price input into
    an integer.If the input is invalid (non-numeric, negative, or zero),
    it defaults to 500 million. This ensures the program can continue running
    even if the user enters incorrect data.
    """
    try:
        max_price = int(price_input)
    except Exception:
        max_price = 500000000
    if max_price <= 0:
        max_price = 500000000
    return max_price


def setup_google_sheets():
    """
    Set up Google Sheets connection using gspread and service
    account credentials.
    Returns the authorized gspread client and the opened sheet.
    """
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
        ]
    CREDS = Credentials.from_service_account_file('creds.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('real_estate_analysis_app')
    today = datetime.now().strftime("%Y-%m-%d")
    # Creates and opens a worksheet in Google Sheets named with today's date.
    try:
        ws = SHEET.worksheet(today)
    except gspread.exceptions.WorksheetNotFound:
        ws = SHEET.add_worksheet(
            title=today,
            rows="10000",
            cols="20"
        )
    return ws


def scrape_data(rooms_input):
    """
    Scrape real estate data from the website using Playwright.
    It navigates through multiple pages of listings,
    extracts relevant information.
    The function handles potential loading issues and collects
    data into a list for further processing.
    """
    all_data = []
    page_num = 1
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        page = browser.new_page()
        while page_num <= MAX_PAGES:
            if rooms_input:
                url = (
                    f"https://krisha.kz/prodazha/kvartiry/{CITY_SLUG}/"
                    f"?das[live.rooms]={rooms_input}&page={page_num}"
                )
            else:
                url = (
                    f"https://krisha.kz/prodazha/kvartiry/{CITY_SLUG}/"
                    f"?page={page_num}"
                )
            print("Currently parsing page", page_num)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception:
                print("Page failed to load, stopping scraper.")
                break
            try:
                page.wait_for_selector(".a-card", timeout=60000)
            except Exception:
                print("No more pages.")
                break
            cards = page.query_selector_all(".a-card")
            for card in cards:
                try:
                    header = card.query_selector(
                        ".a-card__header"
                    ).inner_text()
                    price = card.query_selector(
                        ".a-card__price"
                    ).inner_text()
                    location = card.query_selector(
                        ".a-card__subtitle"
                    ).inner_text()
                    link = card.query_selector("a").get_attribute("href")
                    link = "https://krisha.kz" + link
                    combined_text = card.inner_text()
                    all_data.append([
                        header,
                        price,
                        location,
                        link,
                        combined_text
                    ])
                except Exception as e:
                    print("Skipping card:", e)
                    continue
            page_num += 1
        browser.close()
    return all_data


def clean_data(all_data, rooms_input, location_input, max_price):
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
        columns=["header", "price", "location", "link", "combined_text"]
    )
    # It checks if DataFrame is empty after scraping.
    if df.empty:
        return df
    # The code belowe: extract the number of rooms from the flat header
    # and convert it to numeric format.
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
    # errors="coerce" converts non-numeric values to NaN, which is useful
    # for filtering later.
    if rooms_input is not None:
        df = df[df["rooms"] == int(rooms_input)]
    # The code below removes duplicate flat listings based on the link column.
    # Ensures each property appears only once in the dataset.
    df = df.drop_duplicates(subset=["link"])
    # Filter listings by preferred location.
    # If the user specifies a district or area, this code
    # keeps only listings where the 'location' column
    # contains the entered text.
    # The comparison is case-insensitive and ignores
    # missing values.
    if location_input == "center":
        df = df[
            df["location"].apply(
                lambda x: any(
                    k.lower() in x.lower()
                    for k in CENTER_KEYWORDS
                )
            )
        ]
    elif location_input == "outskirts":
        df = df[
            ~df["location"].apply(
                lambda x: any(
                    k.lower() in x.lower()
                    for k in CENTER_KEYWORDS
                )
            )
        ]
    # Clean and convert price data.
    # This code:
    # 1. Removes all non-numeric characters from the 'price' column using
    # a regular expression.
    # 2. Stores the cleaned values in a new column called 'price_clean'.
    # 3. Converts the cleaned prices into numeric format.
    # 4. Invalid or missing values are converted to NaN.
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
    # Filter out listings that exceed the user's maximum budget to focus on
    # relevant properties.
    # Extract and convert apartment size in square meters.
    # This code:
    # 1. Searches the 'combined_text' column for apartment sizes
    # like "45 m²" or "60м²".
    # 2. Extracts the numeric size value using a regular expression.
    # 3. Stores the result in a new column called 'sqm'.
    # 4. Converts the extracted values into numeric format.
    # 5. Invalid or missing values are converted to NaN.
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
    # Calculate price per square meter.
    # This code divides the cleaned apartment price by the
    # apartment size in square meters and stores the result
    # in the 'price_per_m2' column.
    df = df[df["sqm"] > 0]
    # Filter out listings with zero or negative size to avoid division errors.
    df["price_per_m2"] = (
        df["price_clean"]/df["sqm"]
    )
    # Filter unrealistic listings.
    # Keep only apartments where the price per square meter
    # is greater than 100000 to remove incorrect or invalid data.
    df = df[df["price_per_m2"] > 100000]
    # Remove price per square meter outliers using the IQR method.
    # This code:
    # 1. Calculates the first quartile (Q1) and third quartile (Q3)
    # of the price_per_m2 column.
    # 2. Computes the interquartile range (IQR).
    # 3. Filters out values outside the range:
    # Q1 - 1.5 * IQR to Q3 + 1.5 * IQR.
    # 4. Keeps only listings within the normal price range.
    Q1 = df["price_per_m2"].quantile(0.25)
    # Finds the 25% percentile
    # Lower price range
    Q3 = df["price_per_m2"].quantile(0.75)
    # Finds the 75% percentile
    # Upper price range
    IQR = Q3-Q1
    df = df[
        (df["price_per_m2"] >= Q1-1.5*IQR) &
        (df["price_per_m2"] <= Q3+1.5*IQR)
    ]
    # Remove apartments with extremely low or extremely high price per m².
    # This helps to focus on realistic listings and improve analysis accuracy.
    # Calculate investment scores based on price per square meter.
    # This code:
    # 1. Calculates the mean and standard deviation of price_per_m2.
    # 2. Computes a z-score to measure how each listing compares
    # to the average price per square meter.
    # 3. Creates an undervaluation score where cheaper properties
    # receive higher scores.
    # 4. Creates a liquidity score based on relative price per m²,
    # where lower prices result in higher liquidity scores.
    mean = df["price_per_m2"].mean()
    # The mean (average) price per square meter across all listings.
    std = df["price_per_m2"].std()
    # Standard deviation = average distance from the mean
    if std and not np.isnan(std):
        df["z_score"] = (df["price_per_m2"]-mean)/std
    # Z-score is a number that shows how far a value is
    # from the mean (average), measured in standard deviations.
    else:
        df["z_score"] = 0
    df["undervaluation_score"] = - df["z_score"]
    max_m2 = df["price_per_m2"].max()
    # safe liquidity score calculation that avoids division by zero
    if max_m2 and not np.isnan(max_m2):
        df["liquidity_score"] = (max_m2-df["price_per_m2"])/max_m2
    else:
        df["liquidity_score"] = 0
    # Liquidity score is higher for cheaper properties, indicating they
    # may sell faster.
    # Calculate location-based and investment scores.
    # This section:
    # CENTER SCORE:
    # 1. Defines keywords representing central districts.
    # 2. Checks whether each listing location contains one of the
    # center keywords.
    # 3. Assigns a center_score:
    # - 1 = central location
    # - 0 = non-central location
    df["center_score"] = df["location"].apply(
        lambda x: any(
            k.lower() in x.lower()
            for k in CENTER_KEYWORDS
        )
    ).astype(int)
    # INVESTMENT SCORE:
    # Combines multiple factors into a single score:
    # - undervaluation_score (cheaper properties score higher)
    # - liquidity_score (more affordable properties score higher)
    # - center_score (central locations score higher)
    # Higher investment_score indicates a potentially
    # better investment opportunity.
    df["investment_score"] = (
        df["undervaluation_score"]
        +
        df["liquidity_score"]
        +
        3*df["center_score"]
        # Center location is weighted more heavily in the investment score.
    )
    df = df.fillna(0)
    # Replace any remaining NaN values with 0 to ensure all listings
    # have valid scores.
    # Replace missing values and show the best investments first.
    df = df.sort_values(
        by="investment_score",
        ascending=False
    )
    # Sort listings by investment score in descending order, so
    # the best investment
    #  opportunities appear at the top of the DataFrame.
    if df.empty:
        return df
    return df


def save_to_sheets(df, ws):
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
    ws.clear()
    # Clear worksheet to avoid mixing previous runs with new results
    ws.append_row([
        "header", "price", "location", "link",
        "sqm", "price_per_m2",
        "z_score", "liquidity_score",
        "center_score", "investment_score"
    ])
    # Creates table headers.
    ws.append_rows(
        df[[
            "header", "price", "location", "link",
            "sqm", "price_per_m2",
            "z_score", "liquidity_score",
            "center_score", "investment_score"
        ]].values.tolist()
    )
    # Sends your DataFrame to Google Sheets.
    # .values.tolist() converts the DataFrame into a format
    # Google Sheets understands.


def print_results(df, ws):
    """
    Format Google Sheets output for better readability.
    This section:
    1. Formats the header row (A1:J1) in bold text.
    2. Freezes the header row so column titles remain visible
    while scrolling.
    3. Highlights the top 3 investment listings in green
    based on investment_score ranking.
    This improves the visual presentation of the results
    in Google Sheets.
    """
    header_format = CellFormat(
        textFormat=TextFormat(bold=True)  # Make header bold
    )
    format_cell_range(
        ws,
        "A1:J1",
        header_format
    )
    # Freeze header row
    set_frozen(
        ws,
        rows=1
    )
    # Highlight top 3 investment listings green
    green_format = CellFormat(
        backgroundColor=Color(0.85, 1, 0.85)
    )
    TOP_N = min(3, len(df))
    for i in range(TOP_N):
        row_number = i + 2
        format_cell_range(
            ws,
            f"A{row_number}:J{row_number}",
            green_format
        )
    # Display market statistics and top investment listings.
    # This section:
    # MARKET SUMMARY:
    # 1. Calculates average price, average apartment size,
    # and average price per square meter.
    # 2. Prints a summary of the real estate market.
    # TOP LISTINGS:
    # 3. Selects the top investment opportunities.
    # 4. Prints detailed information for up to 5 listings,
    # including header, location, price, size,
    # price per square meter, and link.
    # print market summary statistics such as average price, average size,
    # and average price
    # per square meter.
    avg_price = df["price_clean"].mean()
    avg_sqm = df["sqm"].mean()
    avg_price_m2 = df["price_per_m2"].mean()
    print("\n📊 MARKET SUMMARY\n")
    print(f"Average price: {avg_price:,.0f} ₸")
    print(f"Average size: {avg_sqm:.1f} m²")
    print(f"Average price per m²: {avg_price_m2:,.0f} ₸")
    # print the top investment options based on the highest investment scores.
    print("\n🔥 TOP INVESTMENT OPTIONS 🔥\n")
    TOP_N = min(3, len(df))
    for _, row in df.head(TOP_N).iterrows():
        translated_header = translate_text(row["header"])
        translated_location = translate_text(row["location"])
        print("\n------------\n")
        print("Apartment:", translated_header)
        print("Location:", translated_location)
        print("Price:", f"{row['price_clean']:,.0f} ₸")
        print("Size:", f"{row['sqm']:.1f} m²")
        print("Price per m²:", f"{row['price_per_m2']:,.0f} ₸")
        print("Link:", row["link"])
    print("Saved to Google Sheets")


def main():
    """
    Main function to run the real estate analysis app.
    This function orchestrates the entire workflow:
    1. Collects user input for search criteria.
    2. Validates the entered location.
    3. Parses and validates the price input.
    4. Sets up the Google Sheets connection.
    5. Scrapes real estate data from the website.
    6. Cleans and analyzes the data.
    7. Saves the results to Google Sheets.
    8. Prints a summary of the market and top investment options.
    """
    subprocess.run(
        ["playwright", "install", "chromium"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    _, _, rooms, location, price_input = get_user_input()
    max_price = parse_price(price_input)
    ws = setup_google_sheets()
    data = scrape_data(rooms)
    df = clean_data(
        data,
        rooms,
        location,
        max_price
    )
    if df.empty:
        print("No listings found.")
        choice = input("Do you want to search again? (y/n): ").strip().lower()
        if choice == "y":
            return
        else:
            print("Goodbye!")
            exit()
    save_to_sheets(df, ws)
    print_results(df, ws)


if __name__ == "__main__":
    while True:
        main()
        choice = input(
            "\nDo you want to run the program again? (y/n): "
            ).strip().lower()
        if choice == "y":
            continue
        elif choice == "n":
            print("Program finished. Goodbye!")
            break
        else:
            print("Invalid input. Exiting program.")
            break
