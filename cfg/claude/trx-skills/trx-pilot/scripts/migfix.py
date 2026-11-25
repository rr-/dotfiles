import re
import sys

p = sys.argv[1]
s = open(p).read()
pat = re.compile(
    r"<<<<<<< [^\n]*\n(.*?)\|\|\|\|\|\|\| [^\n]*\n.*?=======\n(.*?)>>>>>>> [^\n]*\n",
    re.S,
)


def fix(m):
    head, mine = m.group(1), m.group(2)
    hdr = "### Version 1.12 to 1.13\n\n"
    assert head.startswith(hdr) and mine.startswith(hdr), (
        head[:40],
        mine[:40],
    )
    n = len(re.findall(r"^\d+\. ", head, re.M))
    body = mine[len(hdr) :]

    # renumber mine's entries after head's
    def renum(mm):
        return f"{int(mm.group(1)) + n}. "

    body = re.sub(r"^(\d+)\. ", renum, body, flags=re.M)
    return head.rstrip("\n") + "\n\n" + body


s2, k = pat.subn(fix, s)
assert k >= 1
open(p, "w").write(s2)
print("resolved", k)
