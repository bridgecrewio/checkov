import logging
from checkov.arm.parser.node import dict_node

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
from yaml.parser import ParserError, ScannerError
from yaml import YAMLError
from checkov.arm.parser import cfn_yaml, cfn_json

LOGGER = logging.getLogger(__name__)


def parse(filename):
    """
        Decode filename into an object
    """
    template = None
    template_lines = None
    try:
        (template, template_lines) = cfn_yaml.load(filename)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error('Template file not found: %s', filename)
        elif e.errno == 21:
            LOGGER.error('Template references a directory, not a file: %s',
                         filename)
        elif e.errno == 13:
            LOGGER.error('Permission denied when accessing template file: %s',
                         filename)
    except UnicodeDecodeError as err:
        LOGGER.error('Cannot read file contents: %s', filename)
    except cfn_yaml.CfnParseError as err:
        pass
    except ScannerError as err:
        if err.problem in [
            'found character \'\\t\' that cannot start any token',
            'found unknown escape character']:
            try:
                (template, template_lines) = cfn_json.load(filename)
            except cfn_json.JSONDecodeError:
                pass
            except JSONDecodeError:
                pass
            except Exception as json_err:  # pylint: disable=W0703
                LOGGER.error(
                    'Template %s is malformed: %s', filename, err.problem)
                LOGGER.error('Tried to parse %s as JSON but got error: %s',
                             filename, str(json_err))
    except YAMLError as err:
        pass

    if template is not None and isinstance(template, dict_node) and '$schema' in template and 'resources' in template:
        return template, template_lines
    return None, None
