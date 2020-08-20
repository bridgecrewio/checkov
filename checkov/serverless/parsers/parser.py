import jmespath
import logging
import re

from yaml import YAMLError

from checkov.cloudformation.parser import cfn_yaml
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.parser.node import dict_node, str_node

logger = logging.getLogger(__name__)

IAM_ROLE_STATEMENTS_TOKEN = 'iamRoleStatements'
CFN_RESOURCES_TOKEN = 'resources'
PROVIDER_TOKEN = 'provider'
FUNCTIONS_TOKEN = 'functions'
ENVIRONMENT_TOKEN = 'environment'
SUPPORTED_PROVIDERS = ['aws']

SELF_VAR_PATTERN = re.compile(r"\${self:(?P<loc>[\w\-_.]+)(,(?P<default>[\w\-_.]+))?}")

def parse(filename):
    template = None
    template_lines = None
    try:
        (template, template_lines) = cfn_yaml.load(filename)
        if not template or not is_checked_sls_template(template):
            return
    except IOError as e:
        if e.errno == 2:
            logger.error('Template file not found: %s', filename)
            return
        elif e.errno == 21:
            logger.error('Template references a directory, not a file: %s',
                         filename)
            return
        elif e.errno == 13:
            logger.error('Permission denied when accessing template file: %s',
                         filename)
            return
    except UnicodeDecodeError as err:
        logger.error('Cannot read file contents: %s', filename)
        return
    except YAMLError as err:
        return

    process_variables(template)

    return template, template_lines


def is_checked_sls_template(template):
    if template.__contains__('provider'):
        # Case provider is a dictionary
        if isinstance(template['provider'], dict_node):
            if template['provider'].get('name').lower() not in SUPPORTED_PROVIDERS:
                return False
        # Case provider is direct provider name
        if isinstance(template['provider'], str_node):
            if template['provider'] not in SUPPORTED_PROVIDERS:
                return False
        if template_contains_cfn_resources(template) or template_contains_key(template, FUNCTIONS_TOKEN):
            return True
    return False


def template_contains_cfn_resources(template):
    if template.__contains__(CFN_RESOURCES_TOKEN):
        if template[CFN_RESOURCES_TOKEN].get('Resources'):
            return True
    return False


def template_contains_key(template, key):
    if ContextParser.search_deep_keys(key, template, []):
        return True
    return False


def process_variables(template):
    """
Modifies the template data in-place to resolve variables.
    """
    process_self_variables(template)


def process_self_variables(template, processing_subdict=None):
    """
This processes "self" variables (e.g., "${self:custom.var}) in values and replaces such variables with
the real values.
    """
    if processing_subdict is None:
        processing_subdict = template

    # Generic loop for handling a source of key/value tuples (e.g., enumerate() or <dict>.items())
    def process_items(key_value_iterator, data_map):
        for key, value in key_value_iterator():
            if isinstance(value, str):
                altered_value = value
                for match in SELF_VAR_PATTERN.finditer(value):
                    location = match.group("loc")
                    default = match.group("default")
                    if default is None:
                        default = ""
                    else:
                        default = default.strip()

                    try:
                        # NOTE: String must be quoted to avoid issues with dashes and other reserved
                        #       characters. If we just wrap the whole thing, dot separators won't work so:
                        #       split and join with individually wrapped tokens.
                        #         Original:  foo.bar-baz
                        #         Wrapped:   "foo"."bar-baz"
                        location = ".".join([f'"{token}"' for token in location.split(".")])
                        source_value = jmespath.search(location, template)
                    except KeyError:
                        source_value = default
                    except Exception as e:
                        print(e)
                        continue
                    if source_value is None:
                        source_value = default

                    altered_value = altered_value.replace(match[0], source_value)
                data_map[key] = altered_value
            elif isinstance(value, dict):
                process_self_variables(template, value)
            elif isinstance(value, list):
                process_items(lambda: enumerate(value), value)

    process_items(processing_subdict.items, processing_subdict)
