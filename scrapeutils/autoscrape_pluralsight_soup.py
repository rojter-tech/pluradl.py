from __future__ import unicode_literals
import os, json, re, sys, codecs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
if os.name == 'nt':
    clear = lambda: os.system('cls')
elif os.name == 'posix':
    clear = lambda: os.system('clear')
else:
    clear = lambda: None

SEARCH_URL = r'https://www.pluralsight.com/search?categories=course&sort=title'
JSON_OUTPUT_FILE = os.path.join('..', "data", "courses.json")
LOAD_MORE_RESULTS = r'jQuery(".button--secondary").click()'
RESULT_BUTTON=r'//*[@id="search-results-section-load-more"]'


def set_driver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=640x360")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Firefox(options=firefox_options)
    return driver


def wait_for_access(driver, XPATH, timer=10):
    element = WebDriverWait(driver, timer).until(
    EC.element_to_be_clickable((By.XPATH, XPATH)))
    return element


def get_source(n_pages=500):
    driver = set_driver()
    driver.get(SEARCH_URL)

    for i in range(n_pages):
        try:
            wait_for_access(driver, RESULT_BUTTON)
            if i > 0:
                clear()
                print("Loading more results " + i*'.')
            driver.execute_script(LOAD_MORE_RESULTS)
            print("Loaded 25 courses from resultpage","{:03d}".format(i+1), "of ~385.", end=' ')
        except TimeoutException:
            print('No more results could be found. Preparing data ...')
            break
    print("Finalizing reading from source.")
    for i in range(5000):
        driver.execute_script(LOAD_MORE_RESULTS)
    print('')
    output_html = driver.page_source
    driver.close()
    return output_html


def get_course_elements(course):
    title = course.find("div", class_="search-result__title")
    author = course.find("div", class_="search-result__author")
    level = course.find("div", class_="search-result__level")
    date = course.find("div", class_="search-result__date")
    length = course.find("div", class_="search-result__length")
    rating = course.find("div", class_="search-result__rating")
    return title, author, level, date, length, rating


def get_length(length_element):
    length_text = length_element.get_text()
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


def get_course_elements_texts(course_elements):
    title = course_elements[0].get_text()
    url = course_elements[0].find('a').get('href')
    courseid = url.split('/')[-1]
    author = course_elements[1].get_text()
    level = course_elements[2].get_text()
    date = course_elements[3].get_text()
    length = get_length(course_elements[4])
    rating = get_rating(course_elements[5])
    return courseid, url, title, author, level, date, length, rating


def get_course_dictionary(course_texts):
    thiscourse = {}
    thiscourse["url"] = course_texts[1].strip()
    thiscourse["title"] = course_texts[2].strip()
    thiscourse["author"] = course_texts[3].strip().split('by ')[-1]
    thiscourse["level"] = course_texts[4].strip()
    thiscourse["date"] = course_texts[5].strip()
    thiscourse["length"] = course_texts[6]
    thiscourse["rating"] = course_texts[7]
    return thiscourse


def store_dict_as_json(dictionary, filepath):
    path = os.path.dirname(filepath)
    if not os.path.exists(path):
        os.mkdir(path)
    with codecs.open(filepath, 'w', "utf-8") as f:
        json_string = json.dumps(dictionary, sort_keys=True, indent=4, ensure_ascii=False)
        f.write(json_string)

def main():
    print(JSON_OUTPUT_FILE)
    if os.path.exists(JSON_OUTPUT_FILE):
        with codecs.open(JSON_OUTPUT_FILE, 'r', 'utf-8') as json_file:
            courses = json.load(json_file)
    else:
        courses = {}
    print("Loading web driver ...")
    source_data = get_source(n_pages=400)
    soup = BeautifulSoup(source_data, 'html.parser')
    course_results = soup.find_all("div", class_="search-result__info")
    i=0
    out=sys.stdout
    print("Processing course metadata ...", flush=True, end='')
    for this_course in course_results:
        if i%200 == 0:
            msg = '.'
            out.write(msg)
        i+=1
        course_elements = get_course_elements(this_course)
        course_texts = get_course_elements_texts(course_elements)
        courses[course_texts[0]] = get_course_dictionary(course_texts)
    print('')
    print('Loaded', len(courses), 'courses.', 'Saving results to', JSON_OUTPUT_FILE)
    store_dict_as_json(courses, JSON_OUTPUT_FILE)
    print('Done.')


if __name__ == "__main__":
    main()
