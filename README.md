# Automated download from Pluralsight with `pluradl.py`

You can download whole courses from a number of tutorial sites with the CLI tool `youtube-dl`, however, in this Git I have provided an Python script, `pluradl.py`,  for automated download of a **whole sequence of Pluralsight courses** (of your choice) at once using the `youtube_dl` API. Below I give an example of how to use the `pluradl.py` script with a Pluralsight account to get videos from an arbitrary large list of courses at their site.

**You can get a free 1 month trial to Pluralsight by signing up for free to [Visual Studio Dev Essentials](https://www.visualstudio.com/dev-essentials/)**

### Requirements
* [Python 3](https://www.python.org/)
* [youtube_dl](https://ytdl-org.github.io/youtube-dl/) (install via pip)

## Usage

### Download from **Pluralsight** with `pluradl.py`
After installation of youtube_dl (thus is avaiable in the Python 3 environment) make sure that [`courselist.txt`](https://github.com/rojter-tech/pluradl.py/blob/master/courselist.txt) is in the same directory as [`pluradl.py`](https://github.com/rojter-tech/pluradl.py/blob/master/pluradl.py) with the course ID's of your choice **listed row by row**. Example files and scripts is provided in [Scripts](https://github.com/rojter-tech/pluradl.py/tree/master/Scripts). The course ID can be found via the course URL from the Pluralsight website, e.g [https://app.pluralsight.com/library/courses/c-sharp-fundamentals-with-visual-studio-2015/table-of-contents](https://app.pluralsight.com/library/courses/c-sharp-fundamentals-with-visual-studio-2015/table-of-contents) where the ID is "c-sharp-fundamentals-with-visual-studio-2015".

Run the script in your terminal to download all the videos from all the courses in [`courselist.txt`](https://github.com/rojter-tech/pluradl.py/blob/master/courselist.txt). The videos will be automatically placed in course specific directories and named by playlist order number. Substitute the example credentials with your own and supply courselist.txt with your desired courses ...

```bash
$ python pluradl.py
Enter you Pluralsight credentials
Enter username: youremail@example.com
Enter password (will not be displayed)
: yourPassword
```

... with `courselist.txt` available at the same path

`courselist.txt`
```notepad
c-sharp-fundamentals-with-visual-studio-2015
csharp-nulls-working
csharp-best-practices-collections-generics
object-oriented-programming-fundamentals-csharp
using-csharp-interfaces
linq-fundamentals-csharp-6
.
.
```

For even more automation, the script can be executed directly by passing Pluralsight username and password

```bash
python pluradl.py "myusername@mymail.com" "myPassword"
```

#### Set subtitle
To supplement with english subtitles use the "-s", "--sub" or "--subtitle" flag
```bash
$ python pluradl.py --subtitle
^C
$ python pluradl.py "myusername@mymail.com" "myPassword" --subtitle
^C
$ python pluradl.py --user "myusername@mymail.com" --pass "myPassword" --subtitle
^C
```

#### Set video interval
If you only want a specific interval/range of videoclips from a specific course you can specify {the end number} or {the start and the end number} on the same row as the course id (they comes in the same order as they do on the website playlist with start number of 1)

eg. in `courselist.txt`
```notepad
c-sharp-fundamentals-with-visual-studio-2015 25
csharp-best-practices-collections-generics 11 56
.
.
```

wich would give you the **25 first videoclips** in the course c-sharp-fundamentals-with-visual-studio-2015 and the clips **numbered 11 up to 56** in csharp-best-practices-collections-generics.

If you specify **three of more numbers** it will download those specific video indicies

`courselist.txt`
```notepad
c-sharp-fundamentals-with-visual-studio-2015 2 10 15
csharp-best-practices-collections-generics 5 3 10 11
.
.
```

wich would give you three videos, those that are numbered **2**, **10** and **15**, in the course c-sharp-fundamentals-with-visual-studio-2015 and the four specific videos with indicies **5**, **3**, **10** and **11** in csharp-best-practices-collections-generics.

### Example output

![Directory tree of pluradl.py root](https://raw.githubusercontent.com/rojter-tech/pluradl.py/master/Image/example_output_tree.png)

# IMPORTANT
The argument `SLEEP_INTERVAL = 150` parameter used in the [`pluradl.py`](https://github.com/rojter-tech/pluradl.py/blob/master/pluradl.py) script is important. It means that the program will wait at least 150s (2.5 minutes) before it downloads the next video. If you don't use this flag _Pluralsight_ will ban you because you are doing too many requests under a short period of time.

>We have blocked your account because our security systems have flagged your Pluralsight account for an unusual amount activity. This does mean a high volume of requests that are in the realm of a request every 10-30 seconds for a prolonged period of time. Please note that this high volume of activity is in violation of our terms of service [https://www.pluralsight.com/terms].
