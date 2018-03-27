import subprocess
import os
import platform


def capture(output_dir, duration, interval):
    print('capturing one photo every {interval} seconds for {duration} seconds'.format(
        duration=duration,
        interval=interval,
    ))
    
    if platform.system() == 'Darwin':
        formats = 'avfoundation'
    elif platform.system() == 'Windows':    
        formats = 'dshow'

    video = os.getenv("FFMPEG_VIDEO")

    print('using {formats} and {video}'.format(formats = formats, video = video))
    capture_rate = '1/{}'.format(interval)
    output_pattern = '{}/image%d.png'.format(output_dir)
    # TODO check exit status
    subprocess.call([
        'ffmpeg',
        '-loglevel', 'warning',
        '-f', formats,
        '-i', 'video={}'.format(video),
        '-t', str(duration),
        '-s', '1280x720',
        '-framerate', '30',
        '-r', capture_rate,
        output_pattern,
    ])

def compile_video(photos_dir, output_filename, photos_per_second=30):
    print('compiling timelapse (photos per second: {photos_per_second})'.format(
        photos_per_second=photos_per_second,
    ))
    # TODO ensure output_filename ends with .mp4
    photos_pattern = '{}/image%05d.png'.format(photos_dir)
    # TODO check exit status
    subprocess.call([
        'ffmpeg',
        '-loglevel', 'warning',
        '-framerate', str(photos_per_second),
        '-i', photos_pattern,
        '-c:v', 'libx264',
        #'-r', '30',
        '-pix_fmt', 'yuv420p',
        output_filename,
    ])
