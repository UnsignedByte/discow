from discow.handlers import message_handlers
import asyncio
import discow.utils
import dateparser as cf
import datetime
import re

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

schedules = {}
raw_schedules = open("discow/gunn_schedule/schedules.txt").read().split('\n')

defaults = {}
raw_defaults = open("discow/gunn_schedule/defaults.txt").read().split('\n')

curr_day = None
curr_day_text = None
curr_schedule = []

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

            curr_schedule.append(ScheduleEvent(times[0], times[1],
                                               name, None))
defaults[curr_day_text] = curr_schedule.copy()

print("Parsing schedules")

for sched in raw_schedules:
    if sched.startswith("$$"):
        schedules[curr_day] = curr_schedule.copy()
        curr_day_text = sched[2:]
        curr_day = parseDate(curr_day_text).date()
        curr_schedule = []
    else:
        if sched == "None":
            continue
        elif sched == "Default":
            relev  = defaults[str(curr_day.weekday())]

            for relevant_default in relev:
                curr_schedule.append(ScheduleEvent(parseSchoolDate(curr_day_text + " " + relevant_default.start),
                                                                parseSchoolDate(curr_day_text + " " + relevant_default.end),
                                               relevant_default.name, relevant_default.desc))
        elif sched.startswith('!e'):
            name = getName.findall(sched)[0]
            times = getTime.findall(sched)[0].split('-')

            curr_schedule.append(ScheduleEvent(parseSchoolDate(curr_day_text + " " + times[0]),
                                               parseSchoolDate(curr_day_text + " " + times[1]),
                                               name, None))

schedules[curr_day] = curr_schedule

print("Finished parsing")

def getSchedule(date):
    return schedules[date]

def formatSchedule(date):
    try:
        sched = getSchedule(date)
    except:
        return "Schedule for %s unknown." % date.isoformat()
    if not sched:
        return """No school on %s.""" % date.isoformat()
    table = """Schedule for %s:\n\n""" % date.isoformat()
    for event in sched:
        table += (event.format()) + '\n'
    return table

@asyncio.coroutine
def schedule(Discow, msg):

    time = discow.utils.strip_command(msg.content)
    parsed = specialParseDate(time)

    if not parsed:
        yield from Discow.send_message(msg.channel, "Unknown date.")
        return

    parsed = parsed.date()

    yield from Discow.send_message(msg.channel, formatSchedule(parsed))


message_handlers["schedule"] = schedule