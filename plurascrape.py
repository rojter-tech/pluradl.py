from plura_dl.scrapeutils import (
    os,
    sys,
    out,
    time,
    load_stored_json,



    get_course_dictionary,
    store_dict_as_json
)
from plura_dl.dependentutils import (
    BeautifulSoup,
    get_courselist_source,
    get_course_elements,
    get_course_elements_texts,
)

SCRIPTPATH=os.path.dirname(os.path.abspath(sys.argv[0]))
JSON_OUTPUT_FILE = os.path.abspath(os.path.join(SCRIPTPATH, "data", "courses.json"))
SEARCH_URL = r'https://www.pluralsight.com/search?categories=course&sort=title'


def main():
    start = time()
    course_dict = load_stored_json(JSON_OUTPUT_FILE)
    source_data = get_courselist_source(SEARCH_URL, n_pages=400, finish_rounds=100)
    out.write("Parsing html data ... "); out.flush()
    soup = BeautifulSoup(source_data, 'html.parser')
    course_results = soup.find_all("div", class_="search-result__info")
    out.write("Done.\n"); out.flush()
    i=0
    out.write("Processing course metadata ."); out.flush()
    for this_course in course_results:
        if i%400 == 0:
            out.write('.'); out.flush()
        i+=1
        course_elements = get_course_elements(this_course)
        course_texts = get_course_elements_texts(course_elements)
        course_dict[course_texts[0]] = get_course_dictionary(course_texts)
    msg = ' Loaded ' + str(len(course_dict)) + ' courses.' + '\nSaving results to ' + JSON_OUTPUT_FILE
    out.write(msg); out.flush()
    store_dict_as_json(course_dict, JSON_OUTPUT_FILE)
    end = time()
    timedelta = end - start
    minutes = int(timedelta/60)
    seconds = int(timedelta%60)
    out.write('\nDone scraping courses in ' + str(minutes) + 'm' + str(seconds) + 's' + '.\n'); out.flush()


if __name__ == "__main__":
    main()
