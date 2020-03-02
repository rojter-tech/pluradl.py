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

############################ GENERAL functions ###########################
##########################################################################

def set_headless_driver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=640x360")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Firefox(options=firefox_options)
    return driver


def get_courselist_source(SEARCH_URL, n_pages=500, finish_rounds=100):
    RESULT_BUTTON=r'//*[@id="search-results-section-load-more"]'
    LOAD_MORE_RESULTS = r'jQuery(".button--secondary").click()'
    driver = set_headless_driver()
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
    for i in range(finish_rounds):
        driver.execute_script(LOAD_MORE_RESULTS)
    print('')
    output_html = driver.page_source
    driver.close()
    return output_html


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


def wait_for_access(driver, XPATH, timer=10):
    element = WebDriverWait(driver, timer).until(
    EC.element_to_be_clickable((By.XPATH, XPATH)))
    return element


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


def load_stored_json(json_path):
    if os.path.exists(json_path):
        with codecs.open(json_path, 'r', 'utf-8') as json_file:
            json_dict = json.load(json_file)
    else:
        json_dict = {}
    
    return json_dict

############################# Regex functions ############################
##########################################################################


def outer_search_html(source_html, class_name):
    read_state=False; track=0; search_snippets=[]
    for line in source_html.split('\n'):
        if re.search(r'class=' + r'"' + class_name + r'"', line):
            read_state = True
            search_result = []
        if read_state:
            search_result.append(line)
            n_open = len(re.findall(r'<div', line))
            n_close = len(re.findall(r'/div>', line))
            track+=n_open;   track-=n_close
            if track == 0:
                read_state = False
                search_snippets.append(''.join(search_result))
    return search_snippets


def outer_search_snippet(snippet, class_name):
    read_state=False; track=0; search_result = None
    for line in snippet.split('\n'):
        if re.search(r'class=' + r'"' + class_name + r'"', line):
            read_state = True
            search_result = []
        if read_state:
            search_result.append(line.strip())
            n_open = len(re.findall(r'<div', line))
            n_close = len(re.findall(r'/div>', line))
            track+=n_open;   track-=n_close
            if track == 0:
                read_state = False
    return search_result


def return_rating(rating_snippet):
    rating = 'none'
    if rating_snippet:
        for row in rating_snippet:
            number = re.search(r'\([0-9]+\)', row)
            if number:
                rating = number.group()
    if rating != 'none':
        return int(rating)
    else:
        return ""


def lookaround_tags(start_tag, end_tag):
    # Contruct regular expression
    lookbehind = r'(?<=' + start_tag + r')'
    lookahead = r'(?=' + end_tag + r')'
    wildcard = r'.*?'
    regex = "%s%s%s"%(lookbehind,wildcard,lookahead)

    # Compile it and return
    lookaround = re.compile(regex)
    return lookaround


def return_lookaround_text(lookaround_search):
    if lookaround_search:
        lookaround_text = lookaround_search.group()
        return lookaround_text

######################## Beautuful soup functions ########################
##########################################################################

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
