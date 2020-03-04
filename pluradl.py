from __future__ import unicode_literals
import sys, os, shutil, re, getpass, io, certifi, plura_dl
from plura_dl import PluraDL
from plura_dl.utils import ExtractorError, DownloadError, std_headers
if sys.version_info[0] <3:
    raise Exception("Must be using Python 3")

certpath = os.path.abspath(certifi.where())
os.environ["SSL_CERT_FILE"] = certpath

std_headers['User-Agent'] = r"Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0"
std_headers['Accept'] = r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
std_headers['Referer'] = r'https://app.pluralsight.com/id/'
std_headers['Host'] = r'app.pluralsight.com'
std_headers['Cache-Control'] = r'max-age=0'
std_headers['Upgrade-Insecure-Requests'] = r'1'
std_headers['TE'] = r'Trailers'
std_headers['DNT'] = r'1'
std_headers['Connection'] = r'keep-alive'
std_headers['Accept-Charset'] = r'ISO-8859-1,utf-8;q=0.7,*;q=0.7'

# IMPORTANT SETTINGS TO PREVENT SPAM BLOCKING OF YOUR ACCOUNT/IP AT PLURALSIGHT # # # #
SLEEP_INTERVAL = 40     # minimum sleep time        #                                 #
SLEEP_OFFSET   = 120    # adding random sleep time  #  Change this at your own risk.  #
RATE_LIMIT     = 10**6  # download rate in bytes/s  #                                 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Global defaults
DLPATH, USERNAME, PASSWORD = "", "", ""
INPROGRESSPATH, FINISHPATH, FAILPATH, INTERRUPTPATH = "", "", "", ""
PDL_OPTS = {}
SUBTITLE = False
FILENAME_TEMPLATE = r"%(playlist_index)s-%(chapter_number)s-%(title)s-%(resolution)s.%(ext)s"
PLURAURL = r"https://app.pluralsight.com/library/courses/"
SCRIPTPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
COOKIEFILE = os.path.join(SCRIPTPATH, 'cookies', 'cookies.txt')
if os.path.exists(COOKIEFILE):
    os.remove(COOKIEFILE)
    pass


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


def set_playlist_options(digits):
    """Using appended digits in courselist.txt to set playlist option.
    
    Arguments:
        digits {[int]} -- List with playlist indicies
    """
    global PDL_OPTS

    n = len(digits)
    if n == 0:
        pass
    elif n == 1:
        print("Downloading video indicies up to",digits[0],"to")
        PDL_OPTS["playlistend"]   = digits[0]
    elif n == 2:
        print("Downloading video indicies from",digits[0],"up to and including",digits[1])
        PDL_OPTS["playliststart"] = digits[0]
        PDL_OPTS["playlistend"]   = digits[1]
    else:
        print("Downloading specific video indicies", digits)
        PDL_OPTS["playlist_items"] = ','.join([str(x) for x in digits])


def move_content(pdl, course_id, coursepath, completionpath):
    """Moves course content to its completion path.
    
    Arguments:
        pdl {PluraDL} -- PluraDL object
        course_id {str} -- [description]
        coursepath {str} -- [description]
        completionpath {str} -- Path where to store content
    """
    finalpath = os.path.join(completionpath, course_id)
    pdl.to_stdout("Moving content to " + finalpath)
    set_directory(completionpath)
    try:
        if os.path.exists(finalpath):
            shutil.rmtree(finalpath)
        shutil.move(coursepath,finalpath)
        if os.path.exists(INPROGRESSPATH):
            shutil.rmtree(INPROGRESSPATH)
    except PermissionError:
        print("Directory still in use, leaving it. Will be fixed in future releases.")


def invoke_download(course_id, course_url, coursepath):
    """Using plura_dl API to invoke download requests with associated parameters.
    
    Arguments:
        course_id {str} -- Course identifier
        course_url {str} -- Playlist url
        coursepath {str} -- Local temporary course storage path
    
    Returns:
        Bool -- Validation of completion level
    """
    with PluraDL(PDL_OPTS) as pdl:
        try:
            # Invoke download
            set_directory(coursepath)
            pdl.download([course_url])

            # Moving content to _finished destination path if the download was sucessful
            pdl.to_stdout("The course '" + course_id + "' was downloaded successfully.")
            finalpath = os.path.join(FINISHPATH, course_id)
            move_content(pdl, course_id, coursepath, FINISHPATH)
            return True

        except ExtractorError:
            # Handling the case of invalid download requests
            pdl.to_stdout("The course '" + course_id + "' may not be a part of your current licence.")
            pdl.to_stdout("Visit " + course_url + " for more information.\n")
            # Moving content to _failed destination 
            move_content(pdl, course_id, coursepath, FAILPATH)
            return True
        
        except DownloadError:
            # Handling the the more general case of download error
            pdl.to_stdout("Something went wrong.")
            pdl.to_stdout("The download request for '" + course_id + "' was forced to terminate.")
            pdl.to_stdout("Double check that " + course_url)
            pdl.to_stdout("exists or that your subscription is valid for accessing its content.\n")
            # Moving content to _failed destination path
            move_content(pdl, course_id, coursepath, FAILPATH)
            return True

        except KeyboardInterrupt:
            # Handling the case of user interruption
            pdl.to_stdout("\n\nThe download stream for '" + course_id + "' was canceled by user.")
            # Moving content to _canceled destination 
            move_content(pdl, course_id, coursepath, INTERRUPTPATH)
            return False


def pluradl(course):
    """Handling the video downloading requests for a single course.
    
    Arguments:
        course {(str, [])} -- Course identifier and playlist parameters
    
    Returns:
        str -- youtue-dl CLI command
    """
    global PDL_OPTS

    # Course metadata
    course_id = course[0]
    pl_digits = course[1]
    set_playlist_options(pl_digits)
    course_url = PLURAURL + course_id

    # OS parameters - Setting up paths metadata
    coursepath = os.path.join(INPROGRESSPATH,course_id)

    # Invoking download if not already finished
    if not os.path.exists(os.path.join(FINISHPATH, course_id)):
        # Setting progress structure
        if not os.path.exists(INPROGRESSPATH):
            os.mkdir(INPROGRESSPATH)
        set_directory(coursepath)
        # Setting up logging metadata
        logfile = course_id + ".log"
        logpath = os.path.join(coursepath,logfile)
        PDL_OPTS["logger"] = Logger(logpath)
        
        return invoke_download(course_id, course_url, coursepath)
    else:
        print("Course", course_id, "already downloaded")
        return True


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


def get_usr_pw():
    """Requesting credentials from the user.
    
    Raises:
        ValueError: User enters an empty password too many times
    """
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
            return USERNAME, PASSWORD
        else:
            print('Password cannot be empty, enter password again')
    else:
        raise ValueError('Username or password was not given.')


def set_subtitle():
    """Determines whether subtitle parameters should be turned on or not.
    """
    global SUBTITLE
    subtitle_flags = ("--sub", "--subtitle", "-s",
                      "--SUB", "--SUBTITLE", "-S")
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in subtitle_flags:
                SUBTITLE = True
                print("Subtitles will be appended to videoclips")


def set_directory(path):
    """Setting up directory state for os related tasks.
    
    Arguments:
        path {str} -- Full path to directory
    """
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)


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


def download_courses(courses):
    """Dowloading all courses listed in courselist.txt.
    
    Arguments:
        courses {[(str,[])]} -- List of tuples with course ID and playlist parameters.
    
    """
    global PDL_OPTS
    # General PluraDL settings
    PDL_OPTS["username"] = USERNAME
    PDL_OPTS["password"] = PASSWORD
    PDL_OPTS["sleep_interval"] = SLEEP_INTERVAL
    PDL_OPTS["max_sleep_interval"] = SLEEP_INTERVAL + SLEEP_OFFSET
    PDL_OPTS["ratelimit"] = RATE_LIMIT
    PDL_OPTS["outtmpl"] = FILENAME_TEMPLATE
    PDL_OPTS["verbose"] = True
    PDL_OPTS["restrictfilenames"] = True
    PDL_OPTS["format"] = "bestaudio/best"
    PDL_OPTS["cookiefile"] = COOKIEFILE
    PDL_OPTS["writesubtitles"] = True
    PDL_OPTS["allsubtitles"] = True
    PDL_OPTS["subtitlesformat"] = r'srt'
    PDL_OPTS["verbose"] = True
    if SUBTITLE:
        PDL_OPTS["writesubtitles"] = False
        PDL_OPTS["allsubtitles"] = False

    for course in courses:
        if pluradl(course):
            print("Moving to next course playlist\n")
        else:
            print("\nTerminating requests.\n")
            break


def main():
    """Main execution
    Using command line to store username and password, loops
    through the course IDs and invoking download requests.
    """
    global DLPATH, USERNAME, PASSWORD
    global INPROGRESSPATH, FINISHPATH, FAILPATH, INTERRUPTPATH

    if flag_parser():
        print("Executing by flag input ..\n")
    elif arg_parser():
        print("Executing by user input ..\n")
    else:
        USERNAME, PASSWORD = get_usr_pw()
    
    set_subtitle()

    # Script's absolute directory path
    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Download directory paths
    DLPATH = os.path.join(scriptpath,"courses")
    INPROGRESSPATH = os.path.join(DLPATH,"_inprogress")
    FINISHPATH = os.path.join(DLPATH,"_finished")
    INTERRUPTPATH = os.path.join(DLPATH,"_canceled")
    FAILPATH = os.path.join(DLPATH,"_failed")
    set_directory(DLPATH)

    # Looping through the courses determined by get_courses() invoking download requests
    courses = get_courses(scriptpath)
    if courses:
        download_courses(courses)


if __name__ == "__main__":
    main()