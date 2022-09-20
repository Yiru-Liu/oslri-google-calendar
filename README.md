# oslri-google-calendar
A Python script which automatically adds the due dates for items checked out from the Ocean State Libraries system to Google Calendar.

## Technologies
This project was created with:
* Python 3.10
* Mechanize 0.4.8
* Beautiful Soup 4.11.1
* Google Calendar API for Python

## Installation
1. Install the Google client library for Python, Mechanize, and Beautiful Soup:
   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib mechanize beautifulsoup4
   ```
2. Create a file in the same directory as `main.py` named `credentials.txt`. Put the user's library card number or username on the first line and the PIN on the second line of this text file. Example:
   ```
   library_card_number_or_username
   PIN
   ```
4. Run `main.py`. A browser window should appear asking you to authorize the application with your Google account. Sign in to your Google account and grant the application permissions to access the Calendar.
5. In order to make sure that the calendar is up to date, `main.py` should be run periodically (e.g. every 24 hours).
