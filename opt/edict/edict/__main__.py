#!/usr/bin/env python3
import argparse
import re
import gzip
import pathlib
import typing as t
from functools import reduce
import xdg
import requests
from edict import parser
from edict import db


_DL_URL = 'http://ftp.monash.edu/pub/nihongo/edict2.gz'
_RAW_PATH = pathlib.Path(xdg.XDG_CACHE_HOME) / 'edict2.txt'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Look up words in edict2 dictionary')
    parser.add_argument('pattern', nargs='+', help='regex to search for')
    parser.add_argument('--tags', nargs='*', help='regex to search tags for')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--kana', action='store_true', help='search only kana')
    group.add_argument(
        '--kanji', action='store_true', help='search only kanji')
    group.add_argument(
        '--english', action='store_true', help='search only English')
    return parser.parse_args()


def download() -> str:
    print('Downloading dictionary file...', flush=True)
    data = requests.get(_DL_URL).content
    data = gzip.decompress(data)
    return data.decode('euc-jp')


def create_db_if_needed() -> None:
    if not _RAW_PATH.exists():
        data = download()
        _RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
        _RAW_PATH.write_text(data)
    db.init()
    if not db.exists():
        print('Recreating SQLite database...', flush=True)
        with _RAW_PATH.open('r') as handle:
            db.put_entries(entry for entry in parser.parse(list(handle)))


def main() -> None:
    args = parse_args()
    patterns: t.List[str] = args.pattern
    tag_patterns: t.List[str] = args.tags or []
    sources: db.SearchSource = reduce(lambda x, y: x | y, list(db.SearchSource))
    if args.kanji:
        sources = db.SearchSource.KANJI
    elif args.kana:
        sources = db.SearchSource.KANA
    elif args.english:
        sources = db.SearchSource.ENGLISH

    create_db_if_needed()
    entries = db.search_entries_by_regex(patterns, sources)
    entries = [
        entry
        for entry in entries
        if all(
            any(re.match(tag_pattern, tag, re.I) for tag in entry.tags)
            for tag_pattern in tag_patterns)]

    for entry in entries:
        print('({})'.format(','.join(entry.tags)))
        for kanji in entry.kanji:
            print('{} ({})'.format(kanji.kanji, kanji.kana))
        for glossary in entry.glossaries:
            print(glossary.english)
        print()


if __name__ == '__main__':
    main()
