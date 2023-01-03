from __future__ import annotations

import copy
from typing import Any


def convert_cloudformation_conf_to_iam_policy(conf: dict[str, Any]) -> dict[str, Any]:
    """
        converts terraform parsed configuration to iam policy document
    """
    result = copy.deepcopy(conf)
    if "Statement" in result.keys():
        result["Statement"] = result.pop("Statement")
        for statement in map(dict, result["Statement"]):
            if "Action" in statement:
                statement["Action"] = str(statement.pop("Action")[0])
            if "Resource" in statement:
                resources = statement.pop("Resource")
                if isinstance(resources, list):
                    statement["Resource"] = str(resources[0])
                else:
                    statement["Resource"] = str(resources)
            if "NotAction" in statement:
                statement["NotAction"] = str(statement.pop("NotAction")[0])
            if "NotResource" in statement:
                not_resources = statement.pop("NotResource")
                if isinstance(not_resources, list):
                    statement["NotResource"] = str(not_resources[0])
                else:
                    statement["NotResource"] = str(not_resources)
            if "Effect" in statement:
                statement["Effect"] = str(statement.pop("Effect"))
            if "Effect" not in statement:
                statement["Effect"] = "Allow"
    return result
