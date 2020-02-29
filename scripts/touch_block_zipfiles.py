import os, sys, re

stored_location = "/media/MediaShare/Video/Education/Programming/PluralSight/_Course-Materials/"
exercise_dir = os.path.join('..','exercise_files')
zip_reg = re.compile(r'.+\.zip$')
name_reg = re.compile(r'.*(?=.zip)')

course_tags = []
for element in os.listdir(stored_location):
    if zip_reg.match(element):
        course_tags.append(name_reg.search(element).group())

if not os.path.exists(exercise_dir):
    os.mkdir(exercise_dir)

for course in course_tags:
    file_name = course + '.zip'
    with open(os.path.join(exercise_dir, file_name), 'wt') as f: f.close

