import datetime
import time
import os

from astral import Astral, Location
import pytz

def getAstralObject():
    city = os.getenv('ASTRAL_CITY')
    astral = Astral()
    if city in astral.geocoder.locations:
        return astral[city]
    
    l = Location((city, os.getenv('ASTRAL_REGION'),
               float(os.getenv('LATITUDE')),  float(os.getenv('LONGITUDE')), os.getenv('ASTRAL_TIMEZONE'), 0))

    return l

def get_timezone(astral):
    return pytz.timezone(astral.timezone)

def get_today(astral):
    local_timezone = get_timezone(astral)
    now = datetime.datetime.now(local_timezone)
    return now.date()

def get_time_for_event(event, today=None):
    
    astral = getAstralObject()

    if today is None:
        today = get_today(astral)
    
    return astral.sun(today)[event]

def get_sunset_time():
    return get_time_for_event('sunset')    

def get_start_time(minutes_before):

    event_start = get_time_for_event(os.getenv('ASTRAL_START_EVENT'))

    minutes_before = minutes_before or int(os.getenv('MINUTES_BEFORE_START')) or 0

    start =  event_start - datetime.timedelta(minutes=minutes_before)
    print('Starting at {}'.format(start))
    return start 

def get_end_time(minutes_after):
    end_event_time = get_time_for_event(os.getenv('ASTRAL_END_EVENT'))
    
    minutes_after = minutes_after or int(os.getenv('MINUTES_AFTER_END')) or 0
    ending = end_event_time + datetime.timedelta(minutes=minutes_after)
    print('ending at {}'.format(ending))
    return ending

def get_seconds_until(earlier_time, later_time):
    tdelta = later_time - earlier_time
    return tdelta.total_seconds()

def wait_for_start(minutes_before=0, minutes_after=0):
    city = os.getenv('ASTRAL_CITY')
    astral = getAstralObject()
    local_timezone = get_timezone(astral)
    
    start_time = get_start_time(minutes_before)
    end_time = get_end_time(minutes_after)
    now = datetime.datetime.now(local_timezone)

    if  now > end_time:
        print('ERROR: too late to start for today\'s sunset')
        exit()
    
    if start_time > now:
        print('not sleeping')
        return

    sleep_seconds = get_seconds_until(now, start_time)
    if sleep_seconds < 0:
        return
	
    # TODO print wait time in hours and seconds
    print('waiting {} seconds to start {} minutes before start event'.format(sleep_seconds, minutes_before))
    time.sleep(sleep_seconds)
