from dataclasses import dataclass
from typing import List, Tuple

from .models import Card, Observation


@dataclass(frozen=True)
class Breakpoint:
    """Wording for a rule once the tag count reaches min_count.

    finding/detail are str.format() templates; {count} and {names} are always
    available regardless of whether a given template uses them.
    """
    min_count: int
    finding: str
    detail: str


@dataclass(frozen=True)
class TagThresholdRule:
    """Declarative shape for rules that filter cards by one tag, count them,
    and pick wording based on breakpoints in that count (0 / 1 / many, etc).
    Not every rule fits this shape — rules that compare two tags against each
    other, or reason about cost/other fields, need their own logic."""
    tag: str
    category: str
    breakpoints: Tuple[Breakpoint, ...]


def tag_threshold_observation(cards: List[Card], rule: TagThresholdRule) -> Observation:
    matches = [c for c in cards if rule.tag in c.tags]
    count = len(matches)
    names = ", ".join(c.name for c in matches) or "none"

    chosen = rule.breakpoints[0]
    for bp in sorted(rule.breakpoints, key=lambda b: b.min_count):
        if count >= bp.min_count:
            chosen = bp

    return Observation(
        category=rule.category,
        finding=chosen.finding.format(count=count, names=names),
        detail=chosen.detail.format(count=count, names=names),
    )
