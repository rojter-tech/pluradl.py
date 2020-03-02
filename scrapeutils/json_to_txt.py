from __future__ import unicode_literals
import json, os, re, sys

SCRIPTPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
JSON_FILE = os.path.abspath(os.path.join(SCRIPTPATH, "..", "data", "courses.json"))
mode = 'all'

with open(JSON_FILE, 'rt') as f:
    json_load = json.load(f)

course_ids = list(json_load.keys())

search_string = r'kali-linux'

if mode == 'all':
    results_path = os.path.join(SCRIPTPATH, "filtered_results", r"all_courses" + r'.txt')
else:
    results_path = None

if results_path:
    with open(results_path, 'wt') as f:
        for course_id in course_ids:
            if mode == 'search':
                search = re.search(search_string, course_id)
                if search:
                    f.write(course_id + '\r\n')
            elif mode == 'all':
                f.write(course_id + '\r\n')
            else:
                break
