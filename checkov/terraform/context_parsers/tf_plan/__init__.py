import json
import logging
from checkov.terraform.context_parsers.tf_plan.node import dict_node

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from checkov.terraform.context_parsers.tf_plan import tf_plan_json

LOGGER = logging.getLogger(__name__)


def parse(filename):
    """
        Decode filename into an object
    """
    template = None
    template_lines = None
    try:
        (template, template_lines) = tf_plan_json.load(filename)
    except tf_plan_json.JSONDecodeError:
        pass
    except json.decoder.JSONDecodeError:
        # Most parsing errors will get caught by the exception above. But, if the file is totally empty, and perhaps in
        # other specific cases, the json library will not even begin parsing with our custom logic that throws the
        # exception above, and will fail with this exception instead.
        pass

    if template is not None and isinstance(template, dict_node) and 'terraform_version' in template and 'planned_values' in template:
        return template, template_lines
    return None, None
