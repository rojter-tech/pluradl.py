import os, json, re, datetime
from selenium import webdriver
if not os.path.exists('data'):
    os.mkdir('data')

SCRAPE_URL = r'https://www.pluralsight.com/search?categories=course&sort=title'
HTML_OUTPUT_FILE = os.path.join("data", "search_results.html")
JSON_OUTPUT_FILE = os.path.join("data", "courses.json")


def load_and_save_html(SCRAPE_URL, HTML_OUTPUT_FILE):
    driver = webdriver.Firefox()
    driver.get(SCRAPE_URL)
    load_more_results = r'jQuery(".button--secondary").click()'

    for i in range(50000):
        driver.execute_script(load_more_results)

    with open(HTML_OUTPUT_FILE, 'wt') as f:
        f.write(driver.page_source)

    driver.close()


def outer_search_html(HTML_FILE, class_name):
    read_state=False; track=0; search_snippets=[]
    with open(HTML_FILE, 'rt') as f:
        for line in f.readlines():
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


def lookaround_tags(start_tag, end_tag):
    # Contruct regular expression
    lookbehind = r'(?<=' + start_tag + r')'
    lookahead = r'(?=' + end_tag + r')'
    wildcard = r'.*?'
    regex = "%s%s%s"%(lookbehind,wildcard,lookahead)

    # Compile it and return
    lookaround = re.compile(regex)
    return lookaround


def store_dict_as_json(dictionary, filepath):
    path = os.path.dirname(filepath)
    if not os.path.exists(path):
        os.mkdir(path)
    with open(filepath, 'wt') as f:
        json.dump(dictionary, f, sort_keys=True, indent=4)


def return_lookaround_text(lookaround_search):
    if lookaround_search:
        lookaround_text = lookaround_search.group()
        return lookaround_text


def return_rating(rating_snippet):
    rating = 'none'
    if rating_snippet:
        for row in rating_snippet:
            number = re.search(r'[0-9]{1,}', row)
            if number:
                rating = number.group()
    if rating != 'none':
        return int(rating)
    else:
        return 'none'


def return_length(length_text):
    hours=None; minutes=None;
    if length_text:
        hours_search = re.search(r'[0-9]{1,}(?=h)', length_text)
        minutes_search = re.search(r'[0-9]{1,}(?=m)', length_text)
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


def main():
    load_and_save_html(SCRAPE_URL, HTML_OUTPUT_FILE)
    class_name = r'search-result columns'
    search_snippets = outer_search_html(HTML_OUTPUT_FILE, class_name)

    title_tag=r'<div class="search-result__title">'
    author_tag=r'<div class="search-result__author">'
    level_tag=r'<div class="search-result__level">'
    date_tag=r'<div class="search-result__date">'
    length_tag=r'<div class="search-result__length show-for-large-up">'
    div_tag=r'</div>'; quote = r'"'; gt = r'>'; a_tag = r'</a>'; href=r'href="'

    title_lookaround = lookaround_tags(title_tag, div_tag)
    author_lookaround = lookaround_tags(author_tag, div_tag)
    level_lookaround = lookaround_tags(level_tag, div_tag)
    date_lookaround = lookaround_tags(date_tag, div_tag)
    length_lookaround = lookaround_tags(length_tag, div_tag)
    href_lookaround = lookaround_tags(href, quote)
    gt_a_lookaround = lookaround_tags(gt, a_tag)


    courses = {}
    for html_input in search_snippets:
        thiscourse = {}
        title_outer_text = return_lookaround_text(title_lookaround.search(html_input))
        if title_outer_text:
            url_text = return_lookaround_text(href_lookaround.search(title_outer_text))
            name_text = return_lookaround_text(gt_a_lookaround.search(title_outer_text))
            course_id = url_text.split('/')[-1]
            author_text = return_lookaround_text(author_lookaround.search(html_input))
            level_text = return_lookaround_text(level_lookaround.search(html_input))
            date_text = return_lookaround_text(date_lookaround.search(html_input))
            length_text = return_lookaround_text(length_lookaround.search(html_input))
            lenght = return_length(length_text)
            rating_snippet = outer_search_snippet(html_input, r'search-result__rating')
            rating = return_rating(rating_snippet)

            if author_text and not '{' in author_text:
                thiscourse['url'] = url_text
                thiscourse['name'] = name_text
                thiscourse['author'] = author_text.split('by ')[-1]
                thiscourse['level'] = level_text
                thiscourse['date'] = date_text
                thiscourse['length'] = lenght
                thiscourse['rating'] = rating
                courses[course_id] = thiscourse
    
    store_dict_as_json(courses, JSON_OUTPUT_FILE)


if __name__ == "__main__":
    main()