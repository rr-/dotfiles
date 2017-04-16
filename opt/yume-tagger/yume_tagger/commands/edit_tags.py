import sys
from typing import Dict
import configargparse
import tabulate
from yume_tagger import util
from yume_tagger.api import Api, Tag
from yume_tagger.autotag_settings import AutoTagSettings
from yume_tagger.commands.base import BaseCommand


def _serialize_tags(tags: Dict[int, Tag]) -> str:
    return tabulate.tabulate(
        [
            [
                tag_id,
                ' '.join(tag['names']),
                ' '.join(tag['implications']),
                ' '.join(tag['suggestions']),
                tag['category'],
                tag['usages'],
            ]
            for tag_id, tag in tags.items()
        ],
        headers=[
            'ID',
            'Names',
            'Implications',
            'Suggestions',
            'Category',
            'Usages',
        ],
        tablefmt='pipe')


def _deserialize_tags(text: str) -> Dict[int, Tag]:
    ret: Dict[int, Tag] = {}

    past_header = False
    for i, line in enumerate(text.split('\n')):
        try:
            if not line:
                continue
            assert line.startswith('|'), 'Line should start with "|"'
            assert line.endswith('|'), 'Line should end with "|"'

            if ' ' not in line.strip():
                past_header = True
            elif past_header:
                row = [cell.strip() for cell in line.strip('|').split('|')]
                tag_id = int(row[0])
                tag_names = list(set(row[1].split()))
                tag_implications = list(set(row[2].split()))
                tag_suggestions = list(set(row[3].split()))
                tag_category = row[4]
                tag_usages = int(row[5])

                assert tag_id not in ret, 'Tag appears twice'

                ret[tag_id] = {
                    'names': tag_names,
                    'implications': tag_implications,
                    'suggestions': tag_suggestions,
                    'category': tag_category,
                }

        except Exception as ex:
            raise ValueError('Syntax error near line {}: {}'.format(i + 1, ex))

    if not past_header:
        raise ValueError('Syntax error: header not found')

    return ret


def _edit_tags_interactively(tags: Dict[int, Tag]) -> Dict[int, Tag]:
    return util.run_editor(
        'tags.txt', tags, _serialize_tags, _deserialize_tags)


def _delete_tag(api: Api, autotag_settings: AutoTagSettings, tag: Tag) -> None:
    if util.confirm('Delete tag {}?'.format(tag['names'][0])):
        api.delete_tag(tag)
    for tag_name in tag['names']:
        if not autotag_settings.is_tag_banned(tag_name):
            if util.confirm('Ban autotagging {}?'.format(tag_name)):
                autotag_settings.ban_tag(tag_name)


def _create_tag(api: Api, autotag_settings: AutoTagSettings, tag: Tag) -> None:
    if util.confirm('Create tag {}?'.format(tag['names'][0])):
        api.create_tag(tag)
    for tag_name in tag['names']:
        if autotag_settings.is_tag_banned(tag_name):
            if util.confirm('Unban autotagging {}?'.format(tag_name)):
                autotag_settings.unban_tag(tag_name)


def _update_tag(api: Api, old_tag: Tag, new_tag: Tag) -> None:
    request: Dict = {}
    for key in ['names', 'implications', 'suggestions']:
        if sorted(old_tag[key]) != sorted(new_tag[key]):
            request[key] = new_tag[key]
    if old_tag['category'] != new_tag['category']:
        request['category'] = new_tag['category']

    if not request:
        return

    if util.confirm('Update tag {} ({})?'.format(
            new_tag['names'][0], request)):
        request['version'] = old_tag['version']
        api.update_tag(old_tag['names'][0], request)


def _update_tags(
        api: Api,
        autotag_settings: AutoTagSettings,
        old_tags: Dict[int, Tag],
        new_tags: Dict[int, Tag]) -> None:
    for old_tag_id, old_tag in old_tags.items():
        try:
            if old_tag_id not in new_tags:
                _delete_tag(api, autotag_settings, old_tag)
        except Exception as ex:
            print(ex, file=sys.stderr)

    for new_tag_id, new_tag in new_tags.items():
        try:
            if new_tag_id not in old_tags:
                _create_tag(api, autotag_settings, new_tag)
            else:
                old_tag = old_tags[new_tag_id]
                _update_tag(api, old_tag, new_tag)
        except Exception as ex:
            print(ex, file=sys.stderr)


class EditTagsCommand(BaseCommand):
    def run(self, args: configargparse.Namespace) -> None:
        query: str = args.query
        old_tags = {
            i + 1: old_tag
            for i, old_tag in enumerate(self._api.find_tags(query))
        }
        new_tags = _edit_tags_interactively(old_tags)
        _update_tags(self._api, self._autotag_settings, old_tags, new_tags)

    @staticmethod
    def _create_parser(
            parent_parser: configargparse.ArgumentParser
    ) -> configargparse.ArgumentParser:
        parser = parent_parser.add_parser(
            'edit', help='edit tags interactively')
        parser.add('query', help='query to filter the tags with')
        return parser
