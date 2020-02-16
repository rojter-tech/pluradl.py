from __future__ import unicode_literals
import sys, os, shutil, re, getpass, io, youtube_dl
from youtube_dl.extractor.common import ExtractorError
from youtube_dl.utils import DownloadError

if sys.version_info[0] <3:
    raise Exception("Must be using Python 3")

# IMPORTANT SETTINGS TO PREVENT SPAM BLOCKING OF YOUR ACCOUNT/IP AT PLURALSIGHT # # # #
SLEEP_INTERVAL = 150    # minimum sleep time        #                                 #
SLEEP_OFFSET   = 50     # adding random sleep time  #  Change this at your own risk.  #
RATE_LIMIT     = 10**6  # download rate in bytes/s  #                                 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Global defaults
DLPATH, USERNAME, PASSWORD = "", "", ""
YDL_OPTS = {}
SUBTITLE = False
FILENAME_TEMPLATE = r"%(playlist_index)s-%(chapter_number)s-%(title)s-%(resolution)s.%(ext)s"
PLURAURL = "https://app.pluralsight.com/library/courses/"


class Logger(object):
    def __init__(self,logpath):
        self.logpath = logpath
        with open(self.logpath, 'wt') as f: pass

    def debug(self, msg):
        print(msg)
        with open(self.logpath, 'at') as f: f.write(msg+'\n')

    def warning(self, msg):
        print(msg)
        with open(self.logpath, 'at') as f: f.write(msg+'\n')

    def error(self, msg):
        print(msg)
        with open(self.logpath, 'at') as f: f.write(msg+'\n')


def _set_subtitle():
    global SUBTITLE
    subtitle_flags = ("--sub", "--subtitle", "-s",
                      "--SUB", "--SUBTITLE", "-S")
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in subtitle_flags:
                SUBTITLE = True
                print("Subtitles will be appended to videoclips")


def _get_usr_pw():
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


def _set_playlist_options(digits):
    global YDL_OPTS

    n = len(digits)
    if n == 0:
        pass
    elif n == 1:
        print("Downloading video indicies up to",digits[0],"to")
        YDL_OPTS["playlistend"]   = digits[0]
    elif n == 2:
        print("Downloading video indicies from",digits[0],"up to and including",digits[1])
        YDL_OPTS["playliststart"] = digits[0]
        YDL_OPTS["playlistend"]   = digits[1]
    else:
        print("Downloading specific video indicies", digits)
        YDL_OPTS["playlist_items"] = ','.join([str(x) for x in digits])


def _invoke_download(course_id, course_url, coursepath, finishpath, failpath, interruptpath):

    with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
        try:
            # Invoke download
            ydl.download([course_url])

            # Moving content to final destination if the download was sucessful
            finalpath = os.path.join(finishpath,course_id)
            ydl.to_stdout("The course " + course_id + " was downloaded successfully.")
            ydl.to_stdout("Moving content to " + finalpath)
            if not os.path.exists(finishpath):
                os.mkdir(finishpath)
            try:
                shutil.move(coursepath,finalpath)
            except PermissionError:
                ydl.to_stdout("Directory still in use, leaving it. Will be fixed in future releases.")
            return True
        
        except (ExtractorError, DownloadError):
            # Handling the case of invalid download requests
            finalpath = os.path.join(failpath,course_id)
            ydl.to_stdout("Something went wrong.")
            ydl.to_stdout("The course " + course_id + " may not be a part of your current licence.")
            ydl.to_stdout("Visit " + course_url + " for more information.\n")
            if not os.path.exists(failpath):
                os.mkdir(failpath)
            try:
                shutil.move(coursepath,finalpath)
            except PermissionError:
                ydl.to_stdout("Directory still in use, leaving it. Will be fixed in future releases.")
            return True
        
        except KeyboardInterrupt:
            finalpath = os.path.join(interruptpath,course_id)
            ydl.to_stdout("\n\nThe download stream for " + course_id + " was canceled by user.")
            ydl.to_stdout("Moving content to " + finalpath)
            if not os.path.exists(interruptpath):
                os.mkdir(interruptpath)
            try:
                shutil.move(coursepath,finalpath)
            except PermissionError:
                ydl.to_stdout("Directory still in use, leaving it. Will be fixed in future releases.")
            return False


def _pluradl(course):
    """Handling the video downloading requests for a single course
    
    Arguments:
        course {str} -- Course identifier
    
    Returns:
        str -- youtue-dl CLI command
    """
    global YDL_OPTS

    # Course metadata
    course_id = course[0]
    pl_digits = course[1]
    _set_playlist_options(pl_digits)
    course_url = PLURAURL + course_id

    # OS parameters - Setting up paths metadata
    coursepath = os.path.join(DLPATH,course_id)
    failpath = os.path.join(DLPATH,"_failed")
    finishpath = os.path.join(DLPATH,"_finished")
    interruptpath = os.path.join(DLPATH,"_canceled")
    if not os.path.exists(coursepath):
        os.mkdir(coursepath)
    os.chdir(coursepath)

    # Setting up logging metadata
    logile = course_id + ".log"
    logpath = os.path.join(coursepath,logile)
    YDL_OPTS["logger"] = Logger(logpath)

    # Setting up subtitles
    if SUBTITLE:
        YDL_OPTS["writesubtitles"] = True

    # Invoking download request
    return _invoke_download(course_id,
                            course_url,
                            coursepath,
                            finishpath,
                            failpath,
                            interruptpath)


def _download_courses(courses):
    """Dowloading all courses listed in courselist.txt
    
    Arguments:
        courses {[type]} -- List of course ID
    
    """
    global YDL_OPTS
    YDL_OPTS["username"] = USERNAME
    YDL_OPTS["password"] = PASSWORD
    YDL_OPTS["sleep_interval"] = SLEEP_INTERVAL
    YDL_OPTS["max_sleep_interval"] = SLEEP_INTERVAL + SLEEP_OFFSET
    YDL_OPTS["ratelimit"] = RATE_LIMIT
    YDL_OPTS["outtmpl"] = FILENAME_TEMPLATE
    YDL_OPTS["verbose"] = True
    YDL_OPTS["restrictfilenames"] = True
    YDL_OPTS["format"] = "bestaudio/best"

    for course in courses:
        if _pluradl(course):
            print("Moving to next course playlist\n")
        else:
            print("\nTerminating requests.\n")
            break


def _get_courses(scriptpath):
    """Parsing courselist.txt
    
    Arguments:
        scriptpath {str} -- Absolute path to script directory
    
    Returns:
        [str] -- List of course identifiers exposed by courselist.txt
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


def _flag_parser():
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
    for key, val in flag_states.items():
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


def _arg_parser():
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

    if _flag_parser():
        print("Executing by flag input ..\n")
    elif _arg_parser():
        print("Executing by short input ..\n")
    else:
        _get_usr_pw()
    
    _set_subtitle()

    # Script's absolute directory path
    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Download directory path
    dldirname = "Courses"
    DLPATH = os.path.join(scriptpath,dldirname)
    if not os.path.exists(DLPATH):
        os.mkdir(DLPATH)

    # Looping through the courses determined by _get_courses() invoking download requests
    courses = _get_courses(scriptpath)
    if courses:
        _download_courses(courses)


if __name__ == "__main__":
    main()
