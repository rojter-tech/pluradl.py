import os, sys, re, json, shutil

exercise_path = os.path.abspath(os.path.join('..','exercise_files'))
json_file_path = os.path.abspath(os.path.join('..', 'data', 'courses.json'))


def load_json_dict(json_file_path):
    with open(json_file_path, 'rt') as json_file:
        course_dict = json.load(json_file)
    return course_dict


def local_course_materials(exercise_path):
    zip_reg = re.compile(r'.+\.zip$')
    name_reg = re.compile(r'.*(?=.zip)')
    
    course_tags = []
    for element in os.listdir(exercise_path):
        if zip_reg.match(element):
            course_tags.append(name_reg.search(element).group().strip())
    return course_tags


def create_dir(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def create_dir_struct(exercise_path, level):
    create_dir(exercise_path)
    os.chdir(exercise_path)
    create_dir('Unknown')
    level_path = os.path.join(exercise_path, level)
    create_dir(level_path)
    os.chdir(level_path)
    create_dir('0-9')
    create_dir('a-d')
    create_dir('e-h')
    create_dir('i-l')
    create_dir('m-p')
    create_dir('q-t')
    create_dir('u-z')


def match_move(regex, first_char, source, target):
    if re.match(regex, first_char):
        shutil.move(source, target)


def trasfer_files(first_char, file_source, level_path):
    match_move(r'\d', first_char, file_source, os.path.join(level_path, '0-9'))
    match_move(r'[a-d]', first_char, file_source, os.path.join(level_path, 'a-d'))
    match_move(r'[e-h]', first_char, file_source, os.path.join(level_path, 'e-h'))
    match_move(r'[i-l]', first_char, file_source, os.path.join(level_path, 'i-l'))
    match_move(r'[m-p]', first_char, file_source, os.path.join(level_path, 'm-p'))
    match_move(r'[q-t]', first_char, file_source, os.path.join(level_path, 'q-t'))
    match_move(r'[u-z]', first_char, file_source, os.path.join(level_path, 'u-z'))


def sort_within_level(course_zip_id, exercise_path, level):
        zip_file = course_zip_id+'.zip'
        file_source = os.path.join(exercise_path, zip_file)
        first_char = course_zip_id[0]
        os.chdir(exercise_path)
        level_path = os.path.join(exercise_path,level)
        trasfer_files(first_char, file_source, level_path)

def main():
    count=0
    course_dict = load_json_dict(json_file_path)

    create_dir_struct(exercise_path, 'Beginner')
    create_dir_struct(exercise_path, 'Intermediate')
    create_dir_struct(exercise_path, 'Advanced')

    os.chdir(exercise_path)
    for course_zip_id in local_course_materials(exercise_path):
        try:
            this_json = course_dict[course_zip_id]
            level = this_json['level']
            sort_within_level(course_zip_id, exercise_path, level)
        except KeyError:
            count+=1
            print(course_zip_id, '|' ,'not in list')
            shutil.move(course_zip_id+'.zip', 'Unknown')

    print(count, 'missing courses in db')
    print('courses in loaded dicionary', len(course_dict))


if __name__ == "__main__":
    main()