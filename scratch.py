from plura_dl import PluraDL

YDL_OPTS = {}
YDL_OPTS["username"] = "gorangorangoran"
YDL_OPTS["password"] = "DownloadPlural"

with PluraDL(YDL_OPTS) as pl:
    course_url = r"https://app.pluralsight.com/library/courses/big-data-amazon-web-services"
    pl.download([course_url])