#!/bin/python3
import os
import sys
import argparse
import subprocess
import shlex
import socket
from datetime import datetime


# configuration
MINIMUM_WATCHED_PERCENTAGE = 80
MINIMUM_DURATION = 300  # five minutes
IGNORE_ONLINE_STREAMS = True
REMOTE_HOST = 'cyclone'
REMOTE_LOG_PATH = '/srv/www/sakuya.pl/data/playback.lst'
ALLOWED_EXTENSIONS = [
    'mkv', 'mp4', 'avi', 'm4v', 'mov',
    'flv', 'mpeg', 'mpg', 'wmv', 'ogv', 'webm', 'rm']


def parse_args():
    parser = argparse.ArgumentParser(description='Send playback log')
    parser.add_argument('--path', required=True)
    parser.add_argument('--percent', required=True, type=float)
    parser.add_argument('--duration', required=True, type=float)
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        _, extension = os.path.splitext(args.path)
        extension = extension.strip('.')

        if extension.lower() not in ALLOWED_EXTENSIONS:
            raise RuntimeError(
                'Extension doesn\'t match allowed files, skipping')

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
                    args.duration,
                    MINIMUM_DURATION))

        line = '%s %s %s' % (
            datetime.now().replace(microsecond=0).isoformat(),
            socket.gethostname(),
            os.path.abspath(args.path))

        print('Sending data: ' + line)
        subprocess.run(
            [
                'ssh',
                REMOTE_HOST,
                'echo',
                shlex.quote(line).encode('utf-8').decode('unicode-escape'),
                '>>',
                shlex.quote(REMOTE_LOG_PATH),
            ],
            check=True)

    except Exception as ex:
        print(ex, file=sys.stderr)

if __name__ == '__main__':
    main()
