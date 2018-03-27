import datetime

# credit to https://stackoverflow.com/a/13756038
def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)

class ScheduleEvent:
    def __init__(self, starttime, endtime, name, desc):
        self.start = starttime
        self.end = endtime
        self.name = name
        self.desc = desc
    def format(self, tfhour = False, showlengths = True):
        return "%s: **%s** - **%s** " % (self.name.title(),
                                             self.start.time().strftime("%I:%M %p"),
                                             self.end.time().strftime("%I:%M %p")) + "(%s)" % (td_format(self.end-self.start))
    def getDesc(self):
        return self.desc

def parsestr(s):
    s = s.strip()
    replstrs = {
        "\"": ["”","“"],
        "'": ["’","‘"],
        " ": ["&nbsp;", " "],
        "-": ["–", "—"],
        "\t":["\t\t\t","\t\t","  "],
        "\t•": ["•", "·"],
        "\n": ["<br>"]
    }
    for k, v in replstrs.items():
        for a in v:
            s = s.replace(a, k)
    return s.strip()
