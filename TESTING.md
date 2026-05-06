## PEP8 Errors Identified and Resolved

The following errors were identified and resolved during the CI Python Linter validation process.

| Error | Issue | Resolution | Example |
|------|------|------|------|
| E501 | Lines exceeded the recommended 79 character limit | Broke long lines into multiple lines using parentheses or variables to keep lines under 79 characters | Screenshot of line length correction <br> <img width="400" alt="E501" src="https://github.com/user-attachments/assets/cd0c2c13-d624-45d1-909b-725f2ca9a5b3">|
| E225 | Missing whitespace around operators | Added spaces around operators to follow PEP8 formatting standards | Screenshot showing corrected spacing <br> <img width="400" alt="E225" src="https://github.com/user-attachments/assets/73625e3e-f3fa-4277-990d-bf1b267268fe">|
| E231 | Missing whitespace after commas | Added spaces after commas in lists, function arguments, and dictionaries | Screenshot showing corrected commas <br> <img width="400" alt="E231" src="https://github.com/user-attachments/assets/c15c9a4e-dd73-4f2e-86cc-58bb54f15640">|
| E303 | Too many blank lines between sections of code | Removed extra blank lines to follow PEP8 recommendations | Screenshot showing corrected spacing <br> <img width="400" alt="E303" src="https://github.com/user-attachments/assets/2b919a41-d529-4667-a3f7-4aaab8dec000">|
| W291 | Line contained trailing whitespace | Removed unnecessary whitespace at the end of lines | Screenshot showing corrected line <br> <img width="400" alt="W291" src="https://github.com/user-attachments/assets/c6d41efa-4769-4f4a-bf97-6683b4109ca8">|
| W293 | Blank line contained whitespace | Deleted whitespace from empty lines | Screenshot showing corrected blank line <br> <img width="400" alt="W293" src="https://github.com/user-attachments/assets/b4cac2e4-7c9b-4dfb-b8b4-42adbc141889">|
| W292 | Missing newline at the end of the file | Added a newline at the bottom of the file | Screenshot of file end <br> <img width="400" alt="W292" src="https://github.com/user-attachments/assets/17e3e99b-a54b-4c8a-af53-df59ab6f19d0">|

---

## PEP8 Validation Results

| File | URL | Screenshot | Notes |
|------|------|------|------|
| run.py | PEP8 CI Python Linter | Screenshot of run.py no issues <br> <img width="400" alt="PEP8+" src="https://github.com/user-attachments/assets/76eb35fe-5912-4af8-925d-c5eebe22d49a" />
 | PEP8 validation passed |

---

### Responsiveness
The application runs entirely in a command-line environment. Because it does not have a graphical user interface, testing responsiveness across different devices or screen sizes is not relevant.

### Browser Compatibility
This project is a Python-based command-line program that is deployed using the Code Institute web terminal. Browser compatibility testing therefore concerns only whether the terminal environment loads correctly in the browser, rather than the behaviour of the application itself. For this reason, browser compatibility testing is not applicable to the project.

### Lighthouse Audit
Lighthouse audits are designed to evaluate web pages and front-end performance. Since this project operates as a command-line Python application within a terminal interface, Lighthouse would only analyse the surrounding interface and not the functionality of the program itself. Therefore, running a Lighthouse audit is not relevant for this project.


# Defensive Programming
# Input Validation

Several validation checks were implemented in the program to prevent user input errors and ensure the application runs reliably. These validations help control incorrect data entry and reduce the likelihood of runtime errors.

## 1. Preventing Empty Input

The program checks that the user does not submit an empty value when entering numeric data such as the number of rooms.

Example used in the code:
```
if rooms == "":
    print("Input cannot be empty.")
```
    
### Why this is important

Without this validation, an empty input could cause errors when the program attempts to convert the value into a number. This check ensures that the user always provides a value before the program continues.

## 2. Excluding Letters When Numbers Are Required

When the program expects a numeric value (such as number of rooms or budget), the `.isdigit()` method is used to verify that the input contains only numbers.

Example:
```
elif not rooms.isdigit():
    print("Only numbers are allowed.")
```

### Why this helps

This prevents users from entering letters or mixed values such as:
```
  abc
  2rooms
  five
  2.3
  -5
```
**NOTE:** The `.isdigit()` method checks whether the input contains only digits (0–9). If the input contains any other characters, the validation fails. 
Even though `.isdigit()` would normally accept "0", my code has an **additional validation step [## 5. Restricting Values to a Valid Range](## 5. Restricting Values to a Valid Range)** that blocks it.

## 3. Excluding Numbers and Symbols When Letters Are Required

For inputs like country, city, and location, the program uses .isalpha() to ensure that only alphabetic characters are entered.

Example:
```
if not country.isalpha():
    print("Only letters allowed. No numbers or symbols.")
```
### Why this helps

This validation prevents incorrect entries such as:
```
  Almaty123
  Almaty!
  Kazakhstan1
```
Allowing only letters ensures the input matches the expected format for location names.

## 4. Limiting Input Length

The program checks the length of certain inputs to prevent excessively long entries.

Example:
```
elif len(country) > 10:
    print("Maximum 10 letters allowed.")
```
### Why this helps

Limiting the length prevents unrealistic or incorrect values from being entered. It also protects the program from malformed or accidental long inputs that could affect program logic or readability.

## 5. Restricting Values to a Valid Range

For numeric inputs such as the number of rooms, the program checks that the value falls within an acceptable range.

Example:
```
if not 1 <= rooms <= 10:
    print("Please enter a number between 1 and 10.")
```

### Why this helps

This prevents unrealistic values such as:
```
  0 rooms
  25 rooms
  -5 rooms
```
Restricting the range ensures that the data remains realistic and usable for the real estate search.

## 6. Handling Budget Limits

The user’s budget input is validated to ensure it falls within the acceptable range.

Example:
```
if price < MIN_DEFAULT:
    return MIN_DEFAULT
```

### Why this helps

This prevents unrealistic values from affecting the filtering process and ensures that the system always has a usable budget value.

## 7. Limiting Incorrect Attempts

The program limits the number of incorrect attempts to three.

Example:
```
if attempts >= 3:
```

After three failed attempts, the user is given the option to:

- continue with the last entered value

- exit the program

### Why this helps

This prevents infinite input loops and improves the user experience by giving the user control over how to proceed.

## 8. Data Cleaning Validation

After scraping the data, additional validation is applied to ensure that the dataset is reliable.

Examples include:

**Removing non-numeric characters from price values**
```
df["price_clean"] = df["price"].str.replace(r"[^\d]", "", regex=True)
```
**Converting extracted values to numeric**
```
pd.to_numeric(df["sqm"], errors="coerce")
```
**Removing unrealistic listings**
```
df = df[df["price_per_m2"] > 100000]
```

### Why this helps

These validations ensure that scraped data is accurate and prevents incorrect listings from affecting the final analysis.

## Summary

The validation system improves the reliability of the application by:

- preventing empty input

- ensuring correct data types

- restricting invalid characters

- enforcing realistic value ranges

- limiting incorrect attempts

- cleaning scraped data before analysis

Together, these checks help prevent runtime errors and ensure that the application processes only valid and meaningful data.

## Important:

No bugs are currently known. However, despite extensive testing, the possibility of undiscovered issues cannot be entirely ruled out.
