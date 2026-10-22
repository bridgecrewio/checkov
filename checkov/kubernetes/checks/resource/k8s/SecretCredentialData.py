from __future__ import annotations

import base64
import binascii
import re
from typing import Any
from urllib.parse import urlparse

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check

# Values that are self-evidently not credentials: documentation placeholders and
# fill-in markers found in example manifests and chart templates.
_PLACEHOLDER_VALUES = {
    "changeme",
    "change-me",
    "change_me",
    "placeholder",
    "replace-me",
    "replace_me",
    "todo",
}

# Strings made only of filler characters, e.g. "xxxxxx", "******", "........".
_FILLER_PATTERN = re.compile(r"^[xX*.\-_ ]+$")


def _is_placeholder(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return True
    if stripped.lower() in _PLACEHOLDER_VALUES:
        return True
    # Templating expressions (Helm, envsubst, angle-bracket fill-ins) are
    # references to values supplied at deploy time, not literal credentials.
    if "{{" in stripped or "${" in stripped:
        return True
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    if _FILLER_PATTERN.match(stripped):
        return True
    return False


def _is_credential_free_url(value: str) -> bool:
    """Connection strings without embedded credentials are configuration, not
    credential material (e.g. "redis://cache:6379/5"). A URL carrying a
    password in its userinfo is a credential and is not exempted."""
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    return bool(parsed.scheme and parsed.netloc and not parsed.password)


def _decode_data_value(value: Any) -> str:
    """Return the plaintext form of a Secret ``data`` value when possible."""
    if not isinstance(value, str):
        return ""
    try:
        return base64.b64decode(value, validate=True).decode("utf-8", errors="replace")
    except (binascii.Error, ValueError):
        return value


class SecretCredentialData(BaseK8Check):
    def __init__(self) -> None:
        name = "Secret objects should not contain literal credential data"
        id = "CKV_K8S_161"
        supported_kind = ("Secret",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
        A Secret stored in a manifest is only as safe as the repository holding
        the manifest. Empty Secrets (populated at runtime by an operator or by
        the API server, e.g. service-account-token Secrets) and Secrets whose
        values are placeholders or template references carry no credential
        material and pass. A Secret carrying an actual password, token, or key
        fails: anyone with read access to the manifest has the credential, and
        rendered charts have repeatedly shipped live generated passwords and
        bundled default private keys this way.
        """
        for field in ("data", "stringData"):
            values = conf.get(field)
            if not isinstance(values, dict):
                continue
            for raw_value in values.values():
                value = _decode_data_value(raw_value) if field == "data" else raw_value
                if isinstance(value, str) and not _is_placeholder(value) and not _is_credential_free_url(value):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = SecretCredentialData()
