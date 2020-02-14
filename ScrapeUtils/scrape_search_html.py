import os, re, json

url=r'https://www.pluralsight.com/courses/'

def lookaround_tag(start_tag, end_tag):
    lookbehind = r'(?<=' + start_tag + r')'
    lookahead = r'(?=' + end_tag + r')'
    lookaround = re.compile(lookbehind + r'.*?' + lookahead)

    return lookaround

search_tag=r'<div class="search-result__title">'
div_tag=r'</div>'

result_lookaround = lookaround_tag(search_tag, div_tag)
courseid_lookaround = lookaround_tag(url, '"')
title_lookaround = lookaround_tag(r'>', r'</a>')

courses = {}
with open("search_results.html", 'rt') as f:
    for line in f.readlines():
        search_line = result_lookaround.search(line)
        if search_line:
            title_tag = search_line.group()
            courseid = courseid_lookaround.search(title_tag).group()
            title = title_lookaround.search(title_tag).group()
            
            courses[courseid] = title

with open('courses.json', 'wt') as f:
    json.dump(courses, f, sort_keys=True, indent=4)