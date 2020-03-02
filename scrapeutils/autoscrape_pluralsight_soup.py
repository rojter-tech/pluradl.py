from utils import *

SCRIPTPATH=os.path.dirname(os.path.abspath(sys.argv[0]))
JSON_OUTPUT_FILE = os.path.abspath(os.path.join(SCRIPTPATH, '..', "data", "courses.json"))
SEARCH_URL = r'https://www.pluralsight.com/search?categories=course&sort=title'


def main():
    course_dict = load_stored_json(JSON_OUTPUT_FILE)
    print("Loading web driver ...")
    source_data = get_courselist_source(SEARCH_URL, n_pages=1)
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
        course_dict[course_texts[0]] = get_course_dictionary(course_texts)
    print('')
    print('Loaded', len(course_dict), 'courses.', 'Saving results to', JSON_OUTPUT_FILE)
    store_dict_as_json(course_dict, JSON_OUTPUT_FILE)
    print('Done.')


if __name__ == "__main__":
    main()
