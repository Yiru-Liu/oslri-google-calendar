#!/usr/bin/env python3
"""Main script of the project.

The first time this is run, a browser window may pop up asking the user to
authorize access to their Google account. Permission should be granted to
access Google Calendar in order to update events.
Should be run periodically to ensure Google Calendar is up to date
(recommendation: every 24 hours).
"""

import re
import datetime
import requests
import mechanize
import http.cookiejar
from cal_setup import get_cal_service

__author__ = "Yiru Liu"
__copyright__ = "Copyright 2022, Yiru Liu"
__license__ = "MIT"
__maintainer__ = "Yiru Liu"
__email__ = "yiru.liu05@gmail.com"
__status__ = "Production"

LOGIN_URL = "https://catalog.oslri.net/patroninfo"
CALENDAR_NAME = "OSLRI Due Dates"

def get_checkedout_info(username, pin):
    """
    Returns a list of dictionaries, each dictionary containing information
    about one item.

            Parameters:
                    username (str): Library Card Number or Username
                    pin (str): PIN to log in to the library account

            Returns:
                    info (list of dictionaries):
                        Each dictionary in the list contains info of one item
                        checked out, and has the following keys:
                            "Title" (str): The short title
                            "Due Date" (datetime): The due date
                            "Renewed" (str): A string that describes how many
                                             times the item has been renewed
    """
    # Initialize the driver and run it in headless mode
    # so the browser window doesn't show
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

        # Title up until the first " / " or " : "
        title = re.split(r" / | : ", full_title)[0]

        # Entire text under "Status" column
        status = item.find_element(By.CLASS_NAME, "patFuncStatus").text

        # Use regular expression to find "MM-DD-YY"
        due_date_text = re.search(r'(\d+-\d+-\d+)', status).group(1)
        # Convert to datetime object
        due_date = datetime.datetime.strptime(due_date_text, "%m-%d-%y")

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
    print("Closing Webdriver...", end=" ", flush=True)
    driver.close()
    print("Done.")
    return info


def checkedout_info_to_cal_events(checkedout_info):
    """
    Takes checkedout_info returned by get_checkedout_info and returns a list
    of calendar events.

            Parameters:
                    info (list of dictionaries):
                        Each dictionary in the list contains info of one item
                        checked out, and has the following keys:
                            "Title" (str): The short title
                            "Due Date" (datetime): The due date
                            "Renewed" (str): A string that describes how many
                                             times the item has been renewed

            Returns:
                    updated_events (list of calendar events):
                        List of calendar events, which can be passed to
                        push_to_google_calendar.
    """
    assert isinstance(checkedout_info, list)
    assert all(isinstance(item, dict) for item in checkedout_info)

    updated_events = []
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
        updated_events.append(event)
    return updated_events


def push_to_google_calendar(updated_events):
    assert isinstance(updated_events, list)
    assert all(isinstance(item, dict) for item in updated_events)

    print("Getting calendar service...", end=" ", flush=True)
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

    current_events = service.events().list(calendarId=oslri_calendar_id).execute().get("items", [])
    events_to_be_added = []
    events_to_be_removed = []

    for updated_event in updated_events:
        if all(not (updated_event.items() <= current_event.items()) for current_event in current_events):
            events_to_be_added.append(updated_event)

    for current_event in current_events:
        if all(not (updated_event.items() <= current_event.items()) for updated_event in updated_events):
            events_to_be_removed.append(current_event)

    print(f"Events to be added: {events_to_be_added}")
    print(f"Events to be removed: {events_to_be_removed}")

    for event in events_to_be_removed:
        service.events().delete(calendarId=oslri_calendar_id, eventId=event["id"]).execute()
        print(f"Event removed: {event}")

    for event in events_to_be_added:
        event = service.events().insert(calendarId=oslri_calendar_id, body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")


def main():
    with open("credentials.txt") as f:
        username = f.readline().strip()
        pin = f.readline().strip()
        f.close()
    checkedout_info = get_checkedout_info(username, pin)
    updated_events = checkedout_info_to_cal_events(checkedout_info)
    push_to_google_calendar(updated_events)
    print("Pushed to Google Calendar.")


if __name__ == "__main__":
    # main()
    print("Program started.")
    cj = http.cookiejar.CookieJar()
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_cookiejar(cj)
    br.open(LOGIN_URL)
    print("Login page loaded.")
    br.select_form(nr=0)
    br.form["code"] = ""
    br.form["pin"] = ""
    br.submit()
    print("Login successful.")

    br.follow_link(text_regex=".*currently checked out")

    print(br.response().read())
    print("Successfully retrieved checked out items.")

    with open("items.html", "wb") as w:
        w.write(br.response().read())
