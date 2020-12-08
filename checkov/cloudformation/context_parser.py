import logging
import operator
from functools import reduce
import re
from checkov.common.comment.enum import COMMENT_REGEX


ENDLINE = '__endline__'

STARTLINE = '__startline__'

class ContextParser(object):
    """
    CloudFormation template context parser
    """
    def __init__(self, cf_file, cf_template, cf_template_lines):
        self.cf_file = cf_file
        self.cf_template = cf_template
        self.cf_template_lines = cf_template_lines

    def evaluate_default_refs(self):
        # Get Parameter Defaults - Locate Refs in Template
        refs = []
        refs.extend(self.search_deep_keys('Ref', self.cf_template, []))

        for ref in refs:
            refname = ref.pop()
            ref.pop()  # Get rid of the 'Ref' dict key

            if 'Parameters' in self.cf_template.keys() and refname in self.cf_template[
                'Parameters'].keys():
                # TODO refactor into evaluations
                if 'Default' in self.cf_template['Parameters'][refname].keys():
                    logging.debug(
                        "Replacing Ref {} in file {} with default parameter value: {}".format(refname, self.cf_file,
                                                                                              self.cf_template[
                                                                                                  'Parameters'][
                                                                                                  refname][
                                                                                                  'Default']))
                    self._set_in_dict(self.cf_template, ref,
                                      self.cf_template['Parameters'][refname]['Default'])

                    ## TODO - Add Variable Eval Message for Output
                    # Output in Checkov looks like this:
                    # Variable versioning (of /.) evaluated to value "True" in expression: enabled = ${var.versioning}

    @staticmethod
    def extract_cf_resource_id(cf_resource, cf_resource_name):
        if cf_resource_name == STARTLINE or cf_resource_name == ENDLINE:
            return
        if 'Type' not in cf_resource:
            # This is not a CloudFormation resource, skip
            return
        return f"{cf_resource['Type']}.{cf_resource_name}"

    def extract_cf_resource_code_lines(self, cf_resource):
        find_lines_result_list = list(self.find_lines(cf_resource, STARTLINE))
        if len(find_lines_result_list) >= 1:
            start_line = min(find_lines_result_list)
            end_line = max(list(self.find_lines(cf_resource, ENDLINE)))

            # start_line - 2: -1 to switch to 0-based indexing, and -1 to capture the resource name
            entity_code_lines = self.cf_template_lines[start_line - 2: end_line - 1]

            # if the file did not end in a new line, and this was the last resource in the file, then we
            # trimmed off the last line
            if (end_line - 1) < len(self.cf_template_lines) and not self.cf_template_lines[end_line - 1][1].endswith('\n'):
                entity_code_lines.append(self.cf_template_lines[end_line - 1])

            entity_code_lines = ContextParser.trim_lines(entity_code_lines)
            entity_lines_range = [entity_code_lines[0][0],entity_code_lines[-1][0]]
            return entity_lines_range, entity_code_lines
        return None, None

    @staticmethod
    def trim_lines(code_lines):
        # Removes leading and trailing lines that are only whitespace, returning a new value
        # The passed value should be a list of tuples of line numbers and line strings (entity_code_lines)
        start = 0
        end = len(code_lines)
        while start < end and not code_lines[start][1].strip():
            start += 1
        while end > start and not code_lines[end - 1][1].strip():
            end -= 1

        # if start == end, this will just be empty
        return code_lines[start:end]

    @staticmethod
    def find_lines(node, kv):
        if isinstance(node, list):
            for i in node:
                for x in ContextParser.find_lines(i, kv):
                    yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in ContextParser.find_lines(j, kv):
                    yield x

    @staticmethod
    def collect_skip_comments(entity_code_lines):
        skipped_checks = []
        for line in entity_code_lines:
            skip_search = re.search(COMMENT_REGEX, str(line))
            if skip_search:
                skipped_checks.append(
                    {
                        'id': skip_search.group(2),
                        'suppress_comment': skip_search.group(3)[1:] if skip_search.group(
                            3) else "No comment provided"
                    }
                )
        return skipped_checks

    @staticmethod
    def search_deep_keys(search_text, cfn_dict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(cfn_dict, dict):
            for key in cfn_dict:
                pathprop = path[:]
                pathprop.append(key)
                if key == search_text:
                    pathprop.append(cfn_dict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(cfn_dict[key], dict):
                    keys.extend(ContextParser.search_deep_keys(search_text, cfn_dict[key], pathprop))
                elif isinstance(cfn_dict[key], list):
                    for index, item in enumerate(cfn_dict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(ContextParser.search_deep_keys(search_text, item, pathproparr))
        elif isinstance(cfn_dict, list):
            for index, item in enumerate(cfn_dict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(ContextParser.search_deep_keys(search_text, item, pathprop))

        return keys

    def _set_in_dict(self, data_dict, map_list, value):
        self._get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value

    @staticmethod
    def _get_from_dict(data_dict, map_list):
        return reduce(operator.getitem, map_list, data_dict)
