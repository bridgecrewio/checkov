import re
from typing import Any

from checkov.common.util.parser_utils import find_var_blocks

TF_OPERATOR_PREFIXES = ("lookup(", "list(", "file(")

CFN_VARIABLE_DEPENDANT_REGEX = re.compile(r"(?:Ref)\.\S+")
TF_BLOCK_REFS = ("var.", "local.", "module.", "data.")
TF_PROVIDER_PREFIXES = (
    "aws_",
    "azurerm_",
    "azuread_",
    "digitalocean_",
    "google_",
    "github_",
    "kubernetes_",
    "linode_",
    "oci_",
    "openstack_",
    "yandex_",
)


def is_terraform_variable_dependent(value: Any) -> bool:
    if not isinstance(value, str):
        return False

    if value.startswith(TF_BLOCK_REFS):
        return True

    if value.startswith(TF_PROVIDER_PREFIXES):
        return True

    if value.startswith(TF_OPERATOR_PREFIXES):
        return True

    if "${" not in value:
        return False

    if find_var_blocks(value):
        return True
    return False


def is_cloudformation_variable_dependent(value: Any) -> bool:
    if isinstance(value, str) and re.match(CFN_VARIABLE_DEPENDANT_REGEX, value):
        return True
    return False
