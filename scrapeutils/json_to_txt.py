from __future__ import unicode_literals
import json, os, re
JSON_FILE = os.path.join("data", "courses.json")

with open(JSON_FILE, 'rt') as f:
    json_load = json.load(f)

course_ids = list(json_load.keys())

search_string = r'kali-linux'
results_path = os.path.join("filtered_results", search_string + r'.txt')

with open(results_path, 'wt') as f:
    for course_id in course_ids:
        search = re.search(search_string, course_id)
        if search:
            f.write(course_id + '\r\n')
