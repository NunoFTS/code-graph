from __future__ import annotations

import json
from typing import Any, Mapping


class _SafeFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return ""


def safe_format(template: str, values: Mapping[str, Any]) -> str:
    normalized: dict[str, Any] = {}
    for key, value in values.items():
        if isinstance(value, (dict, list, tuple)):
            normalized[key] = json.dumps(value, ensure_ascii=False, default=str)
        else:
            normalized[key] = value
    return template.format_map(_SafeFormatDict(normalized))
