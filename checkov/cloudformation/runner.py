import logging
import os
import json

from checkov.cloudformation.checks.resource.registry import resource_registry
from checkov.terraform.output.record import Record
from checkov.terraform.output.report import Report
from checkov.cloudformation.parser import parse

from functools import reduce
import operator

class Runner:

    def run(self, root_folder, external_checks_dir=None, files=None):
        report = Report()
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)

        if files:
            for file in files:
                files_list.append(file)
        if root_folder:
            for file in os.listdir(root_folder):
                if file.endswith(".yaml") or file.endswith(".json") or file.endswith(".template"):
                    files_list.append(os.path.join(root_folder, file))

        for file in files_list:
            (definitions[file], definitions_raw[file]) = parse(file)

        for definition in definitions.keys():
            logging.debug("Template Dump for {}: {}".format(definition, json.dumps(definitions[definition], indent = 2)))

            # Get Parameter Defaults - Locate Refs in Template
            refs = []
            refs.extend(self._search_deep_keys('Ref', definitions[definition], []))

            for ref in refs:
                refname = ref.pop()
                ref.pop()   # Get rid of the 'Ref' dict key

                if 'Parameters' in definitions[definition].keys() and refname in definitions[definition]['Parameters'].keys():
                    if 'Default' in definitions[definition]['Parameters'][refname].keys():
                        logging.debug("Replacing Ref {} in file {} with default parameter value: {}".format(refname, definition, definitions[definition]['Parameters'][refname]['Default']))
                        setInDict(definitions[definition], ref, definitions[definition]['Parameters'][refname]['Default'])

                        ## TODO - Add Variable Eval Message for Output
                        # Output in Checkov looks like this:
                        # Variable versioning (of /.) evaluated to value "True" in expression: enabled = ${var.versioning}

            for resource in definitions[definition]['Resources'].keys():
                if resource == '__startline__' or resource == '__endline__':
                    continue

                ## TODO - Evaluate skipped_checks
                skipped_checks = {}

                results = resource_registry.scan(definitions[definition]['Resources'][resource], resource, definition, skipped_checks)

                start_line = min(list(findlines(definitions[definition]['Resources'][resource], '__startline__')))
                end_line = max(list(findlines(definitions[definition]['Resources'][resource], '__endline__')))

                entity_lines_range = [start_line, end_line - 1]

                entity_code_lines = definitions_raw[definition][start_line - 1: end_line - 1]



                # TODO - Variable Eval Message!
                variable_evaluations = {}

                for check, check_result in results.items():
                    ### TODO - Need to get entity_code_lines and entity_lines_range
                    record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                    code_block=entity_code_lines, file_path=file,
                                    file_line_range=entity_lines_range,
                                    resource=resource, evaluations=variable_evaluations,
                                    check_class=check.__class__.__module__)
                    report.add_record(record=record)
        return report

    def _search_deep_keys(self, searchText, cfndict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(cfndict, dict):
            for key in cfndict:
                pathprop = path[:]
                pathprop.append(key)
                if key == searchText:
                    pathprop.append(cfndict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(cfndict[key], dict):
                    keys.extend(self._search_deep_keys(searchText, cfndict[key], pathprop))
                elif isinstance(cfndict[key], list):
                    for index, item in enumerate(cfndict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(self._search_deep_keys(searchText, item, pathproparr))
        elif isinstance(cfndict, list):
            for index, item in enumerate(cfndict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(self._search_deep_keys(searchText, item, pathprop))

        return keys

def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)

def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value


def findlines(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findlines(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findlines(j, kv):
                yield x
