from discow.handlers import message_handlers
import asyncio
import discow.utils
import re

import datetime
import dateparser as cf
from icalendar import Calendar, Event


dateparser = cf.DateDataParser(["en"])
def parseDate(string):
    return dateparser.get_date_data(string)["date_obj"]

def parseSchoolDate(string):
    literal_date = parseDate(string)
    if literal_date.hour <= 6:
        literal_date += datetime.timedelta(hours=12)
    return literal_date

def specialParseDate(string):
    prf = parseDate(string)
    if prf:
        return prf
    string = string.replace(' ', '')
    if string.startswith("this") or string.startswith("next"):
        return parseDate(string[4:]) + datetime.timedelta(7)

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
        return "%s: **%s** - **%s** " % (self.name,
                                             self.start.time().strftime("%I:%M"),
                                             self.end.time().strftime("%I:%M")) + "(%s)" % (td_format(self.end-self.start))

defaults = {}
raw_defaults = open("discow/gunn_schedule/defaults.txt").read().split('\n')
curr_day_text = None
curr_schedule = []

getName = re.compile('\[(.+)\]')
getTime = re.compile('\((.+)\)')

for sched in raw_defaults:
    if sched.startswith("$$"):
        defaults[curr_day_text] = curr_schedule.copy()
        curr_day_text = sched[2:]
        curr_schedule = []
    else:
        if sched == "None":
            continue
        elif sched.startswith('!e'):
            name = getName.findall(sched)[0]
            times = getTime.findall(sched)[0].split('-')
            curr_schedule.append(ScheduleEvent(parseSchoolDate(times[0]), parseSchoolDate(times[1]),
                                               name, None))
defaults[curr_day_text] = curr_schedule.copy()

def tomarkdown(string):
    string = string.replace("<p>", "")
    string = string.replace("</p>", "\n")
    string = string.replace("<span>", "")
    string = string.replace("</span>", "")
    string = string.replace("<i>", "*")
    string = string.replace("</i>", "*")
    string = string.replace("<u>", "__")
    string = string.replace("</u>", "__")
    string = string.replace("&nbsp;", "")
    string = string.replace("<br>", "\n")
    return string

@asyncio.coroutine
def calendar(Discow, msg):
    try:
        time = discow.utils.parse_command(msg.content, 1)
    except IndexError:
        time = "today"
    parsed = specialParseDate(time)

    if not parsed:
        yield from Discow.send_message(msg.channel, "Unknown date.")
        return

    parsed = parsed.date()

    out = "__**Events on "+str(parsed)+"**__"
    hasevent = False

    g = open('discow/gunn_schedule/calendar.ics','rb')
    gcal = Calendar.from_ical(g.read())
    for component in gcal.walk():
        if component.name == "VEVENT":
            if component.get("dtstart").dt == parsed:
                out+="\n\n**"+component.get("summary")+"**"
                if 'Schedule (see below)' in component.get("summary"):
                    hasevent = True
                elif component.get("description").strip():
                    out+="\n\n"+tomarkdown(component.get("description"))
    g.close()
    if not hasevent:
        relev  = defaults[str(parsed.weekday())]
        if parsed.weekday() not in [5, 6]:
            out+="\n\n**Default Schedule**\n"
            for event in relev:
                out+="\n"+event.format()
        else:
            out+="\nNo school on "+str(parsed)+"."

    yield from Discow.send_message(msg.channel, out.strip())

message_handlers["cal"] = calendar
