#!/bin/python3
import os
import sys
import argparse
import json
import subprocess
import shlex
import socket
from datetime import datetime

# configuration
MINIMUM_WATCHED_PERCENTAGE = 80
MINIMUM_DURATION = 300 # five minutes
IGNORE_ONLINE_STREAMS = True
REMOTE_HOST = 'burza'
REMOTE_LOG_PATH = '/srv/www/tmp.sakuya.pl/public_html/mal/watched.lst'
ALLOWED_EXTENSIONS = ['mpv', 'mp4', 'avi', 'm4v', 'mov', 'flv', 'mpeg', 'mpg', 'wmv', 'ogv', 'webm', 'rm']

def parse_args():
    parser = argparse.ArgumentParser(description='Send playback log')
    parser.add_argument('--path', required=True)
    parser.add_argument('--percent', required=True, type=float)
    parser.add_argument('--duration', required=True, type=float)
    return parser.parse_args()

def main():
    args = parse_args()

    try:
        _,  extension = os.path.splitext(args.path)
        extension = extension.strip('.')

        if extension.lower() not in ALLOWED_EXTENSIONS:
            raise RuntimeError('Extension doesn\'t match allowed files, skipping')

        if not args.duration:
            raise RuntimeError('No information on duration, skipping')

        if not args.percent:
            raise RuntimeError('No information on % watched, skipping')

        if IGNORE_ONLINE_STREAMS and args.path.startswith('http'):
            raise RuntimeError('Online stream detected, skipping')

        if args.percent < MINIMUM_WATCHED_PERCENTAGE:
            raise RuntimeError(
                'Watched too little (%.02f%% < %.02f%%), skipping' % (
                    args.percent,
                    MINIMUM_WATCHED_PERCENTAGE))

        if args.duration < MINIMUM_DURATION:
            raise RuntimeError(
                'File is too short (%.02fs < %.02fs), skipping' % (
                    duration,
                    minimum_duration))

        line = json.dumps({
            'date': datetime.now().isoformat(),
            'host': socket.gethostname(),
            'path': args.path,
        })

        print('Sending JSON: ' + line)
        subprocess.run(
            [
                'ssh',
                REMOTE_HOST,
                'echo',
                shlex.quote(line),
                '>>',
                shlex.quote(REMOTE_LOG_PATH),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True)

    except Exception as e:
        print(e, file=sys.stderr)

if __name__ == '__main__':
    main()
