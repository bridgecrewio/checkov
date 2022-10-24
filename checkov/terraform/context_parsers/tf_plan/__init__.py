import logging
from typing import Dict

from checkov.cloudformation.parser.cfn_yaml import ContentType
from checkov.cloudformation.parser import cfn_yaml
from checkov.common.parsers.node import DictNode

LOGGER = logging.getLogger(__name__)


def parse(filename, out_parsing_errors: Dict[str, str]):
    """
        Decode filename into an object
    """
    try:
        (template, template_lines) = cfn_yaml.load(filename, ContentType.TFPLAN)
    except Exception as e:
        out_parsing_errors[filename] = str(e)
        return None, None

    if (
        template is not None
        and isinstance(template, DictNode)
        and 'terraform_version' in template
        and 'planned_values' in template
    ):
        return template, template_lines
    return None, None
