from typing import Dict, Any, List

from util.iterfuncs import is_match_within_patterns


def filter_keys(d: Dict[str, Any], key_patterns: List[str] | None, ignore_case=True) -> Dict[str, Any]:
    if key_patterns and len(key_patterns) > 0:
        return {k: v for k, v in d.items() if is_match_within_patterns(k, key_patterns, ignore_case)}
    else:
        return d
