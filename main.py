from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

URL = "https://catalog.oslri.net/iii/cas/login" \
      "?service=https%3A%2F%2Fcatalog.oslri.net%3A443%2Fpatroninfo~S1%2FIIITICKET&scope=1"
WAIT_DELAY = 10


def main():
    driver = webdriver.Firefox()
    driver.get(URL)
    assert driver.title == "Ocean State Libraries Log in"
    username_input = driver.find_element(By.ID, "code")
    pin_input = driver.find_element(By.ID, "pin")
    submit_button = driver.find_element(By.CSS_SELECTOR, ".formButtons > a:nth-child(1) > div:nth-child(1)")
    with open("credentials.txt") as f:
        username = f.readline().strip()
        pin = f.readline().strip()
    username_input.send_keys(username)
    pin_input.send_keys(pin)
    ActionChains(driver).click(submit_button).perform()
    checked_out_link = WebDriverWait(driver, WAIT_DELAY).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#patButChkouts > div:nth-child(1) > a:nth-child(1)"))
    )
    ActionChains(driver).click(checked_out_link).perform()
    time.sleep(5)
    first_due_date = WebDriverWait(driver, WAIT_DELAY).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr.patFuncEntry:nth-child(2) > td:nth-child(4)"))
    )
    print(first_due_date.text)
    driver.close()


if __name__ == "__main__":
    main()
