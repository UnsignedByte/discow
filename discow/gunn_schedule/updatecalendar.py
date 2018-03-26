import urllib.request
import shutil

cal = "https://calendar.google.com/calendar/ical/u5mgb2vlddfj70d7frf3r015h0%40group.calendar.google.com/public/basic.ics"

with urllib.request.urlopen(cal) as response, open('discow/gunn_schedule/calendar.ics', 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
