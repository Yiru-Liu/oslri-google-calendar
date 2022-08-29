#!/usr/bin/env python3
"""Main script of the project.

The first time this is run, a browser window may pop up asking the user to
authorize access to their Google account. Permission should be granted to
access Google Calendar.
Should be run periodically to ensure Google Calendar is up to date
(recommendation: every 24 hours).
"""

import re
import datetime
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from cal_setup import get_cal_service

__author__ = "Yiru Liu"
__copyright__ = "Copyright 2022, Yiru Liu"
__license__ = "MIT"
__maintainer__ = "Yiru Liu"
__email__ = "yiru.liu05@gmail.com"
__status__ = "Development"

LOGIN_URL = "https://catalog.oslri.net/patroninfo"
CALENDAR_NAME = "OSLRI Due Dates"

def get_checkedout_info(username, pin):
    """
    Returns a list of dictionaries.

            Parameters:
                    username (str): Library Card Number or Username
                    pin (str): PIN to log in to the library account

            Returns:
                    info (list of dictionaries):
                        Each dictionary in the list contains info of one item checked out, and has the following keys:
                            "Title" (str): The short title
                            "Due Date" (datetime): The due date
                            "Renewed" (str): A string that describes how many times the item has been renewed
    """
    # Initialize the driver and run it in headless mode so the browser window doesn't show
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(3)  # Allow time for the pages to load
    print("Webdriver initialized.")

    # Go to the login page:
    driver.get(LOGIN_URL)
    assert driver.title == "Ocean State Libraries Log in"

    # Input credentials and log in:
    username_input = driver.find_element(By.ID, "code")
    pin_input = driver.find_element(By.ID, "pin")
    submit_button = driver.find_element(By.CSS_SELECTOR, ".formButtons > a")
    username_input.send_keys(username)
    pin_input.send_keys(pin)
    ActionChains(driver).click(submit_button).perform()
    print("Successfully logged in to OSLRI.")

    # Go to Items Checked Out page:
    checked_out_link = driver.find_element(By.ID, "patButChkouts")
    ActionChains(driver).click(checked_out_link).perform()

    # Pull information from table:
    item_table = driver.find_elements(By.CSS_SELECTOR, "#checkout_form tr.patFuncEntry")
    info = []
    for item in item_table:
        full_title = item.find_element(By.CLASS_NAME, "patFuncTitleMain").text
        title = re.split(r" / | : ", full_title)[0]     # Title up until the first " / " or " : "

        status = item.find_element(By.CLASS_NAME, "patFuncStatus").text     # Entire text under "Status" column

        due_date_text = re.search(r'(\d+-\d+-\d+)', status).group(1)        # Use regular expression to find "MM-DD-YY"
        due_date = datetime.datetime.strptime(due_date_text, "%m-%d-%y")    # Convert to datetime object

        renewed_index = status.find("Renewed")
        if renewed_index == -1:
            renewed = "Renewed 0 times"
        else:
            renewed = status[renewed_index:]

        item_info_dict = {
            "Title": title,
            "Due Date": due_date,
            "Renewed": renewed
        }
        print(f"Item info pulled: {item_info_dict}")
        info.append(item_info_dict)
    print("Closing Webdriver...", end=" ")
    driver.close()
    print("Done.")
    return info


def push_to_google_calendar(checkedout_info):
    assert isinstance(checkedout_info, list)
    assert all(isinstance(item, dict) for item in checkedout_info)
    print("Getting calendar service...", end=" ")
    service = get_cal_service()
    print("Done.")

    # Get currently existing calendars, and their names and ids:
    calendars = service.calendarList().list().execute().get("items", [])
    calendar_summaries = [calendar["summary"] for calendar in calendars]
    calendar_ids = [calendar["id"] for calendar in calendars]
    try:    # Tries to get the calendar ID of the OSLRI calendar, if it exists:
        oslri_calendar_i = calendar_summaries.index(CALENDAR_NAME)
        oslri_calendar_id = calendar_ids[oslri_calendar_i]
    except ValueError:  # If the OSLRI calendar does not yet exist, create it:
        oslri_calendar = {"summary": CALENDAR_NAME}
        oslri_calendar_id = service.calendars().insert(body=oslri_calendar).execute()["id"]

    print(oslri_calendar_id)

    for item in checkedout_info:
        event = {
            "summary": "Due: " + item["Title"],
            "start": {
                "date": item["Due Date"].strftime(r"%Y-%m-%d")
            },
            "end": {
                "date": item["Due Date"].strftime(r"%Y-%m-%d")
            },
            "description": item["Renewed"]
        }
        event = service.events().insert(calendarId=oslri_calendar_id, body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
    

def main():
    with open("credentials.txt") as f:
        username = f.readline().strip()
        pin = f.readline().strip()
        f.close()
    checkedout_info = get_checkedout_info(username, pin)
    push_to_google_calendar(checkedout_info)
    print("Pushed to Google Calendar.")


if __name__ == "__main__":
    main()
