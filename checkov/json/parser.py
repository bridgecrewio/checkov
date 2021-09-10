from checkov.terraform.context_parsers.tf_plan.tf_plan_json import load


def parse(file):
    return load(file)
