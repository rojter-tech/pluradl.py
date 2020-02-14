import os, re, json

# Metadata
RAW_URL = r'https://www.pluralsight.com/courses/'
HTML_FILE = os.path.join("data", "search_results.html")
JSON_OUTPUT_FILE = os.path.join("json_output", "courses.json")


def lookaround_tags(start_tag, end_tag):
    lookbehind = r'(?<=' + start_tag + r')'
    lookahead = r'(?=' + end_tag + r')'
    lookaround = re.compile(lookbehind + r'.*?' + lookahead)
    return lookaround


def store_dict_as_json(filepath, dictionary):
    path = os.path.dirname(filepath)
    if not os.path.exists(path):
        os.mkdir(path)
    with open(filepath, 'wt') as f:
        json.dump(dictionary, f, sort_keys=True, indent=4)


def scrape_and_store_courses():
    # Search results encapsulation
    search_tag=r'<div class="search-result__title">'
    div_tag=r'</div>'
    result_lookaround = lookaround_tags(search_tag, div_tag)

    # Encapsulation within search results
    quote = r'"'
    gt = r'>'
    a_tag = r'</a>'
    courseid_lookaround = lookaround_tags(RAW_URL, quote)
    title_lookaround = lookaround_tags(gt, a_tag)

    # Parse the content of data/search_results.html and put data in a dicionary
    courses = {}
    with open(HTML_FILE, 'rt') as f:
        for line in f.readlines():
            search_line = result_lookaround.search(line)
            if search_line:
                title_tag = search_line.group()
                courseid = courseid_lookaround.search(title_tag).group()
                title = title_lookaround.search(title_tag).group()
                courses[courseid] = title
    
    # Store dictionary as json
    store_dict_as_json(JSON_OUTPUT_FILE, courses)


if __name__ == "__main__":
    scrape_and_store_courses()