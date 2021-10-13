import asyncio
import concurrent.futures
import sys
from asyncio.exceptions import CancelledError
from enum import Enum
from pathlib import Path
from typing import Optional

import aioconsole
import configargparse

from booru_toolkit import cli, errors
from booru_toolkit.plugin import (
    PluginBase,
    PluginGelbooru,
    PluginYume,
    Post,
    Safety,
)
from booru_toolkit.upload import common, ui

PLUGINS: list[PluginBase] = [PluginGelbooru(), PluginYume()]
SAFETY_MAP = {
    "safe": Safety.Safe,
    "sketchy": Safety.Questionable,
    "questionable": Safety.Questionable,
    "unsafe": Safety.Explicit,
    "explicit": Safety.Explicit,
    "s": Safety.Safe,
    "q": Safety.Questionable,
    "e": Safety.Explicit,
}


def parse_args() -> configargparse.Namespace:
    parser = cli.make_arg_parser("Sends post to various boorus.", PLUGINS)
    parser.add(
        "-s",
        "--safety",
        metavar="SAFETY",
        default="safe",
        required=False,
        choices=SAFETY_MAP.keys(),
        help="post safety ({safe,questionable,explicit})",
    )
    parser.add("--source", default="", help="post source")
    parser.add(
        "-t", "--tags", nargs="*", metavar="TAG", help="list of post tags"
    )
    parser.add(
        "--anonymous",
        action="store_true",
        help="upload anonimously if possible",
    )
    parser.add(
        "-i",
        "--interactive",
        action="store_true",
        help="open up interactive editor",
    )
    parser.add(metavar="POST_PATH", dest="path", help="path to the post")
    parser.add("-n", "--no-prompt", dest="prompt", action="store_false")
    return parser.parse_args()


async def confirm_similar_posts(
    plugin: PluginBase, content: bytes, prompt: bool
) -> Optional[Post]:
    similar_posts = await plugin.find_similar_posts(content)
    if not similar_posts:
        return None
    print("Similar posts found:")
    for similarity, post in similar_posts:
        print(
            "%.02f: %s (%dx%d)"
            % (similarity, post.site_url, post.width, post.height)
        )
    for similarity, post in similar_posts:
        if similarity == 0.0:
            print("There is an identical post out there")
            return post
    if not prompt:
        print("Prompting disabled, aborting")
        raise CancelledError
    await aioconsole.ainput("Hit enter to continue, ^C to abort\n")
    return None


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
        anonymous=args.anonymous,
    )

    print(upload_settings.path.absolute().as_uri())

    try:
        content = upload_settings.read_content()

        print("Logging in...")
        await plugin.login(user_name, password)

        print("Searching for duplicates...")
        post = await plugin.find_exact_post(content)
        if not post:
            post = await confirm_similar_posts(
                plugin, content, prompt=args.prompt
            )

        print("Gathering tags...")
        if post:
            for tag in post.tags:
                upload_settings.tags.add(tag, common.TagSource.Initial)
            upload_settings.safety = post.safety
    except (errors.ApiError, errors.DuplicateUploadError) as ex:
        print("Error: %s" % str(ex), file=sys.stderr)
        return 1

    error_message: Optional[str] = None

    while True:
        if interactive:
            await ui.run(plugin, upload_settings, error_message)

        try:
            if post:
                if upload_settings.anonymous:
                    raise errors.ApiError(
                        "Anonymous post updates are not supported."
                    )
                await plugin.update_post(
                    post.id,
                    safety=upload_settings.safety,
                    tags=upload_settings.tag_names,
                )
                print("Updated.")
            else:
                post = await plugin.upload_post(
                    content,
                    source=upload_settings.source,
                    safety=upload_settings.safety,
                    tags=upload_settings.tag_names,
                    anonymous=upload_settings.anonymous,
                )
                print("Uploaded.")

            if post:
                print("Address: " + post.content_url)
            return 0

        except (errors.ApiError, errors.DuplicateUploadError) as ex:
            if interactive:
                error_message = str(ex)
                continue
            else:
                print("Error: %s" % str(ex), file=sys.stderr)
                return 1


def main() -> int:
    args = parse_args()
    loop = asyncio.get_event_loop()
    task = loop.create_task(run(args))
    asyncio.ensure_future(task)
    try:
        loop.run_until_complete(task)
        exit_code = task.result()
    except (KeyboardInterrupt, CancelledError):
        print("Aborted.")
        task.cancel()
        exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
