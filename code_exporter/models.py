from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFile:
    rel_path: str
    text: str


@dataclass(frozen=True)
class Segment:
    rel_path: str
    index: int
    total: int
    text: str
