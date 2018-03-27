import urllib.request
import shutil

import datetime
from icalendar import Calendar, Event
from commands.gunn_schedule.scheduleutils import *
from pytz import timezone

cal = "https://calendar.google.com/calendar/ical/u5mgb2vlddfj70d7frf3r015h0%40group.calendar.google.com/public/basic.ics"

with urllib.request.urlopen(cal) as response, open('commands/gunn_schedule/calendar.ics', 'wb') as out_file:
    shutil.copyfileobj(response, out_file)

#Adds REVIEW if string might need reviewing (for weird html, etc)
def review(string):
    weirdchars = ["<",">","&nbsp;"]
    for i in weirdchars:
        if i in string:
            return True
    return False
events = {}

g = open('commands/gunn_schedule/calendar.ics','rb')
gcal = Calendar.from_ical(g.read())
for component in gcal.walk():
    if component.name == "VEVENT":
        year,month,day = component.get("dtstart").dt.strftime('%Y/%m/%d').split("/")
        if year not in events:
            events[year] = {}
        if month not in events[year]:
            events[year][month] = {}
        if day not in events[year][month]:
            events[year][month][day] = []
        if isinstance(component.get("dtstart").dt, datetime.datetime) and component.get("dtend") is not None:
            events[year][month][day].append(
                ScheduleEvent(component.get("dtstart").dt.astimezone(timezone('US/Pacific')),
                component.get("dtend").dt.astimezone(timezone('US/Pacific')),
                component.get("summary"),
                component.get("description")))
        else:
            events[year][month][day].append(
                ScheduleEvent(datetime.datetime.combine(component.get("dtstart").dt, datetime.time()),
                datetime.datetime.combine(component.get("dtstart").dt + datetime.timedelta(days=1), datetime.time()),
                component.get("summary"),
                component.get("description")))
g.close()

with open('commands/gunn_schedule/schedules_temp.txt', 'w') as f:
    out = ""
    for yr in sorted(events.keys()):
        out+="!Y:"+yr+"\n"
        for m in sorted(events[yr].keys()):
            out+="!M:"+m+"\n"
            for d in sorted(events[yr][m].keys()):
                out+="!D:"+d+"\n"
                for ev in events[yr][m][d]:
                    t = parsestr(ev.format())
                    if "See Below" in t or "Alternate Schedule" in t:
                        ev2 = parsestr(ev.getDesc()).strip().split("\n")
                        for el in ev2:
                            el = parsestr(el)
                            out+="!e:"+el
                            if (review(el)):
                                out+=" REVIEW"
                            out+="\n"
                    else:
                        out+="!e:"+t
                        if (review(t)):
                            out+=" REVIEW"
                        out+="\n"
                        desc = parsestr(ev.getDesc()).strip().split("\n")
                        if len(desc) > 0:
                            for ln in desc:
                                ln = parsestr(ln)
                                out+="~d:"+ln
                                if (review(ln)):
                                    out+=" REVIEW"
                                out+="\n"
    f.write(out)

f.close()
