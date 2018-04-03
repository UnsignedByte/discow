whitespace = [' ', '\t', '\n']
discow_prefix = "cow "
from discord import ServerRegion
import datetime
from pytz import timezone
import pytz

def format_response(string, **kwargs):
    if "_msg" in kwargs:
        message = kwargs["_msg"]
        kwargs["_msgcontent"] = message.content
        kwargs["_author"] = message.author
    if "_author" in kwargs:
        author = kwargs["_author"]
        kwargs["_name"] = author.display_name
        kwargs["_username"] = author.name
        kwargs["_mention"] = author.mention

    return string.format(**kwargs)

def parse_command(msg, num=-1):
    cont = msg[len(discow_prefix):].split(" ")
    if num is not -1:
        if len(cont)<num+1:
            raise IndexError("Not enough inputs")
        else:
            return cont[:num]+[' '.join(cont[num:])]
    else:
        return cont

def strip_command(msg):
    return parse_command(msg, 1)[1]

def get_localized_time(serv):
    return convertTime(datetime.datetime.utcnow())

def convertTime(time, serv):
    timezones = {
    ServerRegion.us_west:"America/Los_Angeles",
    ServerRegion.us_east:"America/New_York",
    ServerRegion.us_central:"US/Central",
    ServerRegion.eu_west:"Europe/Amsterdam",
    ServerRegion.eu_central:"Europe/Berlin",
    ServerRegion.singapore:"Singapore",
    ServerRegion.london:"Europe/London",
    ServerRegion.sydney:"Australia/Sydney",
    ServerRegion.amsterdam:"Europe/Amsterdam",
    ServerRegion.frankfurt:"Europe/Berlin",
    ServerRegion.brazil:"Brazil/Acre",
    ServerRegion.vip_us_east:"America/New_York",
    ServerRegion.vip_us_west:"America/Los_Angeles",
    ServerRegion.vip_amsterdam:"Europe/Amsterdam"
    }
    zone = timezone(timezones[serv.region])
    time_naive = time.replace(tzinfo=pytz.utc)
    loctime = time_naive.astimezone(zone)
    fmt = '%Y-%m-%d at %H:%M:%S %Z%z'
    return loctime.strftime(fmt)
