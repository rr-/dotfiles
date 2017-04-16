import re
from pathlib import Path


DB_DIR = Path('~/.local/share/yume-tagger/').expanduser()


def confirm(text: str) -> bool:
    while True:
        result = input('{} '.format(text.strip())).lower()
        if result in ['yes', 'yep', 'yeah', 'y', 'true']:
            return True
        if result in ['no', 'nah', 'nay', 'n', 'false']:
            return False


def sanitize_tag(name: str) -> str:
    return re.sub(r'\s+', '_', name)


def capitalize(name: str) -> str:
    return re.sub(r'(^|[_()])([a-z])', lambda m: m.group(0).upper(), name)
