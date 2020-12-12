from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import config


def scrape(browser):
    browser.get("https://sx-members.slack.com/stats#overview")

    #Waiting until page has loaded and entering username and password
    try:
        page_ready = WebDriverWait(browser,60).until(EC.visibility_of(browser.find_element_by_id("email")))
    except:
        print("timed out")
        f = open("error.html", "a")
        f.write(browser.page_source)
        browser.quit() 
    email_field = browser.find_element_by_id("email")
    print("login page opened")
    time.sleep(0.5)
    email_field.send_keys(config.username)
    pass_field = browser.find_element_by_id("password")
    pass_field.send_keys(config.password)
    time.sleep(0.5)

    #Submitting credentials
    submit_button = browser.find_element_by_id("signin_btn")
    actions = ActionChains(browser)
    actions.move_to_element(submit_button).click().perform()
    print("done with login")
    print("waiting for new page...")

    #Waiting for next page and catches TimeoutException
    try:
        page_ready = WebDriverWait(browser,60).until(EC.element_to_be_clickable((By.CLASS_NAME, "ent_csv_popover__btn")))
    except(TimeoutException):
        print("timed out")
        f = open("error.html", "a")
        f.write(browser.page_source)
        browser.quit()
    print("loaded!")
    time.sleep(0.5)

    #Clicks the export button on analytics pages and saves it
    export_button = browser.find_element_by_class_name("ent_csv_popover__btn")
    print(export_button.text)
    export_button.click()
    print("downloaded!")
    time.sleep(1)

