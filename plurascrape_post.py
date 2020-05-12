from plura_dl.scrapeutils import (
    store_dict_as_json,
    lookaround_tags
)

import json, os, re, requests, codecs, time
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
json_in = os.path.join(SCRIPTPATH, "data", "courses.json")
JSON_FILE = os.path.abspath(json_in)
JSON_OUTPUT = os.path.join(SCRIPTPATH, "data", "courses_d.json")

def grab_and_update_course_data():
    with open(JSON_FILE, 'rt') as f:
        json_load = json.load(f)
    with open(JSON_OUTPUT, 'rt') as f:
        json_output = json.load(f)
    course_ids = list(json_load.keys())
    for course in course_ids:
        try:
            description = json_output[course]["description"]
        except:
            pass
        json_output[course] = json_load[course]
        json_output[course]["description"] = description
    return course_ids, json_output

def filter_descriptions(course_ids, json_load):
    new_course_ids = []
    for course in course_ids:
        description = json_load[course]["description"]
        if description == "":
            new_course_ids.append(course)
    return new_course_ids

def main():
    course_ids, json_load = grab_and_update_course_data()
    course_ids = filter_descriptions(course_ids, json_load)

    def _case_description(text):
        line_segments = text.split('\n')
        i=0
        for segment in line_segments:
            i+=1
            if re.search(r'Description', segment):
                formatted_desciption = "".join(line_segments[i:]).strip()
                break
        return formatted_desciption
    
    start = time.time(); i=0; count_desciptions = 0;
    for course_id in course_ids:
        url = json_load[course_id]["url"]
        r = requests.get(url)
        scan_next = False
        for line in r.text.split('\n'):
            if scan_next:
                if re.search(r'<p>', line) and re.search(r'</p>', line):
                    formatted_description = lookaround_tags(r'<p>', r'</p>').search(line).group()
                    json_load[course_id]["description"]  = formatted_description
                    count_desciptions+=1
                    break
            if re.search(r'<h6>Description</h6>', line):
                scan_next = True
        i+=1
        print("Iteration:", i, "performed in:", time.time() - start, "seconds.")
        print("Sucessfully loaded desciptions:", count_desciptions)
        print("")
    
    store_dict_as_json(json_load, JSON_OUTPUT)

if __name__ == "__main__":
    main()