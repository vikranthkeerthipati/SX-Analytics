import scrape, analyze
from selenium import webdriver
#Separate config file
import config
import os
#Intializing headless browser
def main():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    profile = webdriver.FirefoxProfile()
    download_path = config.download_path
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_path)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    browser = webdriver.Firefox(profile,executable_path="./geckodriver",options=firefox_options)
    try:
        #scraping data
        scrape.scrape(browser)
        #analyzing and sending to slack
        analyze.analyze()
    finally:
        browser.quit()
