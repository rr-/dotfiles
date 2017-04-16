import re
import json
from typing import Optional, List, Callable, Iterable
import configargparse
import requests
from bs4 import BeautifulSoup
from yume_tagger import iqdb
from yume_tagger import util
from yume_tagger.api import Api, ApiError, Post
from yume_tagger.autotag_settings import AutoTagSettings
from yume_tagger.commands.base import BaseCommand


CACHE_PATH = util.DB_DIR.joinpath('cache')
TAGS_TO_REMOVE = ['tagme']


class AutoTagError(RuntimeError):
    pass


class TooBigError(AutoTagError):
    pass


class _ThirdPartyTag:
    def __init__(self, name: str, category: str) -> None:
        self.name = name
        self.category = category
        # TODO: info about source


class _SyncInfo:
    def __init__(self) -> None:
        self.source_tags: List[str] = []
        self.target_tags: List[str] = []
        self.tags_to_create: List[_ThirdPartyTag] = []


def _get_tags_from_gelbooru(url: str) -> Iterable[_ThirdPartyTag]:
    if 'gelbooru' not in url:
        raise ValueError('Not a valid Gelbooru URL')
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    list_items = soup.select('#tag-sidebar li')
    for list_item in list_items:
        try:
            category = list_item['class'][0].replace('tag-type-', '')
            name = list_item.select('a')[1].text.replace(' ', '_')
            yield _ThirdPartyTag(name, category)
        except IndexError:
            pass


def _get_tags_from_danbooru(url: str) -> Iterable[_ThirdPartyTag]:
    match = re.search(r'danbooru.*?(\d+)', url)
    if not match:
        raise ValueError('Not a valid Danbooru URL')
    post_id = int(match.group(1))
    session = requests.Session()
    response = session.get(
        'http://danbooru.donmai.us/posts/{}.json'.format(post_id))
    post = json.loads(response.text)
    for category in ['artist', 'character', 'copyright', 'general']:
        for name in post['tag_string_' + category].split(' '):
            if name:
                yield _ThirdPartyTag(name, category)


def _get_third_party_tags(source_urls: List[str]) -> List[_ThirdPartyTag]:
    handlers: List[Callable[[str], Iterable[_ThirdPartyTag]]] = [
        _get_tags_from_danbooru,
        _get_tags_from_gelbooru,
    ]
    ret: List[_ThirdPartyTag] = []
    for handler in handlers:
        for source_url in source_urls:
            try:
                ret.extend(list(handler(source_url)))
            except (ValueError, NotImplementedError):
                pass
    return ret


def _get_third_party_tag_sources(post_url: str) -> List[str]:
    try:
        return [
            result.url
            for result in iqdb.search(post_url)
            if result.similarity >= 0.90]
    except iqdb.NothingFoundIqdbError:
        return []
    except iqdb.UploadTooBigIqdbError:
        raise TooBigError('Post is too big to search for')


def _get_post(
        api: Api,
        autotag_settings: AutoTagSettings,
        post_id: int,
        skip_history: bool) -> Optional[Post]:
    if post_id in autotag_settings.get_processed_post_ids() \
            and not skip_history:
        print('Skipping post {} - already processed'.format(post_id))
        return None

    print('Retrieving post {}...'.format(post_id))
    post = api.get_post(post_id)
    print(post['contentUrl'])
    print()
    return post


def _collect_third_party_tags(
        post: Post, source: Optional[str] = None) -> List[_ThirdPartyTag]:
    print('Collecting third party tags...')

    cache_path = CACHE_PATH.joinpath('autotagger-{}.dat'.format(post['id']))
    if cache_path.exists():
        result = json.loads(cache_path.read_text())
        sources = result['sources']
        third_party_tags = [
            _ThirdPartyTag(name=tag['name'], category=tag['category'])
            for tag in result['tags']
        ]
    else:
        if source:
            sources = [source]
        else:
            try:
                sources = _get_third_party_tag_sources(post['contentUrl'])
            except TooBigError:
                sources = _get_third_party_tag_sources(post['thumbnailUrl'])
        third_party_tags = _get_third_party_tags(sources)

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps({
            'sources': sources,
            'tags': [
                {'name': tag.name, 'category': tag.category}
                for tag in third_party_tags],
        }))

    if sources:
        print('Sources:')
        for source in sorted(sources):
            print('- {}'.format(source))
        if not third_party_tags:
            raise AutoTagError('Tag sources found, but not on any known site')
    else:
        raise AutoTagError('No tag sources')

    print('Tags:')
    for tag in third_party_tags:
        print('- {}'.format(tag.name))
    print()
    return third_party_tags


def _sanitize_third_party_tags(
        autotag_settings: AutoTagSettings,
        third_party_tags: List[_ThirdPartyTag]) -> Iterable[_ThirdPartyTag]:
    for tag in third_party_tags:
        if autotag_settings.is_tag_banned(tag.name):
            print('Ignored tag {}'.format(tag.name))
            continue

        translated_tag = autotag_settings.translate_tag(tag.name)
        if tag.name != translated_tag:
            print('Translated tag {} → {}'.format(tag.name, translated_tag))

        sanitized_name = util.sanitize_tag(translated_tag)
        if sanitized_name != tag.name:
            print('Sanitized tag {} → {}'.format(tag.name, sanitized_name))

        yield _ThirdPartyTag(
            name=sanitized_name,
            category=autotag_settings.translate_tag_category(tag.category))


def _get_sync_info(
        api: Api,
        autotag_settings: AutoTagSettings,
        post: Post,
        third_party_tags: List[_ThirdPartyTag]) -> _SyncInfo:
    sync_info = _SyncInfo()
    sync_info.source_tags = [tag.lower() for tag in post['tags']]
    sync_info.target_tags = sync_info.source_tags[:]

    for third_party_tag in _sanitize_third_party_tags(
            autotag_settings, third_party_tags):
        if third_party_tag.name.lower() in sync_info.source_tags:
            continue

        sync_info.target_tags.append(third_party_tag.name)

        try:
            api.get_tag(third_party_tag.name)
        except ApiError as ex:
            if 'not found' in str(ex).lower():
                sync_info.tags_to_create.append(third_party_tag)
            else:
                raise

        for implication in api.get_tag_implications(third_party_tag.name):
            implication = implication.lower()
            if implication not in sync_info.target_tags:
                sync_info.target_tags.append(implication)

    for tag_name in TAGS_TO_REMOVE:
        if tag_name.lower() in sync_info.source_tags:
            sync_info.target_tags.remove(tag_name)

    return sync_info


def _create_new_tags(
        api: Optional[Api],
        tags_to_create: List[_ThirdPartyTag]) -> None:
    print('Creating new tags...')
    if not tags_to_create:
        print('(no tags to create.)')
    else:
        for new_tag in tags_to_create:
            if new_tag.category in ('artist', 'copyright', 'character'):
                new_tag.name = util.capitalize(new_tag.name)
            print('- {}'.format(new_tag.name))
            if api:
                api.create_tag({
                    'names': [new_tag.name],
                    'category': new_tag.category,
                })
        print('Created {} new tags.'.format(len(tags_to_create)))
    print()


def _update_post_tags(
        api: Optional[Api],
        post: Post,
        source_tags: List[str],
        target_tags: List[str]) -> None:
    print('Updating post tags...')
    if target_tags == source_tags:
        print('(nothing to be done.)')
    else:
        for tag_name in target_tags:
            print('- {}{}'.format(
                '(new) ' if tag_name not in source_tags else '',
                tag_name))
        if api:
            api.update_post(
                post['id'],
                {
                    'tags': [tag_name for tag_name in target_tags],
                    'version': post['version'],
                })
        print('Added {} new tags.'.format(len(target_tags) - len(source_tags)))
    print()


def _sync(
        api: Api,
        autotag_settings: AutoTagSettings,
        post_id: int,
        source: Optional[str],
        force: bool,
        dry_run: bool) -> None:
    post = _get_post(api, autotag_settings, post_id, force)
    if not post:
        return
    third_party_tags = _collect_third_party_tags(post, source)
    sync_info = _get_sync_info(api, autotag_settings, post, third_party_tags)
    _create_new_tags(None if dry_run else api, sync_info.tags_to_create)
    _update_post_tags(
        None if dry_run else api,
        post,
        sync_info.source_tags,
        sync_info.target_tags)


class AutoTagChosenPostCommand(BaseCommand):
    def run(self, args: configargparse.Namespace) -> None:
        source: Optional[str] = args.source
        force: bool = args.force
        dry_run: bool = args.dry_run

        for post_id in args.post_ids:
            try:
                _sync(
                    self._api,
                    self._autotag_settings,
                    post_id,
                    source,
                    force,
                    dry_run)
                if not dry_run:
                    self._autotag_settings.mark_as_tagged(post_id)
            except Exception as ex:
                if not dry_run:
                    self._autotag_settings.mark_as_untagged(post_id)
                raise

    @staticmethod
    def _create_parser(
            parent_parser: configargparse.ArgumentParser
    ) -> configargparse.ArgumentParser:
        parser = parent_parser.add_parser(
            'autotag-chosen', help='fetch tags for chosen posts')
        parser.add_argument(
            metavar='POST_ID', dest='post_ids', nargs='*', type=int,
            help='ID of the post to edit the tags for.')
        parser.add_argument(
            '-f', '--force', action='store_true', help=(
                'Force downloading post tags, even if the post was ' +
                'processed earlier.'))
        parser.add_argument(
            '--source', help='Source URL where to get tags from.')
        parser.add_argument(
            '--dry-run', action='store_true', help='Don\'t do anything.')
        return parser


class AutoTagNewestPostCommand(BaseCommand):
    def run(self, args: configargparse.Namespace) -> None:
        post_id = self._get_last_post_id()
        dry_run: bool = args.dry_run

        if not post_id:
            print('Everything up to date')
            return
        try:
            _sync(
                self._api,
                self._autotag_settings,
                post_id,
                None,
                False,
                dry_run)
            if not dry_run:
                self._autotag_settings.mark_as_tagged(post_id)
        except Exception as ex:
            if not dry_run:
                self._autotag_settings.mark_as_untagged(post_id)
            raise

    @staticmethod
    def _create_parser(
            parent_parser: configargparse.ArgumentParser
    ) -> configargparse.ArgumentParser:
        parser = parent_parser.add_parser(
            'autotag-newest', help='fetch tags for newest posts')
        parser.add_argument(
            '--dry-run', action='store_true', help='Don\'t do anything.')
        return parser

    def _get_last_post_id(self) -> Optional[int]:
        latest_id = self._api.get_last_post_id()
        if latest_id is None:
            return None
        processed_post_ids = self._autotag_settings.get_processed_post_ids()
        for post_id in range(1, latest_id + 1):
            if post_id not in processed_post_ids:
                return post_id
        return None
