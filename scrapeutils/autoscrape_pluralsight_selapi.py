from __future__ import unicode_literals
import os, json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
url = r'https://www.pluralsight.com/search?categories=course&sort=title'

driver = webdriver.Firefox()
driver.get(url)
load_more_results = r'jQuery(".button--secondary").click()'

for i in range(50000):
    driver.execute_script(load_more_results)

course_results = driver.find_elements_by_class_name("search-result__info")

courses = {}
for course in course_results:
    url_tag = course.find_element_by_class_name("cludo-result")
    url = url_tag.get_attribute('href')
    name = url_tag.text
    author = course.find_element_by_class_name("search-result__author").text
    level = course.find_element_by_class_name("search-result__level").text
    date = course.find_element_by_class_name("search-result__date").text
    length = course.find_element_by_class_name("search-result__length").text
    try:
        rating = course.find_element_by_class_name("search-result__rating").text
    except NoSuchElementException:
        rating = "none"
    
    thiscourse = {}
    thiscourse["url"] = url.strip()
    thiscourse["name"] = name.strip()
    thiscourse["author"] = author.split('by ')[-1]
    thiscourse["level"] = level.strip()
    thiscourse["date"] = date.strip()
    thiscourse["length"] = length.strip()
    thiscourse["rating"] = rating.strip()

    course_id = url.split('/')[-1]
    course_id = str(course_id.strip())
    courses[course_id] = thiscourse
    print('Done processing',course_id)

driver.close()

datapath = os.path.join('..', 'data')
if not os.path.exists(datapath):
    os.mkdir(datapath)

with open(os.path.join('data', 'pluralsight.json'), 'wt') as f:
    json.dump(courses, f, indent=4)
