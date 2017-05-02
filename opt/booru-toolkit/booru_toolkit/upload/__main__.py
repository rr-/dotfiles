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
        '--anonymous', action='store_true',
        help='upload anonimously if possible')
    parser.add(
        '-i', '--interactive', action='store_true',
        help='open up interactive editor')
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

    upload_settings = common.UploadSettings(
        Path(args.path),
        safety=SAFETY_MAP[args.safety],
        source=args.source,
        tags=args.tags or [],
        anonymous=args.anonymous)

    try:
        content = upload_settings.read_content()

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
            upload_settings.safety = post.safety
    except (errors.ApiError, errors.DuplicateUploadError) as ex:
        print('Error: %s' % str(ex), file=sys.stderr)
        return 1

    error_message: Optional[str] = None

    while True:
        if interactive:
            await ui.run(plugin, upload_settings, error_message)

        try:
            if post:
                if upload_settings.anonymous:
                    raise errors.ApiError(
                        'Anonymous post updates are not supported.')
                await plugin.update_post(
                    post.id,
                    safety=upload_settings.safety,
                    tags=upload_settings.tag_names)
                print('Updated.')
            else:
                post = await plugin.upload_post(
                    content,
                    source=upload_settings.source,
                    safety=upload_settings.safety,
                    tags=upload_settings.tag_names,
                    anonymous=upload_settings.anonymous)
                print('Uploaded.')

            if post:
                print('Address: ' + post.content_url)
            return 0

        except (errors.ApiError, errors.DuplicateUploadError) as ex:
            if interactive:
                error_message = str(ex)
                continue
            else:
                print('Error: %s' % str(ex), file=sys.stderr)
                return 1


def main() -> int:
    args = parse_args()
    loop = asyncio.get_event_loop()
    try:
        try:
            task = loop.create_task(run(args))
            exit_code = loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_until_complete(task)
    except concurrent.futures.CancelledError:
        print('Aborted.')
        exit_code = 1
    finally:
        loop.close()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
