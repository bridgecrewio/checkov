from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

PROVIDERS = ("aws", "gcp", "azure")

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def camel_to_snake(name: str) -> str:
    return _CAMEL_BOUNDARY.sub("_", name).lower()


@lru_cache(maxsize=None)
def _load(provider: str) -> dict[str, Any]:
    path = Path(__file__).parent / f"{provider}.json"
    if not path.exists():
        return {"resources": {}, "aliases": {}}
    return json.loads(path.read_text(encoding="utf-8"))  # type:ignore[no-any-return]


def get_resource_mapping(token: str) -> dict[str, Any] | None:
    """Returns the Terraform mapping of a Pulumi resource type token, ex. 'aws:s3/bucket:Bucket'"""

    provider = token.split(":", 1)[0]
    if provider not in PROVIDERS:
        return None
    mapping = _load(provider)
    token = mapping["aliases"].get(token, token)
    return mapping["resources"].get(token)  # type:ignore[no-any-return]
