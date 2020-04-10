import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from sys import stdout as out


def set_headless_firefox_driver():
    """Preparing a headless Firefox browser driver instance.
    
    Returns:
        WebDriver -- Selenium WebDriver object for Firefox
    """
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=640x360")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Firefox(options=firefox_options)
    return driver


def set_chrome_driver(DLPATH):
    """Preparing a Chromium browser instance ready for downloading files.
    
    Returns:
        WebDriver -- Selenium WebDriver object for Chromium
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--window-size=640x360")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": DLPATH,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_courselist_source(SEARCH_URL, n_pages=500, finish_rounds=100):
    RESULT_BUTTON=r'//*[@id="search-results-section-load-more"]'
    LOAD_MORE_RESULTS = r'jQuery(".button--secondary").click()'
    out.write("Loading the web driver ... "); out.flush()
    driver = set_headless_firefox_driver()
    out.write("Done. \n"); out.flush()
    out.write("Loading searchpage ... "); out.flush()
    driver.get(SEARCH_URL)
    for i in range(n_pages):
        try:
            wait_for_access(driver, RESULT_BUTTON)
            driver.execute_script(LOAD_MORE_RESULTS)
            if i == 0:
                msg_part1 = "Page loaded successfully.\n"
                msg_part2 = "                  "
                msg_part3 = "0%[.................................................]100%"
                msg_part4 = "\nScanning courses:   [."
                msg       = msg_part1+msg_part2+msg_part3+msg_part4
                out.write(msg); out.flush()
            elif i%8 == 0:
                out.write('.'); out.flush()
        except TimeoutException:
            msg = "]\nNo more courses could be found."
            out.write(msg)
            break
    out.write(" Scanning done.\nFinalizing result data .")
    for i in range(finish_rounds):
        driver.execute_script(LOAD_MORE_RESULTS)
        if i%10 == 0:
            out.write('.'); out.flush()
    out.write(' Done.\n')
    output_html = driver.page_source
    out.write('Closing web driver ... '); out.flush()
    driver.close()
    out.write('Done.\n')
    return output_html


def wait_for_access(driver, XPATH, timer=10):
    """Tracking an element, waiting for it to be available.
    
    Arguments:
        driver {WebDriver} -- Selenium WebDriver
        XPATH {str} -- XPATH element string
    
    Keyword Arguments:
        timer {int} -- Default timer to wait for element (default: {20})
    
    Returns:
        [WebDriver element] -- Element in interest
    """
    element = WebDriverWait(driver, timer).until(
    EC.element_to_be_clickable((By.XPATH, XPATH)))
    return element


########################### Beautuful soup functions ##########################
###############################################################################


def get_length(length_text):
    hours=None; minutes=None
    if length_text:
        hours_search = re.search(r'[0-9]+(?=h)', length_text)
        minutes_search = re.search(r'[0-9]+(?=m)', length_text)
        if hours_search:
            hours = int(hours_search.group())
        if minutes_search:
            minutes = int(minutes_search.group())
    if hours and minutes:
        time = hours*60 + minutes
    elif hours:
        time = hours*60
    elif minutes:
        time = minutes
    else:
        time = 'none'
    return time


def get_rating(rating_elem):
    if rating_elem:
        rating = re.search(r'[0-9]+', rating_elem.get_text())
        if rating:
            rating = int(rating.group())
        else:
            rating = ""
    else:
        rating = ""
    return rating


def get_course_elements(course):
    title = course.find("div", class_="search-result__title")
    author = course.find("div", class_="search-result__author")
    level = course.find("div", class_="search-result__level")
    date = course.find("div", class_="search-result__date")
    length = course.find("div", class_="search-result__length")
    rating = course.find("div", class_="search-result__rating")
    return title, author, level, date, length, rating


def get_course_elements_texts(course_elements):
    title = course_elements[0].get_text()
    url = course_elements[0].find('a').get('href')
    courseid = url.split('/')[-1]
    author = course_elements[1].get_text()
    level = course_elements[2].get_text()
    date = course_elements[3].get_text()
    length = get_length(course_elements[4].get_text())
    rating = get_rating(course_elements[5])
    return courseid, url, title, author, level, date, length, rating

