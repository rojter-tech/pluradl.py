from __future__ import unicode_literals
import os, json, re, sys, codecs, getpass
from sys import stdout as out
from time import time, sleep
from pathlib import Path
if os.name == 'nt':
    clear = lambda: os.system('cls')
elif os.name == 'posix':
    clear = lambda: os.system('clear')
else:
    clear = lambda: None


############################### General functions #############################
###############################################################################


class Logger(object):
    """Handling logging mechanism of PluraDL.
    
    Arguments:
        logpath {str} -- Path to logfile
    """
    def __init__(self,logpath):
        self.logpath = logpath
        with open(self.logpath, 'wt') as f: f.close

    def debug(self, msg):
        print(msg)
        with open(self.logpath, 'at') as f: f.write(msg+'\n')

    def warning(self, msg):
        print(msg)
        with open(self.logpath, 'at') as f: f.write(msg+'\n')

    def error(self, msg):
        print(msg)
        with open(self.logpath, 'at') as f: f.write(msg+'\n')


def extract_user_credentials():
    flag_state = _flag_parser()
    arg_state = _arg_parser()
    if flag_state[0]:
        print("Executing by flag input ..")
        USERNAME, PASSWORD = flag_state[1], flag_state[2]
    elif arg_state[0]:
        print("Executing by user input ..")
        USERNAME, PASSWORD = arg_state[1], arg_state[2]
    else:
        USERNAME, PASSWORD = _get_usr_pw()
    return USERNAME, PASSWORD


def _flag_parser():
    """Argument handling of 4 or more arguments, interpreting arguments
    as flags with associated values.
    
    Returns:
        (Bool, str, str) -- Validation of argument input, and credentials.
    """
    if len(sys.argv) < 5:
        return False, "", ""

    def _check_flags(key, flag_states, arg_string=' '.join(sys.argv[1:])):
        for flag in flag_states[key][1:]:
            if flag in all_flags:
                lookaroundflag = r'(?<=' + flag + ' ' +  ')'
                lookaroundflag+=r".*?[\S]+"
        return re.findall(lookaroundflag, arg_string)

    def _check_inputs(key, user_inputs):
        for user_input in user_inputs:
            user_input = user_input.strip()
            if user_input not in (all_flags):
                flag_inputs[key] = user_input
                break # will take the first valid input
    
    usn_psw_flag_state = False
    flag_states = {"usn":[False],"psw":[False]}
    flag_inputs = {}
    username_flags = ("--user", "--username", "-u")
    password_flags = ("--pass", "--password", "-p")
    all_flags=(username_flags+password_flags)
    
    for arg in sys.argv[1:]:
        if arg in username_flags:
            flag_states["usn"][0] = True
            flag_states["usn"].append(arg)
        if arg in password_flags:
            flag_states["psw"][0] = True
            flag_states["psw"].append(arg)
    
    if flag_states["usn"][0] and flag_states["psw"][0]:
        usn_psw_flag_state = True
    
    for key in flag_states.keys():
        if flag_states[key][0]:
            user_inputs = _check_flags(key, flag_states)
            if user_inputs:
                _check_inputs(key, user_inputs)
    
    if (not "usn" in flag_inputs.keys()) or (not "psw" in flag_inputs.keys()):
        usn_psw_flag_state = False
    
    if usn_psw_flag_state:
        USERNAME = flag_inputs["usn"]
        PASSWORD = flag_inputs["psw"]
        return True, USERNAME, PASSWORD
    else:
        return False, "", ""


def _arg_parser():
    """Handling of simple username and password argument input.
    
    Returns:
        (Bool, str, str) -- Validation of argument input, and credentials.
    """
    if len(sys.argv) < 3:
        return False, "", ""

    username = sys.argv[1]
    password = sys.argv[2]
    if username[0] != '-' and password[0] != '-':
        USERNAME = sys.argv[1]
        PASSWORD = sys.argv[2]
        return True, USERNAME, PASSWORD
    else:
        return False, "", ""


def _get_usr_pw():
    """Requesting credentials from the user.
    
    Raises:
        ValueError: User enters an empty password too many times
    """
    print("Enter you Pluralsight credentials")
    for attempt in ["First","Second","Last"]:
        u0 = input("Enter username: ")
        if u0 == "":
            print("Username cannot be empty, enter username again")
            print(attempt, "attempt failed")
            continue
        else:
            USERNAME = u0
        
        print("Enter password (will not be displayed)")
        p0 = getpass.getpass(': ')
        if p0 != "":
            PASSWORD = p0
            return USERNAME, PASSWORD
        else:
            print('Password cannot be empty, enter password again')
    else:
        raise ValueError('Username or password was not given.')


def get_length(length_text):
    hours=None; minutes=None
    if length_text:
        hours_search = re.search(r'[0-9]+(?=h)', length_text)
        minutes_search = re.search(r'[0-9]+(?=m)', length_text)
        if hours_search:
            hours = int(hours_search.group())
        if minutes_search:
            minutes = int(minutes_search.group())
    if hours and minutes:
        time = hours*60 + minutes
    elif hours:
        time = hours*60
    elif minutes:
        time = minutes
    else:
        time = 'none'
    return time


def get_rating(rating_elem):
    if rating_elem:
        rating = re.search(r'[0-9]+', rating_elem.get_text())
        if rating:
            rating = int(rating.group())
        else:
            rating = ""
    else:
        rating = ""
    return rating


def get_course_dictionary(course_texts):
    thiscourse = {}
    thiscourse["url"] = course_texts[1].strip()
    thiscourse["title"] = course_texts[2].strip()
    thiscourse["author"] = course_texts[3].strip().split('by ')[-1]
    thiscourse["level"] = course_texts[4].strip()
    thiscourse["date"] = course_texts[5].strip()
    thiscourse["length"] = course_texts[6]
    thiscourse["rating"] = course_texts[7]
    return thiscourse


def store_dict_as_json(dictionary, filepath):
    path = os.path.dirname(filepath)
    if not os.path.exists(path):
        os.mkdir(path)
    with codecs.open(filepath, 'w', "utf-8") as f:
        json_string = json.dumps(dictionary, sort_keys=True, indent=4, ensure_ascii=False)
        f.write(json_string)


def load_stored_json(json_path):
    if os.path.exists(json_path):
        with codecs.open(json_path, 'r', 'utf-8') as json_file:
            out.write("Loading coursedata from: " + json_path + '\n')
            json_dict = json.load(json_file)
    else:
        json_dict = {}
    
    return json_dict


def enter_hibernation():
    while True:
        userinput = input("Waiting for user input ... [Press Enter to terminate]\n:")
        userinput = input("Do you want to terminate? [y/N]: ")
        if userinput in ['y','Y','yes','YES']:
            print("Terminating ...")
            break
        elif userinput in ['n','N','no','NO']:
            continue
        else:
            userinput = input("Not entering valid option again will terminate. This is you last chance [y/N] :")
            if userinput in ['y','Y','yes','YES']:
                continue
            else:
                print("Terminating ...")
                break


################################ Regex functions ##############################
###############################################################################


def outer_search_html(source_html, class_name):
    read_state=False; track=0; search_snippets=[]
    for line in source_html.split('\n'):
        if re.search(r'class=' + r'"' + class_name + r'"', line):
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


def outer_search_snippet(snippet, class_name):
    read_state=False; track=0; search_result = None
    for line in snippet.split('\n'):
        if re.search(r'class=' + r'"' + class_name + r'"', line):
            read_state = True
            search_result = []
        if read_state:
            search_result.append(line.strip())
            n_open = len(re.findall(r'<div', line))
            n_close = len(re.findall(r'/div>', line))
            track+=n_open;   track-=n_close
            if track == 0:
                read_state = False
    return search_result


def return_rating(rating_snippet):
    rating = 'none'
    if rating_snippet:
        for row in rating_snippet:
            number = re.search(r'\([0-9]+\)', row)
            if number:
                rating = number.group()
    if rating != 'none':
        return int(rating)
    else:
        return ""


def lookaround_tags(start_tag, end_tag):
    # Contruct regular expression
    lookbehind = r'(?<=' + start_tag + r')'
    lookahead = r'(?=' + end_tag + r')'
    wildcard = r'.*?'
    regex = "%s%s%s"%(lookbehind,wildcard,lookahead)

    # Compile it and return
    lookaround = re.compile(regex)
    return lookaround


def return_lookaround_text(lookaround_search):
    if lookaround_search:
        lookaround_text = lookaround_search.group()
        return lookaround_text

