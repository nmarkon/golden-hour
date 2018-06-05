import argparse
import os
import subprocess

from .ffmpeg import compile_video


def capture(output_dir, duration, interval):
    print('capturing one photo every {interval} seconds for {duration} seconds'.format(
        duration=duration,
        interval=interval,
    ))
    output_pattern = '{}/image%05d.png'.format(output_dir)
    # TODO check exit status
    subprocess.call([
        'raspistill',
        '-t', str(duration * 1000),
        '-tl', str(interval * 1000),
        '-n', # don't try to show a preview window
        '-w', '1920',
        '-h', '1080',
        #'--rotation', '180', # set this to correct for camera orientation
        '--quality', '100',
        # '--verbose',
        # '--saturation', '50',
        '-o', output_pattern,
        '-e', 'png',
    ])


def main():
    parser = argparse.ArgumentParser(description='Record a timelapse.')
    parser.add_argument('--duration', metavar='seconds', required=True, type=int, help='total duration of timelapse capture in seconds')
    parser.add_argument('--interval', metavar='seconds', required=True, type=int, help='number of seconds between photo captures')
    parser.add_argument('--photos-per-second', type=int, default=30, help='number of photos displayed per second in video')
    args = parser.parse_args()
    print(args)

    # capture and compile timelapse
    if not os.path.exists('photos'):
        os.makedirs('photos')
    photos_dir = os.path.abspath('photos')
    output_filename = 'timelapse.mp4'
    print('created {}'.format(photos_dir))
    capture(photos_dir, args.duration, args.interval)
    compile_video(photos_dir, output_filename, args.photos_per_second)
    # TODO clean up temp dir


if __name__ == '__main__':
    main()
