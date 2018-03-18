import datetime
import time

from astral import Astral
import pytz


ASTRAL_CITY_NAME_SEATTLE = 'minneapolis'

def get_timezone(city):
    return pytz.timezone(Astral()[city].timezone)

def get_today_sunset_time(city, today=None):
    if today is None:
        local_timezone = get_timezone(city)
        now = datetime.datetime.now(local_timezone)
        today = now.date()

    return Astral()[city].sun(today)['sunset']


def get_seconds_until(earlier_time, later_time):
    tdelta = later_time - earlier_time
    return tdelta.total_seconds()


def wait_for_sunset(minutes_before=0):
    city = ASTRAL_CITY_NAME_SEATTLE
    local_timezone = get_timezone(city)
    now = datetime.datetime.now(local_timezone)
    sunset_time = get_today_sunset_time(city, now.date())
    start_time = sunset_time - datetime.timedelta(minutes=minutes_before)
    if start_time < now:
        print('ERROR: too late to start for today\'s sunset')
        exit()

    sleep_seconds = get_seconds_until(now, start_time)
    # TODO print wait time in hours and seconds
    print('waiting {} seconds to start {} minutes before sunset'.format(sleep_seconds, minutes_before))
    time.sleep(sleep_seconds)
