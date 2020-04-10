from plura_dl.scrapeutils import (
    os,
    sys,
    re,
    sleep,
    Path,
    clear,
    enter_hibernation,
    extract_user_credentials
)
from plura_dl.dependentutils import (
    TimeoutException,
    set_chrome_driver,
    wait_for_access
)

from selenium.webdriver.chrome.options import Options
from pluradl import get_courses, set_directory
from plura_dl.scrapeutils import extract_user_credentials, Logger

LOGIN_URL=r'https://app.pluralsight.com/id?'
COURSE_BASE=r'https://app.pluralsight.com/library/courses'
DLPATH, USERNAME, PASSWORD = "", "", ""

USERNAME_INPUT=r'//*[@id="Username"]'
PASSWORD_INPUT=r'//*[@id="Password"]'
LOGIN_SUBMIT=r'//*[@id="login"]'
DOWNLOAD_EXERCISE_FILE=r'//*[@id="ps-main"]/div/div[2]/section/div[3]/div/div/button'
ALT_DOWNLOAD_EXERCISE_FILE=r'/html/body/div[1]/div[3]/div/div[2]/section/div[4]/div/div/button'


def login_routine(driver, LOGIN_URL):
    """Handles WebDriver login into Pluralsight
    
    Arguments:
        driver {WebDriver} -- WebDriver object to use
        LOGIN_URL {str} -- Login url
    """
    driver.get(LOGIN_URL)
    wait_for_access(driver, PASSWORD_INPUT)
    driver.find_element_by_xpath(USERNAME_INPUT).send_keys(USERNAME)
    driver.find_element_by_xpath(PASSWORD_INPUT).send_keys(PASSWORD)
    driver.find_element_by_xpath(LOGIN_SUBMIT).click()


def download_routine(driver, course, sleep_time=5):
    """Handling the download of exercise files from Pluralsight
    
    Arguments:
        driver {WebDriver} -- WebDriver object to use
        excercise_url {str} -- Exercise files page url
    """
    sleep(sleep_time)
    excercise_url = COURSE_BASE + '/' + course + '/' + 'exercise-files'
    no_materals_lookup = r'this course has no materials'
    upgrade_lookup = r'Upgrade today'

    driver.get(excercise_url)
    materials_check=True
    try:
        wait_for_access(driver, DOWNLOAD_EXERCISE_FILE, timer=sleep_time).click()
    except TimeoutException:
        try:
            course_text = driver.find_element_by_class_name('l-course-page__content').text
        except:
            course_text = ""
        if re.search(no_materals_lookup, course_text):
            materials_check=False
            print(course, 'did not have any course materials. Tagging it ...')
            with open(os.path.join(DLPATH,'tagged_courses.txt'), 'at') as f:
                f.write(course + '\n')
        elif re.search(upgrade_lookup, course_text):
            materials_check=False
            print(course, 'are not a part of your subscription. Tagging it ...')
            with open(os.path.join(DLPATH,'tagged_courses.txt'), 'at') as f:
                f.write(course + '\n')
        if materials_check:
            try:
                wait_for_access(driver, ALT_DOWNLOAD_EXERCISE_FILE, timer=sleep_time).click()
            except TimeoutException:
                print(course, 'did not succeeded. The course might not be in your subscription or it`s not available anymore. Tagging it ...')
                with open(os.path.join(DLPATH,'failed_courses.txt'), 'at') as f:
                    f.write(course + '\n')


def already_tagged_courses():
    """Courses get tagged if they are already downloaded, if they do 
    not contain any materials at all or if the do not contain authorized  
    materials for used subscription. Getting information from tagged_courses.txt.
    
    Returns:
        [str] -- List of tagged course_ids
    """
    zip_reg = re.compile(r'.+\.zip$')
    name_reg = re.compile(r'.*(?=.zip)')
    tagged_courses = os.path.join(DLPATH, 'tagged_courses.txt')
    course_tags = []
    if os.path.exists(tagged_courses):
        with open(tagged_courses, 'rt') as f:
            for line in f.readlines():
                course_tags.append(line.strip())
    for element in Path(DLPATH).rglob('*.zip'):
        filename = element.name
        if zip_reg.match(filename):
            course_tags.append(name_reg.search(filename).group())
    return course_tags


def main():
    """Main execution
    Using Selenium WebDriver along with courselist.txt and Pluralsight
    credentials to automate the downloading process of exercise files.
    """
    global DLPATH, USERNAME, PASSWORD

    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    DLPATH = os.path.join(scriptpath,"exercise_files")
    USERNAME, PASSWORD = extract_user_credentials()
    print("Setting username to:", USERNAME)
    courses = get_courses(os.path.dirname(os.path.abspath(sys.argv[0])))

    if os.path.exists(DLPATH):
        course_tags = already_tagged_courses()
    else:
        course_tags = []

    courses_to_fetch = []
    for course in courses:
        if course[0] not in course_tags:
            courses_to_fetch.append(course)
        else:
            print(course[0], "is tagged, skipping it.")

    if courses_to_fetch:
        driver = set_chrome_driver(DLPATH)
        set_directory(DLPATH)
        login_routine(driver, LOGIN_URL)
        for course in courses_to_fetch:
            download_routine(driver, course[0], sleep_time=5)
        print("\nEnd of list reached. Downloads might still be in progress.")
        enter_hibernation()
        driver.close()


if __name__ == "__main__":
    main()
