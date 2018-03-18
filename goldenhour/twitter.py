from __future__ import absolute_import

import argparse
import twitter
import yaml
import os

from twitter.twitter_utils import parse_media_file

def load_credentials():
    return {
        'consumer_key': os.getenv("TWITTER_CONSUMER_KEY"),
        'consumer_secret': os.getenv("TWITTER_CONSUMER_SECRET"),
        'access_token_key': os.getenv("TWITTER_ACCESS_TOKEN_KEY"),
        'access_token_secret': os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    }


def verify_credentials():
    credentials = load_credentials()
    api = twitter.Api(**credentials)

    assert api.VerifyCredentials() is not None


def post_update(text, media=None):
    print('posting to twitter (status_text: {}, media: {})'.format(text, media))
    credentials = load_credentials()
    api = twitter.Api(**credentials)

    media_id = None
    if media:
        with open(media, 'rb') as mediafile:
            media_id = api.UploadMediaChunked(mediafile)

    api.PostUpdate(text, media=media_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    parser.add_argument('--media', default=None)
    args = parser.parse_args()
    post_update(args.text, args.media)


if __name__ == '__main__':
    main()
