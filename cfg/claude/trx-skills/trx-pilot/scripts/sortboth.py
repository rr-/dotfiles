# Resolves diff3 conflict hunks by keeping the sorted union of both sides.
import re
import sys

CONFLICT = re.compile(
    r"<<<<<<< [^\n]*\n(.*?)\|\|\|\|\|\|\| [^\n]*\n.*?=======\n(.*?)>>>>>>> [^\n]*\n",
    re.S,
)


def merge(match):
    lines = (match.group(1) + match.group(2)).splitlines(True)
    return "".join(sorted({line for line in lines if line.strip()}))


path = sys.argv[1]
with open(path) as handle:
    text = handle.read()
text, count = CONFLICT.subn(merge, text)
with open(path, "w") as handle:
    handle.write(text)
print(path, count)
