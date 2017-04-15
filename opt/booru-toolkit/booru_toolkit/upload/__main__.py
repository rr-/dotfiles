import asyncio
import concurrent.futures
import sys
from pathlib import Path
from typing import Optional, List
import aioconsole
import configargparse
from booru_toolkit import errors
from booru_toolkit import cli
from booru_toolkit.plugin import Safety
from booru_toolkit.plugin import PluginBase
from booru_toolkit.plugin import PluginYume
from booru_toolkit.plugin import PluginGelbooru
from booru_toolkit.upload import common
from booru_toolkit.upload import ui


PLUGINS: List[PluginBase] = [PluginGelbooru(), PluginYume()]
SAFETY_MAP = {
    'safe': Safety.Safe,
    'sketchy': Safety.Questionable,
    'questionable': Safety.Questionable,
    'unsafe': Safety.Explicit,
    'explicit': Safety.Explicit,
    's': Safety.Safe,
    'q': Safety.Questionable,
    'e': Safety.Explicit,
}


def parse_args() -> configargparse.Namespace:
    parser = cli.make_arg_parser('Sends post to various boorus.', PLUGINS)
    parser.add(
        '-s', '--safety', metavar='SAFETY', default='safe', required=False,
        choices=SAFETY_MAP.keys(),
        help='post safety ({safe,questionable,explicit})')
    parser.add('--source', default='', help='post source')
    parser.add(
        '-t', '--tags', nargs='*', metavar='TAG',
        help='list of post tags')
    parser.add(
        '-i', '--interactive', action='store_true',
        help='edit tags interactively')
    parser.add(metavar='POST_PATH', dest='path', help='path to the post')
    return parser.parse_args()


async def confirm_similar_posts(plugin: PluginBase, content: bytes) -> None:
    similar_posts = await plugin.find_similar_posts(content)
    if not similar_posts:
        return
    print('Similar posts found:')
    for similarity, post in similar_posts:
        print('%.02f: %s (%dx%d)' % (
            similarity,
            post.site_url,
            post.width,
            post.height))
    await aioconsole.ainput('Hit enter to continue, ^C to abort\n')


async def run(args: configargparse.Namespace) -> int:
    plugin: PluginBase = args.plugin
    user_name: str = args.user
    password: str = args.password

    interactive: bool = args.interactive
    path: Path = Path(args.path)

    upload_settings = common.UploadSettings(
        safety=SAFETY_MAP[args.safety],
        source=args.source,
        tags=args.tags or [])

    try:
        if not path.exists():
            raise errors.NoContentError()
        with path.open('rb') as handle:
            content = handle.read()

        print('Logging in...')
        await plugin.login(user_name, password)

        print('Searching for duplicates...')
        post = await plugin.find_exact_post(content)
        if not post:
            await confirm_similar_posts(plugin, content)

        print('Gathering tags...')
        if post:
            for tag in post.tags:
                upload_settings.tags.add(tag, common.TagSource.Initial)

        if interactive:
            await ui.run(plugin, path, upload_settings)

        print('Tags:')
        print('\n'.join(upload_settings.tag_names))

        if post:
            await plugin.update_post_tags(post, upload_settings.tag_names)
            print('Updated.')
        else:
            post = await plugin.upload_post(
                content,
                source=upload_settings.source,
                safety=upload_settings.safety,
                tags=upload_settings.tag_names)
            print('Uploaded.')

        if post:
            print('Address: ' + post.content_url)
        return 0

    except (errors.ApiError, errors.DuplicateUploadError) as ex:
        print('Error: %s' % str(ex), file=sys.stderr)

    return 1


def main() -> int:
    args = parse_args()
    loop = asyncio.get_event_loop()
    try:
        try:
            task = loop.create_task(run(args))
            result = loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_until_complete(task)
    except concurrent.futures.CancelledError:
        print('Aborted.')
        result = 1
    finally:
        loop.close()
    sys.exit(result)


if __name__ == '__main__':
    main()
