from discow.handlers import *
import asyncio
import discow.utils
import dateparser as cf
import datetime
import re
import calendar
import time
from discord import Embed
from commands.gunn_schedule.scheduleutils import *

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
raw_schedules = open("commands/gunn_schedule/schedules.txt").read().split('\n')

defaults = {}
raw_defaults = open("commands/gunn_schedule/defaults.txt").read().split('\n')

curr_day = None
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

            curr_schedule.append(ScheduleEvent(times[0], times[1],
                                               name, None))
defaults[curr_day_text] = curr_schedule.copy()

print("Parsing schedules")

i = 1
for sched in raw_schedules:
    i += 1
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
    em = Embed(title="Schedule for %s (%s)" % (date.isoformat(), calendar.day_name[date.weekday()]), colour=0x12AA24)
    em.set_footer(text="Taken from the Gunn Website.")
    try:
        sched = getSchedule(date)
    except:
        em.description = "unknown"
        return em
    if not sched:
        em.description = "No school"
        return em
    n = ""
    t = ""
    for event in sched:
        n+="**"+event.name.title()+"**\n"
        t+=event.getT()+"\n"
        #em.add_field(name=event.name.title(), value=event.getT(), inline=False)
    em.add_field(name="Periods", value=n)
    em.add_field(name="Times", value=t)
    return em

old_schedule_messages = []
old_week_schedule_messages = []

class ScheduleMessage:
    def __init__(self, msg, stamp, timef):
        self.id = msg.id
        self.stamp = stamp
        self.time = timef
        self.beingmodified = False

    def __eq__(self, other):
        return self.msg == other.msg

leftarrow = "\U000025C0"
rightarrow = "\U000025B6"
rewind = "\U000023EA"
fastforward = "\U000023E9"

@asyncio.coroutine
def schedule(Discow, msg):

    timef = discow.utils.strip_command(msg.content)
    if timef == '':
        timef = "today"
    parsed = specialParseDate(timef)

    if not parsed:
        yield from Discow.send_message(msg.channel, "Unknown date.")
        return

    parsed = parsed.date()

    msg = yield from Discow.send_message(msg.channel, embed=formatSchedule(parsed))

    yield from Discow.add_reaction(msg, rewind)
    yield from Discow.add_reaction(msg, leftarrow)
    yield from Discow.add_reaction(msg, rightarrow)
    yield from Discow.add_reaction(msg, fastforward)

    old_schedule_messages.append(ScheduleMessage(msg, time.gmtime(), parsed))


@asyncio.coroutine
def schedule_react(Discow, reaction, user):
    if user == Discow.user or reaction.message.author != Discow.user:
        return

    for c in old_schedule_messages:
        if c.id == reaction.message.id:
            c.time += datetime.timedelta(days=(-1 if (reaction.emoji == leftarrow) else (1 if reaction.emoji == rightarrow else -7 if reaction.emoji == rewind else 7)))
            yield from Discow.edit_message(reaction.message, embed=Embed(title="Schedule for %s (%s)" % (c.time.isoformat(), calendar.day_name[c.time.weekday()]), colour=0x12AA24, description="Calculating schedule..."))
            yield from Discow.edit_message(reaction.message, embed=formatSchedule(c.time))
            return

@asyncio.coroutine
def week_schedule_react(Discow, reaction, user):
    if user == Discow.user or reaction.message.author != Discow.user:
        return

    for c in old_week_schedule_messages:
        if c.id == reaction.message.id:
            c.time += datetime.timedelta(days=(-7 if (reaction.emoji == leftarrow) else 7))
            yield from Discow.edit_message(reaction.message, "Calculating schedule...")

            parsed = c.time
            daf = (parsed.weekday() + 1) % 7

            yield from Discow.edit_message(reaction.message, '\n'.join(
                formatSchedule(parsed + datetime.timedelta(days=x)) for x in range(-daf, 7 - daf)))
            return

@asyncio.coroutine
def week_schedule(Discow, msg):

    timef = discow.utils.strip_command(msg.content)
    if timef == '':
        timef = "today"

    parsed = specialParseDate(timef)
    if not parsed:
        yield from Discow.send_message(msg.channel, "Unknown date.")
        return

    parsed = parsed.date()
    daf = (parsed.weekday() + 1) % 7

    frp = yield from Discow.send_message(msg.channel, '\n'.join(formatSchedule(parsed + datetime.timedelta(days=x)) for x in range(-daf, 7-daf)))

    yield from Discow.add_reaction(frp, leftarrow)
    yield from Discow.add_reaction(frp, rightarrow)

    old_week_schedule_messages.append(ScheduleMessage(frp, time.gmtime(), parsed))

add_message_handler(schedule, "schedule")
add_message_handler(week_schedule, "weekschedule")
add_message_handler(week_schedule, "week-schedule")
add_message_handler(week_schedule, "week_schedule")

add_reaction_handler(schedule_react, "sch_react")
add_unreaction_handler(schedule_react, "sch_react")
add_reaction_handler(week_schedule_react, "wsch_react")
add_unreaction_handler(week_schedule_react, "wsch_react")
