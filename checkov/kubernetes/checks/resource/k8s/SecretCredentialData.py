from __future__ import annotations

import base64
import binascii
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

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

# Secret keys that conventionally hold public material (CA bundles and the
# public half of a TLS pair). Private keys under any key still fail.
_PUBLIC_MATERIAL_KEYS = {
    "ca.crt",
    "ca-bundle.crt",
    "tls.crt",
    "cert",
    "certificate",
    "public-key",
    "public_key",
}

# Well-known token formats, matched against a URL's username component. A token
# used as the username (e.g. "https://ghp_...@github.com/...") is an embedded
# credential even when the URL has no password component.
_TOKEN_USERNAME_PREFIXES = (
    "ghp_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "github_pat_",
    "glpat-",
    "xoxb-",
    "xoxa-",
    "xoxp-",
    "xoxr-",
    "xoxs-",
)

# Query parameters that carry credentials when given a real value. Deliberately
# narrow: ordinary configuration parameters (timeouts, database indexes, …)
# must not turn a credential-free connection string into a finding.
_CREDENTIAL_QUERY_PARAMS = {
    "token",
    "access_token",
    "sig",
    "signature",
    "password",
    "passwd",
    "api_key",
    "apikey",
    "key",
}


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


def _is_encrypted_value(value: str) -> bool:
    """Values encrypted by an external secrets tool are ciphertext, not literal
    credentials: SOPS values start with ``ENC[`` and Ansible Vault values with
    ``$ANSIBLE_VAULT;``. Flagging them would punish the recommended pattern for
    storing Secrets in Git."""
    stripped = value.strip()
    return stripped.startswith("ENC[") or stripped.startswith("$ANSIBLE_VAULT;")


def _is_public_material(key: str, value: str) -> bool:
    """Public certificate material is not a credential. A PEM private key is
    always credential material, whatever key it sits under."""
    if "PRIVATE KEY" in value:
        return False
    if "BEGIN CERTIFICATE" in value:
        return True
    return key in _PUBLIC_MATERIAL_KEYS


def _looks_like_token(username: str) -> bool:
    if username.startswith(_TOKEN_USERNAME_PREFIXES):
        return True
    # A long username made of token-like characters (digits/underscores mixed
    # in) is treated as a token. Plain service names — the normal userinfo in
    # credential-free connection strings — are short alphabetic or hyphenated
    # words, so this stays conservative: length alone is not enough.
    if len(username) >= 20 and any(ch.isdigit() or ch == "_" for ch in username):
        return True
    return False


def _is_credential_free_url(value: str) -> bool:
    """Connection strings without embedded credentials are configuration, not
    credential material (e.g. "redis://cache:6379/5"). A URL carries a
    credential — and is not exempted — when it has a password in its userinfo,
    a token as its username, or a credential query parameter with a real
    value."""
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    if not (parsed.scheme and parsed.netloc):
        return False
    if parsed.password:
        return False
    if parsed.username and _looks_like_token(parsed.username):
        return False
    if parsed.query:
        for param, values in parse_qs(parsed.query).items():
            if param.lower() in _CREDENTIAL_QUERY_PARAMS and any(not _is_placeholder(v) for v in values):
                return False
    return True


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
        material and pass. So do values encrypted with SOPS or Ansible Vault,
        Secrets carrying SOPS metadata, and public certificate material. A
        Secret carrying an actual password, token, or key fails: anyone with
        read access to the manifest has the credential, and rendered charts
        have repeatedly shipped real generated passwords and bundled default
        private keys this way.
        """
        # A top-level ``sops`` key is the metadata SOPS writes into every file
        # it encrypts; the Secret's values are ciphertext managed by SOPS.
        if "sops" in conf:
            return CheckResult.PASSED
        for field in ("data", "stringData"):
            values = conf.get(field)
            if not isinstance(values, dict):
                continue
            for key, raw_value in values.items():
                value = _decode_data_value(raw_value) if field == "data" else raw_value
                if not isinstance(value, str):
                    continue
                if _is_placeholder(value) or _is_encrypted_value(value):
                    continue
                if _is_public_material(key, value):
                    continue
                if _is_credential_free_url(value):
                    continue
                return CheckResult.FAILED
        return CheckResult.PASSED


check = SecretCredentialData()
