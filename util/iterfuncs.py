import re
from itertools import chain

from typing import List, Any


def is_match_within_patterns(target: str, patterns: List[str], ignore_case=False):
    for pattern in patterns:
        p = pattern.lower() if ignore_case else pattern
        t = target.lower() if ignore_case else target

        if re.compile(p).match(t):
            return True

    return False


def flatten(l: List[List[Any]]) -> List[Any]:
    return list(chain(*l))
