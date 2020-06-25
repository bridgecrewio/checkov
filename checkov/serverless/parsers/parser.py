import logging
from yaml import YAMLError

from checkov.cloudformation.parser import cfn_yaml
from checkov.cloudformation.context_parser import ContextParser

logger = logging.getLogger(__name__)

IAM_ROLE_STATEMENTS_TOKEN = 'iamRoleStatements'
CFN_RESOURCES_TOKEN = 'resources'
PROVIDER_TOKEN = 'provider'
FUNCTIONS_TOKEN = 'functions'
ENVIRONMENT_TOKEN = 'environment'
SUPPORTED_PROVIDERS = ['aws']


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

    return template, template_lines


def is_checked_sls_template(template):
    if template.__contains__('provider'):
        if template['provider'].get('name').lower() in SUPPORTED_PROVIDERS or \
                template['provider'] in SUPPORTED_PROVIDERS:
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
