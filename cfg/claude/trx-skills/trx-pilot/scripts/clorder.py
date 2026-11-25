# Sorts the entries of each [Unreleased] subsection in docs/CHANGELOG.md:
# Added first, then Changed, then Fixed, then the rest, keeping their order.
import sys

ORDER = ("- Added", "- Changed", "- Fixed")


def rank(line):
    for idx, prefix in enumerate(ORDER):
        if line.startswith(prefix):
            return idx
    return len(ORDER)


path = sys.argv[1]
with open(path) as handle:
    lines = handle.read().split("\n")
start = next(
    i for i, line in enumerate(lines) if line.startswith("## [Unreleased")
)
end = next(
    i for i in range(start + 1, len(lines)) if lines[i].startswith("## [")
)

result = lines[:start]
block = []
for line in lines[start:end]:
    if line.startswith("- "):
        block.append(line)
        continue
    result += sorted(block, key=rank)
    block = []
    result.append(line)
result += sorted(block, key=rank)
result += lines[end:]
with open(path, "w") as handle:
    handle.write("\n".join(result))
