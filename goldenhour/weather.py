import datetime
from random import choice

from darksky import forecast as get_forecast

def get_sunset_forecast(darksky_key, sunset_time, lat_long):
    # Get the forecast from *just before* sunset to avoid night-themed emoji
    just_before_sunset_time = sunset_time - datetime.timedelta(minutes=10)
    with get_forecast(darksky_key, *lat_long, time=just_before_sunset_time.isoformat()) as forecast:
        return forecast


def get_status_text(forecast, sunset_time):
    hourly = forecast['hourly']
    units = forecast['flags']['units']
    currently = forecast['currently']

    return '\n'.join(
        filter(None, [
            '🌅 sunset at {}\n'.format(sunset_time.strftime('%I:%M%p')),
            summary(hourly, currently),
            temp(currently, units),
            cloudiness(currently),
            precip(currently),
            wind(currently),
            visibility(currently),
            nearest_storm(currently),
        ])
    )


def summary(hourly, currently):
    summ = hourly['data'][0]['summary']

    icon = currently['icon']
    cloud_cover = currently['cloudCover']
    temperature = currently['temperature']

    return '{} {}'.format(
        get_emoji(icon, temperature, cloud_cover),
        summ.lower()
    )

def temp(currently, units):
    temperature = currently['temperature']
    apparent_temp = currently['apparentTemperature']

    feels_like = (
        ''
        if round(temperature) == round(apparent_temp)
        else ' (feels like {})'.format(display_temp(apparent_temp, units))
    )

    return '🌡 {}{}'.format(
        display_temp(temperature, units),
        feels_like
    )


def cloudiness(currently):
    cloud_cover = currently['cloudCover']

    if cloud_cover > 0.01:
        return '{} {}% cloud cover'.format(
            get_cloud_cover_emoji(cloud_cover),
            round(cloud_cover * 100)
        )

def precip(currently):
    cloud_cover = currently['cloudCover']

    precip_prob = currently['precipProbability']
    precip_type = currently.get('precipType')

    if precip_type and precip_prob > 0:
        return  '{} {}% chance of {}'.format(
            get_precip_emoji(precip_type, cloud_cover),
            round(precip_prob * 100),
            precip_type
        )

def wind(currently):
    wind_speed = currently['windSpeed']
    wind_bearing = currently['windBearing']

    if wind_speed > 5:
        return '💨 winds about {}mph from the {}'.format(
            round(wind_speed),
            get_bearing(wind_bearing)
        )

def visibility(currently):
    vis = currently.get('visibility', -1)
    if vis < 5 and vis >= 0:
        return '🌁 {} miles of visibility'.format(vis)

def nearest_storm(currently):
    nearest_storm_distance = currently.get('nearestStormDistance', 0)
    nearest_storm_bearing = currently.get('nearestStormBearing')

    if nearest_storm_distance > 0:
        return '⛈ nearest storm {} miles to the {}'.format(
            nearest_storm_distance,
            get_bearing(nearest_storm_bearing)
        )

def display_temp(temperature, units):
    degrees = '℉' if units == 'us' else '℃'

    return str(round(temperature)) + degrees


def get_emoji(icon, temperature, cloud_cover):
    if icon == 'clear-day':
        if temperature > 75:
            return choice(['☀️', '☀️', '😎'])

        if temperature < 32:
            return choice(['☀️', '☀️', '⛄️'])

        return '☀️'

    if icon == 'rain':
        if cloud_cover < 0.5:
            return choice(['🌧', '☔️', '🌦'])

        return choice(['🌧', '☔️'])

    return {
        'clear-night': '🌝',
        'snow': choice(['❄️', '🌨', '☃️']),
        'sleet': '🌨',
        'wind': '🌬',
        'fog': '🌁',
        'cloudy': '☁️',
        'partly-cloudy-day': '🌤',
        'partly-cloudy-night': '⛅️',
    }.get(icon, '')


def get_cloud_cover_emoji(cloud_cover):
    if cloud_cover < 0.2:
        return '☀️'

    if cloud_cover < 0.5:
        return '🌤'

    if cloud_cover < 0.9:
        return '🌥'

    return '☁️'


def get_precip_emoji(precip_type, cloud_cover):
    if precip_type == 'rain':
        if (cloud_cover < 0.5):
            return choice(['🌧', '☔️', '🌦'])

        return choice(['🌧', '☔️'])

    if precip_type == 'snow':
        return choice(['❄️', '🌨', '☃️'])

    if precip_type == 'sleet':
        return '🌨'

    return ''

def get_bearing(degrees, short = False):
    directions = (
        'N,NNE,NE,ENE,E,ESE,SE,SSE,S,SSW,SW,WSW,W,WNW,NW,NNW'
        if short
        else 'north,northeast,east,southeast,south,southwest,west,northwest'
    ).split(',')

    count = len(directions)

    # Distance between each direction
    span = 360.0 / count

    # Use modulo to "round" `16` to `0`
    index = int(round(degrees / span) % count)

    return directions[index]