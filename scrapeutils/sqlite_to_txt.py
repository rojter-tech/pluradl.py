from __future__ import unicode_literals
import sqlite3, os
from sqlite3 import Error

DB_FILE = os.path.join("...", "data", "courses.db")
ALL_COURSES_OUTPUT = os.path.join('filtered_results', 'all_courses.txt')
BEGINNER_COURSES_OUTPUT = os.path.join('filtered_results', 'beginner_courses.txt')
INTERMEDIATE_COURSES_OUTPUT = os.path.join('filtered_results', 'intermediate_courses.txt')
ADVANCED_COURSES_OUTPUT = os.path.join('filtered_results', 'advanced_courses.txt')

def create_connection(db_file, con=None):    
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)
 
    return con

def select_all_courses(con, table='courses'):
    cur = con.cursor()
    cur.execute("SELECT id FROM " + table)
 
    rows = cur.fetchall()
    n_rows = len(rows)
    print("There is", n_rows,"rows in the",table,"table.")

    return rows

def select_beginner_courses(con, table='courses'):
    cur = con.cursor()
    cur.execute("SELECT id FROM " + table + " WHERE level='Beginner'")
 
    rows = cur.fetchall()
    n_rows = len(rows)
    print("There is", n_rows,"beginner courses in the",table,"table.")

    return rows

def select_intermediate_courses(con, table='courses'):
    cur = con.cursor()
    cur.execute("SELECT id FROM " + table + " WHERE level='Intermediate'")
 
    rows = cur.fetchall()
    n_rows = len(rows)
    print("There is", n_rows,"intermediate courses in the",table,"table.")

    return rows

def select_advanced_courses(con, table='courses'):
    cur = con.cursor()
    cur.execute("SELECT id FROM " + table + " WHERE level='Advanced'")
 
    rows = cur.fetchall()
    n_rows = len(rows)
    print("There is", n_rows,"advanced courses in the",table,"table.")

    return rows

con = create_connection(DB_FILE)
all_courses = select_all_courses(con)
beginner_courses = select_beginner_courses(con)
intermediate_courses = select_intermediate_courses(con)
advanced_courses = select_advanced_courses(con)
con.close

with open(ALL_COURSES_OUTPUT, 'wt') as f:
    for course in all_courses:
        f.write(course[0]+'\n')

with open(BEGINNER_COURSES_OUTPUT, 'wt') as f:
    for course in beginner_courses:
        f.write(course[0]+'\n')

with open(INTERMEDIATE_COURSES_OUTPUT, 'wt') as f:
    for course in intermediate_courses:
        f.write(course[0]+'\n')

with open(ADVANCED_COURSES_OUTPUT, 'wt') as f:
    for course in advanced_courses:
        f.write(course[0]+'\n')