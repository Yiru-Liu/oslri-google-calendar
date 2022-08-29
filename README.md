# oslri-google-calendar
A Python script which automatically adds the due dates for items checked out from the Ocean State Libraries system to Google Calendar.

## Technologies
This project was created with:
* Python 3.10
* Selenium 4.4.0
* Google Calendar API for Python

## Installation
1. Install the Google client library for Python and Selenium:
   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib selenium
   ```
2. Follow [instructions](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) to install the browser driver for Firefox and add the executable to PATH.
3. Create a file in the same directory as `main.py` named `credentials.txt`. Put the user's library card number or username on the first line and the PIN on the second line of this text file. Example:
   ```
   library_card_number_or_username
   PIN
   ```
4. Run `main.py`. A browser window should appear asking you to authorize the application with your Google account. Sign in to your Google account and grant the application permissions to access the Calendar.
5. In order to make sure that the calendar is up to date, `main.py` should be run periodically (e.g. every 24 hours).
