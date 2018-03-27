#!/usr/bin/env python

import argparse
import datetime
import os
import random
from dotenv import load_dotenv
from pathlib import Path 

from goldenhour import sunset, timelapse, twitter, weather

def calc_duration(duration, minutes_before_start, minutes_after_end):
    if duration:
        return duration

    startTime = sunset.get_start_time(minutes_before_start)

    now = sunset.get_now()
    if now > startTime:
        startTime = now

    event_duration = (sunset.get_end_time(minutes_after_end) - startTime).total_seconds()

    return event_duration

def calculate_timelapse_duration(duration, interval, photo_display_rate=30.0):
    # return number of seconds
    return float(duration) / interval / photo_display_rate

def get_random_status_text():
    return random.choice([
        'wow.',
        'holy moly',
        'what a time to be alive',
        'inconceivable',
        'reverse sunrise',
    ])


def get_timelapse_filename(output_dir):
    filename_template = '{output_dir}/timelapse_{date}_{count:03d}.mp4'
    today_str = datetime.date.today().isoformat()
    count = 0
    while True:
        filename = filename_template.format(
            output_dir=output_dir,
            date=today_str,
            count=count,
        )
        if not os.path.exists(filename):
            return filename
        count += 1


def main():
    
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path) 
    parser = argparse.ArgumentParser()

    parser.add_argument('-d','--duration',
        metavar='seconds',
        type=int,
        default=os.getenv('DURATION'), # 2 hours 7200
        help='duration of timelapse capture',
    )
    # TODO might want to enforce minimum of 3 if using raspi cam
    parser.add_argument('-i','--interval',
        metavar='seconds',
        type=int,
        default=8,
        help='time between captured photos',
    )
    parser.add_argument('--minutes-before-start',
        metavar='minutes',
        type=int,
        default=None,
        help='number of minutes before start event to start timelapse',
    )

    parser.add_argument('--minutes-after-end',
        metavar='minutes',
        type=int,
        default=None,
        help='number of minutes after end event to end timelapse',
    )

    parser.add_argument('--post-to-twitter',
        action='store_true',
        default=False,
        help='post video to twitter',
    )
    parser.add_argument('--darksky-key',
        help='API key for the Dark Sky API'
    )
    parser.add_argument('--skip-timelapse',
        action='store_true',
        default=False,
        help='skip recording the timelapse (useful for debugging)',
    )
    args = parser.parse_args()

    output_dir = os.getenv("OUTPUT_DIR")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    timelapse_filename = get_timelapse_filename(output_dir)
    duration = args.duration or os.getenv('DURATION')
    duration = calc_duration(duration, args.minutes_before_start, args.minutes_after_end)
    
    video_duration = calculate_timelapse_duration(duration, args.interval)

    print('DURATION: {} video duration: {}'.format(duration/60, video_duration/60) )
    if args.post_to_twitter:
        print('verifying twitter credentials')
        twitter.verify_credentials()
        # check the expected length of the video to make sure it's within twitter's rules
        
        print('estimated video length: {} seconds'.format(video_duration))
        if video_duration < 5.0:
            print('Error: Timelapse video will be too short to upload to Twitter (min 5 seconds)')
            exit(1)
        if video_duration > 140.0:
            print('Error: Timelapse video will be too long to upload to Twitter (max 140 seconds)')
            exit(2)

    if args.minutes_before_start is not None:
        sunset.wait_for_start(args.minutes_before_start, args.minutes_after_end)

    if not args.skip_timelapse:
        timelapse.create_timelapse(duration, args.interval, timelapse_filename)

    darksky_key = args.darksky_key or os.getenv("DARKSKY_KEY")
    
    if darksky_key:
        
        geoCoordinates = float(os.getenv("LATITUDE")), float(os.getenv("LONGITUDE"))
        sunset_time = sunset.get_sunset_time()

        forecast = weather.get_sunset_forecast(darksky_key, sunset_time, geoCoordinates)
        status_text = weather.get_status_text(forecast, sunset_time)
    else:
        status_text = get_random_status_text()

    print(status_text)

    if args.post_to_twitter and not args.skip_timelapse:
        twitter.post_update(status_text, media=timelapse_filename)

    print('done!')


if __name__ == '__main__':
    main()
