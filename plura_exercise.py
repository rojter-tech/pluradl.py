import os, sys
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pluradl import get_courses, get_usr_pw, USERNAME, PASSWORD

login_url=r'https://app.pluralsight.com/id?'
course_base=r'https://app.pluralsight.com/library/courses'
username, password = "", ""

username_input=r'//*[@id="Username"]'
password_input=r'//*[@id="Password"]'
login_submit=r'//*[@id="login"]'
download_exercise_file=r'//*[@id="ps-main"]/div/div[2]/section/div[3]/div/div/button'
alt_download_excercise_file=r'/html/body/div[1]/div[3]/div/div[2]/section/div[4]/div/div/button'

def set_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=640x360")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "/home/dreuter/Downloads/Exercise_Files",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def wait_for_access(driver, XPATH, timer=20):
    element = WebDriverWait(driver, timer).until(
    EC.element_to_be_clickable((By.XPATH, XPATH)))
    return element


def login_routine(driver, login_url):
    driver.get(login_url)
    wait_for_access(driver, password_input)
    driver.find_element_by_xpath(username_input).send_keys(username)
    driver.find_element_by_xpath(password_input).send_keys(password)
    driver.find_element_by_xpath(login_submit).click()


def download_routine(driver, excercise_url):
    sleep(0.5)
    driver.get(excercise_url)
    try:
        wait_for_access(driver, download_exercise_file, timer=3).click()
    except TimeoutException:
        try:
            wait_for_access(driver, alt_download_excercise_file, timer=3).click()
        except TimeoutException:
            print(excercise_url, 'did not succeeded.')


def main():
    global username, password
    username, password = get_usr_pw()
    courses = get_courses(os.path.dirname(os.path.abspath(sys.argv[0])))
    driver = set_driver()
    login_routine(driver, login_url)
    for course in courses:
        excercise_url = course_base + '/' + course[0] + '/' + 'exercise-files'
        download_routine(driver, excercise_url)


if __name__ == "__main__":
    main()