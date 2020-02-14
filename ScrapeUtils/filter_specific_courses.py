import json, os, re
JSON_FILE = os.path.join("json_output", "courses.json")

with open(JSON_FILE, 'rt') as f:
    json_load = json.load(f)

course_ids = list(json_load.keys())

big_data_path = os.path.join("filtered_results", "big_data.txt")

with open(big_data_path, 'wt') as f:
    for course_id in course_ids:
        search = re.search(r'big-data', course_id)
        if search:
            f.write(course_id + '\r\n')