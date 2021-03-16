import copy
def convert_cloudformation_conf_to_iam_policy(conf):
    """
        converts terraform parsed configuration to iam policy document
    """
    result = copy.deepcopy(conf)
    if "Statement" in result.keys():
        result["Statement"] = result.pop("Statement")
        for statement in result["Statement"]:
            if "Action" in statement:
                statement["Action"] = str(statement.pop("Action")[0])
            if "Resource" in statement:
                statement["Resource"] = str(statement.pop("Resource")[0])
            if "NotAction" in statement:
                statement["NotAction"] = str(statement.pop("NotAction")[0])
            if "NotResource" in statement:
                statement["NotResource"] = str(statement.pop("NotResource")[0])
            if "Effect" in statement:
                statement["Effect"] = str(statement.pop("Effect"))
            if "Effect" not in statement:
                statement["Effect"] = "Allow"
            statement = dict(statement)
    return result
