import copy
def convert_terraform_conf_to_iam_policy(conf):
    """
        converts terraform parsed configuration to iam policy document
    """
    result = copy.deepcopy(conf)
    if "statement" in result.keys():
        result["Statement"] = result.pop("statement")
        for statement in result["Statement"]:
            if "actions" in statement:
                statement["Action"] = statement.pop("actions")[0]
            if "resources" in statement:
                statement["Resource"] = statement.pop("resources")[0]
            if "not_actions" in statement:
                statement["NotAction"] = statement.pop("not_actions")[0]
            if "not_resources" in statement:
                statement["NotResource"] = statement.pop("not_resources")[0]
            if "effect" in statement:
                statement["Effect"] = statement.pop("effect")[0]
            if "effect" not in statement and "Effect" not in statement:
                statement["Effect"] = "Allow"
    return result
