from collections import defaultdict

from bubblesub.api import Api


def check_actors(api: Api) -> None:
    api.log.info("Actors summary:")
    actors = defaultdict(int)

    for line in api.subs.events:
        actors[line.actor] += 1

    for actor, occurrences in sorted(actors.items(), key=lambda kv: -kv[1]):
        api.log.info(f"– {occurrences} time(s): {actor}")
