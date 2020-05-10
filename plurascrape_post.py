from plura_dl.scrapeutils import (
    store_dict_as_json
)

import json, os, re, requests, codecs, time

def main():
    SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
    json_in = os.path.join(SCRIPTPATH, "data", "courses.json")
    JSON_FILE = os.path.abspath(json_in)
    JSON_OUTPUT = os.path.join(SCRIPTPATH, "data", "courses_d.json")

    with open(JSON_FILE, 'rt') as f:
        json_load = json.load(f)

    course_ids = list(json_load.keys())

    start = time.time(); i=0
    for course_id in course_ids:
        url = json_load[course_id]["url"]
        r = requests.get(url)
        test = re.search(r'<p>.*</p>', r.text)
        if test:
            description_paragraph = test.group()
            json_load[course_id]["description"] = description_paragraph[3:-4]
        else:
            json_load[course_id]["description"] = ""
        i+=1
        if i%100 == 1:
            print("Iteration:", i, "performed in:", time.time() - start, "seconds.")
        time.sleep(2.5)
    
    store_dict_as_json(json_load, JSON_OUTPUT)

if __name__ == "__main__":
    main()
