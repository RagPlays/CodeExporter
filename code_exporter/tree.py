INDENT = "  "
SEPARATOR = "/"


def _nest(paths):
    root = {}
    for path in paths:
        node = root
        for part in path.split(SEPARATOR):
            node = node.setdefault(part, {})
    return root


def _render(node, depth=0):
    ordered = sorted(node.items(), key=lambda item: (not item[1], item[0].lower()))
    for name, child in ordered:
        yield f"{INDENT * depth}{name}{SEPARATOR if child else ''}"
        yield from _render(child, depth + 1)


def render_tree(paths):
    return "\n".join(_render(_nest(paths)))
