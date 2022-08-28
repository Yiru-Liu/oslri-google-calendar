# oslri-google-calendar
A python script which automatically adds the due dates for items checked out from the Ocean State Libraries system to Google Calendar.

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
2. Follow [instructions](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) to install the browser driver for Firefox.
3. Run `main.py`. A browser window should appear asking you to authorize the application with your Google account. Sign in to your Google account and grant the application permissions to access the Calendar.
