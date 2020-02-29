import os, sys, re
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pluradl import get_courses, get_usr_pw, set_directory

LOGIN_URL=r'https://app.pluralsight.com/id?'
COURSE_BASE=r'https://app.pluralsight.com/library/courses'
DLPATH, USERNAME, PASSWORD = "", "", ""

USERNAME_INPUT=r'//*[@id="Username"]'
PASSWORD_INPUT=r'//*[@id="Password"]'
LOGIN_SUBMIT=r'//*[@id="login"]'
DOWNLOAD_EXERCISE_FILE=r'//*[@id="ps-main"]/div/div[2]/section/div[3]/div/div/button'
ALT_DOWNLOAD_EXERCISE_FILE=r'/html/body/div[1]/div[3]/div/div[2]/section/div[4]/div/div/button'


def set_driver():
    """Preparing a Chromoium browser instance ready for downloading
    course exercise files.
    
    Returns:
        WebDriver -- Selenium WebDriver object for Chromium
    """
    chrome_options = Options()
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


def wait_for_access(driver, XPATH, timer=20):
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


def login_routine(driver, LOGIN_URL):
    """Handles WebDriver login in to Pluralsight
    
    Arguments:
        driver {WebDriver} -- WebDriver object to use
        LOGIN_URL {str} -- Login url
    """
    driver.get(LOGIN_URL)
    wait_for_access(driver, PASSWORD_INPUT)
    driver.find_element_by_xpath(USERNAME_INPUT).send_keys(USERNAME)
    driver.find_element_by_xpath(PASSWORD_INPUT).send_keys(PASSWORD)
    driver.find_element_by_xpath(LOGIN_SUBMIT).click()


def download_routine(driver, course, sleep_time=2):
    """Handling the download of exercise files from Pluralsight
    
    Arguments:
        driver {WebDriver} -- WebDriver object to use
        excercise_url {str} -- Exercise files page url
    """
    sleep(sleep_time)
    excercise_url = COURSE_BASE + '/' + course + '/' + 'exercise-files'
    driver.get(excercise_url)
    try:
        wait_for_access(driver, DOWNLOAD_EXERCISE_FILE, timer=sleep_time).click()
    except TimeoutException:
        try:
            wait_for_access(driver, ALT_DOWNLOAD_EXERCISE_FILE, timer=sleep_time).click()

        except TimeoutException:
            print(course, 'did not succeeded. Tagging it ...')
            with open(os.path.join(DLPATH,'tagged_courses.txt'), 'at') as f:
                f.write(course + '\n')


def already_tagged_courses():
    """Courses get tagged if they are downloaded or if they not contain 
    any valid course materials for this subscription.
    
    Returns:
        [str] -- List of tagged course_ids
    """
    zip_reg = re.compile(r'.+\.zip$')
    name_reg = re.compile(r'.*(?=.zip)')
    failed_downloads = os.path.join(DLPATH, 'tagged_courses.txt')

    course_tags = []
    if os.path.exists(failed_downloads):
        with open(failed_downloads, 'rt') as f:
            for line in f.readlines():
                course_tags.append(line.strip())
    for element in os.listdir(DLPATH):
        if zip_reg.match(element):
            course_tags.append(name_reg.search(element).group())

    return course_tags


def main():
    """Main execution
    Using Selenium WebDriver along with courselist.txt and Pluralsight
    credentials to automate the downloading process of exercise files.
    """
    global DLPATH, USERNAME, PASSWORD

    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    DLPATH = os.path.join(scriptpath,"exercise_files")
    USERNAME, PASSWORD = get_usr_pw()
    courses = get_courses(os.path.dirname(os.path.abspath(sys.argv[0])))

    if os.path.exists(DLPATH):
        course_tags = already_tagged_courses()
    else:
        course_tags = []

    driver = set_driver()
    set_directory(DLPATH)
    login_routine(driver, LOGIN_URL)
    for course in courses:
        if course[0] not in course_tags:
            download_routine(driver, course[0])
        else:
            print(course[0], "is tagged, skipping it.")


if __name__ == "__main__":
    main()