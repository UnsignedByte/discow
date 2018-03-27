from scheduleutils import *
import dateparser
import re

raw_calendar = open("commands/gunn_schedule/schedules_temp.txt").read().split('\n')

current_year = -1
current_month = -1
current_day = -1

current_dt = None

current_day_schedule = []
cr_event_class = ScheduleEvent(None, None, None,"")
schedules = {}

time_regex = re.compile("\*\*([^*]*)\*\*")

def get_times(string):
    res = time_regex.findall(string)
    return res[0], res[1]


for i,line in enumerate(raw_calendar):
    if line.startswith("!Y:"):
        if cr_event_class.name:
            current_day_schedule.append(cr_event_class.copy())
            cr_event_class = ScheduleEvent(None, None, None, "")
        current_year = int(line[3:])
        continue
    elif line.startswith("!M:"):
        if cr_event_class.name:
            current_day_schedule.append(cr_event_class.copy())
            cr_event_class = ScheduleEvent(None, None, None, "")
        current_month = int(line[3:])
        continue
    elif line.startswith("!D:"):
        if cr_event_class.name:
            current_day_schedule.append(cr_event_class.copy())
            cr_event_class = ScheduleEvent(None, None, None, "")
        if current_dt:
            schedules[current_dt] = current_day_schedule.copy()
        current_day = int(line[3:])
        current_day_schedule = []
        continue

    current_dt = datetime.date(current_year, current_month, current_day)
    dt_formed = "%s/%s/%s " % (current_month, current_day, current_year)

    if line.startswith("!e:"):
        if cr_event_class.name:
            current_day_schedule.append(cr_event_class.copy())
            cr_event_class = ScheduleEvent(None, None, None, "")
        cr_event_class.name = line[3:].split(':')[0].strip()
        times = get_times(line)
        cr_event_class.start = parseDate(dt_formed + times[0])
        cr_event_class.end = parseDate(dt_formed + times[1])
    if line.startswith("~d:"):
        defc = line[3:]
        if defc:
            cr_event_class.desc += defc + '\n'

print(schedules[datetime.date(2018, 3, 26)])
