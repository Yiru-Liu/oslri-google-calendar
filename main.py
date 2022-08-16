from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time
import re
import datetime

LOGIN_URL = "https://catalog.oslri.net/patroninfo"


# Returns a list of dictionaries.
# Each dictionary contains info of one item checked out, and has
# the following keys:
# "Title": A string that contains the short title.
# "Due Date": A datetime object of the due date.
def get_checkedout_info():
    # Initialize the driver and run it in headless mode so the browser window doesn't show
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)  # Allow time for the pages to load

    # Go to the login page:
    driver.get(LOGIN_URL)
    assert driver.title == "Ocean State Libraries Log in"

    # Input credentials and log in:
    username_input = driver.find_element(By.ID, "code")
    pin_input = driver.find_element(By.ID, "pin")
    submit_button = driver.find_element(By.CSS_SELECTOR, ".formButtons > a")
    with open("credentials.txt") as f:
        username = f.readline().strip()
        pin = f.readline().strip()
    username_input.send_keys(username)
    pin_input.send_keys(pin)
    ActionChains(driver).click(submit_button).perform()

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
        item_info_dict = {
            "Title": title,
            "Due Date": due_date
        }
        info.append(item_info_dict)
    driver.close()
    return info


def main():
    checkedout_info = get_checkedout_info()
    print(checkedout_info)


if __name__ == "__main__":
    main()
