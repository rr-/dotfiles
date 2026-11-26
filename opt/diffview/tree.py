"""The file tree shown on the left."""

import dataclasses as dc

from .model import Commit, FileDiff


@dc.dataclass(eq=False)
class Node:
    name: str
    parent: "Node | None" = None
    file: int | None = None
    children: dict[str, "Node"] = dc.field(default_factory=dict)
    expanded: bool = True
    commit: bool = False
    rank: int = 0
    message: int | None = None  # the commit whose message this leaf opens

    @property
    def is_dir(self) -> bool:
        return self.file is None and self.message is None

    def sorted_children(self) -> list["Node"]:
        def key(n: Node) -> tuple:
            kind = 0 if n.message is not None else 1 if n.is_dir else 2
            return (kind, n.rank, n.name, n.file or 0)

        return sorted(self.children.values(), key=key)


def build_tree(
    files: list[FileDiff], commits: list[Commit], by_commit: bool = False
) -> Node:
    """Files under their directories, and under their commit when there
    are several, or always with by_commit."""
    root = Node("")
    grouped = by_commit or (
        len({f.commit for f in files} | set(range(len(commits)))) > 1
    )

    def group(ci: int) -> Node:
        if not grouped:
            return root
        # Short names: the tree is as wide as its widest entry.
        name = "no commit"
        if ci >= 0:
            name = commits[ci].sha[:7] or f"commit {ci + 1}"
            if commits[ci].unit:
                name = commits[ci].lines[0]
        return root.children.setdefault(
            f"c:{ci}", Node(name, parent=root, commit=True, rank=ci)
        )

    for ci in range(len(commits)):
        parent = group(ci)
        parent.children[f"m:{ci}"] = Node("message", parent=parent, message=ci)
    for fi, f in enumerate(files):
        node = group(f.commit)
        *dirs, name = f.path.split("/")
        for part in dirs:
            node = node.children.setdefault(
                f"d:{part}", Node(part, parent=node)
            )
        node.children[f"f:{name}:{fi}"] = Node(name, parent=node, file=fi)

    def squash(node: Node) -> None:
        for child in node.children.values():
            while (
                child.is_dir and not child.commit and len(child.children) == 1
            ):
                (only,) = child.children.values()
                if not only.is_dir:
                    break
                child.name += "/" + only.name
                child.children = only.children
                for grandchild in child.children.values():
                    grandchild.parent = child
            squash(child)

    squash(root)
    return root


def walk_tree(node: Node, depth: int = 0, everything: bool = False):
    for child in node.sorted_children():
        yield depth, child
        if child.is_dir and (child.expanded or everything):
            yield from walk_tree(child, depth + 1, everything)


def tree_guides(node: Node, depth: int) -> str:
    """Box-drawing guides for a row, two cells per level below the top."""

    def last(n: Node) -> bool:
        return n.parent.sorted_children()[-1] is n

    if depth == 0:
        return ""
    guides = ["└─" if last(node) else "├─"]
    n = node.parent
    for _ in range(depth - 1):
        guides.append("  " if last(n) else "│ ")
        n = n.parent
    return "".join(reversed(guides))
