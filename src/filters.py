from fnmatch import fnmatch


def normalize_extension(value):
    value = value.strip().lower()
    return value if value.startswith(".") else f".{value}"


def matches_any(path, root, patterns):
    relative = path.relative_to(root).as_posix()
    return any(fnmatch(path.name, p) or fnmatch(relative, p) for p in patterns)


def is_included_type(path, extensions, names):
    if not extensions and not names:
        return True
    return path.suffix.lower() in extensions or path.name.lower() in names


def is_output_artifact(path, output):
    return (
        path.parent == output.parent
        and path.suffix == output.suffix
        and path.stem.startswith(output.stem)
    )
