import sys, os, re, getpass, io
from subprocess import Popen, PIPE, STDOUT
if sys.version_info[0] <3:
    raise Exception("Must be using Python 3")

# IMPORTANT SETTINGS TO PREVENT SPAM BLOCKING OF YOUR ACCOUNT/IP AT PLURALSIGHT #
SLEEP_INTERVAL = 150 #                                                          #
SLEEP_OFFSET = 50    #               Change this at your own risk.              #
RATE_LIMIT = "1M"    #                                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Global defaults
DLPATH, USERNAME, PASSWORD = "", "", ""
SUBTITLE = False

PLURAURL = "https://app.pluralsight.com/library/courses/"

def set_subtitle():
    global SUBTITLE
    subtitle_flags = ("--sub", "--subtitle", "-s",
                      "--SUB", "--SUBTITLE", "-S")
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in subtitle_flags:
                SUBTITLE = True
                print("Subtitles will be appended to videoclips")


def get_usr_pw():
    """Requesting credentials from the user
    
    Raises:
        ValueError: User enters an empty password too many times
    """
    global USERNAME
    global PASSWORD

    print("Enter you Pluralsight credentials")
    for i in range(3):
        u0 = input("Enter username: ")
        if u0 == "":
            print("Username cannot be empty, enter username again")
            continue
        else:
            USERNAME = u0
        
        print("Enter password (will not be displayed)")
        p0 = getpass.getpass(': ')
        if p0 != "":
            PASSWORD = p0
            break
        else:
            print('Password cannot be empty, enter password again')
    else:
        raise ValueError('Username or password was not given.')


def cli_request(command, logpath):
    """Invokes an OS command line request
    
    Arguments:
        command {str} -- Full command string
        logpath {str} -- Path to stdout/stderror log file
    
    """
    os.chdir(os.path.dirname(logpath))
    print("Logging stdout/stderror to:\n" + logpath + "\n")

    with Popen(command, shell=True, stdout=PIPE, stderr=STDOUT) as process, \
        open(file=logpath, mode='wt') as logfile:
            for line in io.TextIOWrapper(process.stdout, newline=''):
                sys.stdout.write(line)
                logfile.write(line)
                logfile.flush()


def get_playlist_flag(digits):
    """Using appended digits in courselist.txt to set playlist option.
    
    Arguments:
        digits {[int]} -- List with playlist indicies
    """
    n = len(digits)
    if n == 0:
        return ""
    elif n == 1:
        return "--playlist-end " + digits[0]
    elif n == 2:
        return "--playlist-start " + digits[0] + " --playlist-end " + digits[1]
    else:
        print("Could not determine playlist interval. Downloading all videos ...")
        return ""


def get_subtitle_flag():
    if SUBTITLE:
        return "--write-sub"
    else:
        return ""


def get_cli_command(course_id, pl_digits, sleep_interval=SLEEP_INTERVAL, sleep_offset=SLEEP_OFFSET, rate_limit=RATE_LIMIT):
    """Putting together youtube-dl CLI command used to invoke the download requests.
    
    Arguments:
        course_id {str} -- Course identifier
    
    Keyword Arguments:
        sleep_interval {int} -- Minimum sleep time between video downloads (default: {150})
        sleep_offset {int} -- Randomize sleep time up to minimum sleep time plus this value (default: {50})
        rate_limit {str} -- Download speed limit (use "K" or "M" ) (default: {"1M"})
    
    Returns:
        str -- youtue-dl CLI command
    """
    # Quote and space char
    # # # # # # # # # # # #
    qu = '"';  sp = ' '   # 
    # Download parameters #
    pluraurl = PLURAURL
    username = qu + USERNAME + qu
    password = qu + PASSWORD + qu
    filename_template = qu + "%(playlist_index)s-%(chapter_number)s-%(title)s-%(resolution)s.%(ext)s" + qu
    minsleep = sleep_interval
    
    # CMD Tool # # # # # #
    tool = "youtube-dl"  #
    # Flags - useful settings when invoking download request
    usr =  "--username" + sp + username
    pw =  "--password" + sp + password
    minsl =  "--sleep-interval" + sp + str(minsleep)
    maxsl =  "--max-sleep-interval" + sp + str(minsleep + sleep_offset)
    lrate = "--limit-rate" + sp + rate_limit
    fn =  "-o" + sp + filename_template
    vrb =   "--verbose"
    pllst = get_playlist_flag(pl_digits)
    sub = get_subtitle_flag()
    url = qu + pluraurl + course_id + qu

    # Join command
    cli_components = [tool, usr, pw, minsl, maxsl, lrate, fn, vrb, pllst, sub, url]
    command = sp.join(cli_components)

    return command


def pluradl(course):
    """Handling the video downloading requests for a single course
    
    Arguments:
        course {str} -- Course identifier
    
    Returns:
        str -- youtue-dl CLI command
    """
    course_id = course[0]
    pl_digits = course[1]
    # OS parameters - Creates course path and sets current course directory
    coursepath = os.path.join(DLPATH,course_id)
    if not os.path.exists(coursepath):
        os.mkdir(coursepath)
    os.chdir(coursepath)

    command = get_cli_command(course_id, pl_digits)
    
    # Execute command and log stdout/stderror
    logile = course_id + ".log"
    logpath = os.path.join(coursepath,logile)
    cli_request(command, logpath)


def download_courses(courses):
    """Dowloading all courses listed in courselist.txt
    
    Arguments:
        courses {[type]} -- List of course ID
    
    """
    for course in courses:
        pluradl(course)


def get_courses(scriptpath):
    """Parsing courselist.txt separating course data.
    
    Arguments:
        scriptpath {str} -- Absolute path to script directory
    
    Returns:
        [(str, [int])] -- List of course identifiers exposed by courselist.txt
    """
    def _parse_line(line):
        course_id = ""
        digits = []

        input_chunks = re.findall(r'[\S]{1,}', line)
        for chunk in input_chunks:
            if re.search(r'[\D]{1,}', chunk):
                course_id = chunk
            else:
                digits.append(int(chunk))
        digits.sort()

        return course_id, digits
    # courses textfile prelocated inside script directory
    filelist = "courselist.txt"
    
    # Loops the list's lines and stores it as a python list
    filepath = os.path.join(scriptpath,filelist)
    courses = []
    try:
        with open(filepath, 'r+') as file:
            for line in file.readlines():
                if re.search(r'\S', line):
                    course_id, digits = _parse_line(line)
                    courses.append((course_id, digits))
        return courses
    except FileNotFoundError:
        print("There is no courselist.txt in script path. Terminating script ...")


def flag_parser():
    """Argument handling of 4 or more arguments, interpreting arguments
    as flags with associated values.
    
    Returns:
        Bool -- Validation of argument input
    """
    if len(sys.argv) < 5:
        return False
    
    global USERNAME
    global PASSWORD
    global SUBTITLE

    usn_psw_flag_state = False
    flag_states = {"usn":[False],"psw":[False]}
    flag_inputs = {}
    username_flags = ("--user", "--username", "-u")
    password_flags = ("--pass", "--password", "-p")
    
    for arg in sys.argv[1:]:
        if arg in username_flags:
            flag_states["usn"][0] = True
            flag_states["usn"].append(arg)
        if arg in password_flags:
            flag_states["psw"][0] = True
            flag_states["psw"].append(arg)
    
    if flag_states["usn"][0] and flag_states["psw"][0]:
        usn_psw_flag_state = True

    arg_string = ' '.join(sys.argv[1:])
    for key in flag_states.keys():
        if flag_states[key][0]:
            for flag in flag_states[key][1:]:
                lookbehind = r"(?<=" + flag + r' ' +  r')'
                lookbehind+=r".*?[\w]{1,}"
                user_input = re.findall(lookbehind, arg_string)
                if user_input:
                    user_input=user_input[0].strip()
                    if user_input[0] != '-':
                        flag_inputs[key] = user_input
                        break
    
    if (not "usn" in flag_inputs.keys()) or (not "psw" in flag_inputs.keys()):
        usn_psw_flag_state = False
    
    if usn_psw_flag_state:
        USERNAME = flag_inputs["usn"]
        PASSWORD = flag_inputs["psw"]
        return True
    else:
        return False


def arg_parser():
    """Handling of simple username and password argument input.
    
    Returns:
        Bool -- Validation of argument input
    """
    if len(sys.argv) < 3:
        return False
    global USERNAME
    global PASSWORD

    username = sys.argv[1]
    password = sys.argv[2]
    if username[0] != '-' and password[0] != '-':
        USERNAME = sys.argv[1]
        PASSWORD = sys.argv[2]
        return True
    else:
        return False


def main():
    """Main execution
    Using command line to store username and password, loops
    through the course IDs and invoking download requests.
    """
    global DLPATH

    if flag_parser():
        print("Executing by flag input ..\n")
    elif arg_parser():
        print("Executing by short input ..\n")
    else:
        get_usr_pw()
    
    set_subtitle()

    # Script's absolute directory path
    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Download directory path
    dldirname = "Courses"
    DLPATH = os.path.join(scriptpath,dldirname)
    if not os.path.exists(DLPATH):
        os.mkdir(DLPATH)

    # Looping through the courses determined by get_courses() invoking download requests
    courses = get_courses(scriptpath)
    if courses:
        download_courses(courses)

if __name__ == "__main__":
    main()
