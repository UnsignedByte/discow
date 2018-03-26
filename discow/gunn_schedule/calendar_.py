from discow.handlers import message_handlers
import asyncio
import discow.utils

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

@asyncio.coroutine
def calendar(Discow, msg):
    time = discow.utils.strip_command(msg.content)
    parsed = specialParseDate(time)

    if not parsed:
        yield from Discow.send_message(msg.channel, "Unknown date.")
        return

    parsed = parsed.date()

    out = "**Schedule for "+str(parsed)+"**"

    g = open('discow/gunn_schedule/calendar.ics','rb')
    gcal = Calendar.from_ical(g.read())
    for component in gcal.walk():
        if component.name == "VEVENT":
            if component.get("dtstart").dt == parsed:
                print(component.get("summary"))
                out+="\n"+component.get("summary")
    g.close()
    yield from Discow.send_message(msg.channel, out)

message_handlers["calendar"] = calendar
