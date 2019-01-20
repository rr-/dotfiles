from collections import defaultdict

from bubblesub.api import Api


def check_styles(api: Api) -> None:
    api.log.info("Styles summary:")
    styles = defaultdict(int)

    for line in api.subs.events:
        styles[line.style] += 1

    for style, occurrences in sorted(styles.items(), key=lambda kv: -kv[1]):
        api.log.info(f"– {occurrences} time(s): {style}")
