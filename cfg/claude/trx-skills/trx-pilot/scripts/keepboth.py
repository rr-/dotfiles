# Resolves diff3 conflict hunks in a file by keeping both sides, ours first.
import re
import sys

CONFLICT = re.compile(
    r"<<<<<<< [^\n]*\n(.*?)\|\|\|\|\|\|\| [^\n]*\n.*?=======\n(.*?)>>>>>>> [^\n]*\n",
    re.S,
)

path = sys.argv[1]
with open(path) as handle:
    text = handle.read()
text, count = CONFLICT.subn(lambda m: m.group(1) + m.group(2), text)
with open(path, "w") as handle:
    handle.write(text)
print(path, count)
