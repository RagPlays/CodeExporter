CHUNK_JOINER = "\n"
ENCODING = "utf-8"


def chunk_paths(output, total):
    width = len(str(total))
    return [
        output.with_name(f"{output.stem}_{i:0{width}d}{output.suffix}")
        for i in range(1, total + 1)
    ]


def _targets_and_payloads(texts, settings):
    if settings.split_output:
        return chunk_paths(settings.output, len(texts)), texts
    return [settings.output], [CHUNK_JOINER.join(texts)]


def write_output(texts, settings):
    targets, payloads = _targets_and_payloads(texts, settings)
    for target, payload in zip(targets, payloads):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding=ENCODING)
    return targets
