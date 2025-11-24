import re
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


# 🔍 Regex patterns to detect secrets, credentials, and private keys
SECRET_PATTERNS = [
    r"(?i)(key|secret|token|password|pwd|auth|credential|api[_-]?key)\s*=",   # generic secrets
    r"(?i)AKIA[0-9A-Z]{16}",                         # AWS access key
    r"(?i)ASIA[0-9A-Z]{16}",                         # AWS temporary key
    r"(?i)ghp_[0-9A-Za-z]{36}",                      # GitHub personal access token
    r"(?i)eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}",  # JWT
    r'(?i)["\']?\s*-{3,}BEGIN(?: RSA)? PRIVATE KEY-{3,}',  # Private key headers
    r"(?i)xox[baprs]-[0-9A-Za-z-]{10,48}",           # Slack/Discord tokens
]


class SecretsInEnvArg(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure no secrets or private keys are stored in ENV or ARG instructions"
        check_id = "CKV_DOCKER_1005"
        categories = [CheckCategories.SECRETS]
        supported_instructions = ["ENV", "ARG"]
        super().__init__(name=name, id=check_id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf):
        """
        conf: list of dicts representing Dockerfile instructions, e.g.:
        [
            {"instruction": "ENV", "startline": 3, "endline": 3, "value": "API_KEY=abcd1234"},
            {"instruction": "ARG", "startline": 4, "endline": 4, "value": "ACCESS_TOKEN=xyz789"}
        ]
        """
        if not conf or not isinstance(conf, list):
            return CheckResult.PASSED, None

        for item in conf:
            if not isinstance(item, dict):
                continue

            value = str(item.get("value", ""))
            print(f"DEBUG: Checking value -> {value}")

            for pattern in SECRET_PATTERNS:
                if re.search(pattern, value):
                    print(f"DEBUG: Matched pattern -> {pattern} in {value}")
                    return CheckResult.FAILED, {
                        "startline": item.get("startline", 0),
                        "endline": item.get("endline", 0),
                        "instruction": item.get("instruction", ""),
                        "details": f"Potential secret pattern '{pattern}' found in {item.get('instruction', '')}: {value.strip()}"
                    }

        return CheckResult.PASSED, None


check = SecretsInEnvArg()

