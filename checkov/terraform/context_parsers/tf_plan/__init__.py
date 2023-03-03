import logging
from typing import Dict

from checkov.cloudformation.parser.cfn_yaml import ContentType
from checkov.cloudformation.parser import cfn_yaml

LOGGER = logging.getLogger(__name__)


def parse(filename, out_parsing_errors: Dict[str, str]):
    """
        Decode filename into an object
    """
    logging.debug(f"[tf_plan] - Parsing file {filename}")

    try:
        template, template_lines = cfn_yaml.load(filename, ContentType.TFPLAN)
    except Exception as e:
        logging.debug(f"[tf_plan] - Failed to parse file {filename}", exc_info=True)
        out_parsing_errors[filename] = str(e)
        return None, None

    if (
        template is not None
        and isinstance(template, dict)
        and 'terraform_version' in template
        and 'planned_values' in template
    ):
        logging.debug(f"[tf_plan] - Successfully parsed file {filename}")

        return template, template_lines

    logging.debug(f"[tf_plan] - Missing required fields in file {filename}")
    return None, None
