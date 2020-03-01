from __future__ import unicode_literals
import os, re,sqlite3
import pandas as pd
import numpy as np
from sqlite3 import Error
from html.parser import HTMLParser

HTML_DATA = os.path.join("...", "data", "search_results.html")
DB_FILE = os.path.join("...", "data", "courses.db")
course_params = []
course_id = "";


class SearchHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            value = attr[1]
            if re.search(r'courses', value):
                global course_id
                course_id = value.split(r'/')[-1]
                course_params.append(value)

    def handle_data(self, data):
        data = str(data).strip()
        if data:
            course_params.append(data)


def outer_search_result(HTML_DATA):
    read_state=False; track=0; search_snippets=[]
    with open(HTML_DATA, 'rt') as f:
        for line in f.readlines():
            if re.search(r'class="search-result columns"', line):
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


def populate_dictionary(parser, search_snippets):
    global course_params
    global course_id
    search_dictionary = {}
    for snippet in search_snippets:
        course_id = ""; course_params = []
        parser.feed(snippet)
        search_dictionary[course_id] = course_params
    return search_dictionary


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn


if __name__ == '__main__':
    search_snippets = outer_search_result(HTML_DATA)
    parser = SearchHTMLParser()
    search_dictionary = populate_dictionary(parser, search_snippets)

    column_data = []
    for key, values in search_dictionary.items():
        this_entry = []
        this_entry.append(key)
        for val in values:
            this_entry.append(val)
        if len(this_entry) < 8:
            this_entry.append("None")
            this_array = np.array(this_entry)
            column_data.append(this_array)
        elif len(this_entry) == 8:
            this_array = np.array(this_entry)
            column_data.append(this_array)

    data = pd.DataFrame(data=column_data, columns=['id','url','title','author','level','date','length', 'rating']).set_index('id')

    con = create_connection(DB_FILE)
    data.to_sql('courses', con=con, if_exists='replace')
    con.close
