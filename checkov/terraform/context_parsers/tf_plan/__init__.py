import logging
from checkov.common.parsers.json import parse as json_parse
from checkov.common.parsers.node import DictNode

LOGGER = logging.getLogger(__name__)


def parse(filename):
    """
        Decode filename into an object
    """
    (template, template_lines) = json_parse(filename)

    if (
        template is not None
        and isinstance(template, DictNode)
        and 'terraform_version' in template
        and 'planned_values' in template
    ):
        return template, template_lines
    return None, None
