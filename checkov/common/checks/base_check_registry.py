import importlib
import logging
import os
import sys
from abc import abstractmethod


class BaseCheckRegistry(object):
    checks = {}
    check_id_whitelist = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.checks = {}
        self.check_id_whitelist = None

    def register(self, check):
        for entity in check.supported_entities:
            if entity not in self.checks.keys():
                self.checks[entity] = []
            self.checks[entity].append(check)

    def get_check_by_id(self, check_id):
        for resource_type in self.checks.keys():
            resource_type_checks = self.checks[resource_type]
            for check in resource_type_checks:
                if check_id == check.id:
                    return check
        return None

    def get_checks(self, entity):
        if entity in self.checks.keys():
            return self.checks[entity]
        return []

    def set_checks_whitelist(self,runner_filter):
        if runner_filter.checks:
            self.check_id_whitelist = runner_filter.checks

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def scan(self, scanned_file, entity, skipped_checks, runner_filter=None):
        (entity_type, entity_name, entity_configuration) = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        check_id_whitelist = runner_filter.checks
        check_id_blacklist = runner_filter.skip_checks
        for check in checks:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]
            if check_id_whitelist:
                if check.id in check_id_whitelist:
                    result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file, skip_info)
                    results[check] = result
            elif check_id_blacklist:
                if check.id not in check_id_blacklist:
                    result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file, skip_info)
                    results[check] = result
            else:
                result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file, skip_info)
                results[check] = result
        return results

    def run_check(self, check, entity_configuration, entity_name, entity_type, scanned_file, skip_info):
        self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))
        result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                           entity_name=entity_name, entity_type=entity_type, skip_info=skip_info)
        return result

    @staticmethod
    def _directory_has_init_py(directory):
        """ Check if a given directory contains a file named __init__.py.

        __init__.py is needed to ensure the directory is a Python module, thus
        can be imported.
        """
        if os.path.exists("{}/__init__.py".format(directory)):
            return True
        return False

    @staticmethod
    def _file_can_be_imported(entry):
        """ Verify if a directory entry is a non-magic Python file."""
        if entry.is_file() and not entry.name.startswith('__') and entry.name.endswith('.py'):
            return True
        return False

    def load_external_checks(self, directory):
        """ Browse a directory looking for .py files to import.

        Log an error when the directory does not contains an __init__.py or
        when a .py file has syntax error
        """
        directory = os.path.expanduser(directory)
        self.logger.debug("Loading external checks from {}".format(directory))
        sys.path.insert(1, directory)

        with os.scandir(directory) as directory_content:
            if not self._directory_has_init_py(directory):
                self.logger.info("No __init__.py found in {}. Cannot load any check here.".format(directory))
            else:
                for entry in directory_content:
                    if self._file_can_be_imported(entry):
                        check_name = entry.name.replace('.py', '')
                        try:
                            self.logger.debug("Importing external check '{}'".format(check_name))
                            importlib.import_module(check_name)
                        except SyntaxError as e:
                            self.logger.error(
                                "Cannot load external check '{check_name}' from {check_full_path} : {error_message} ("
                                "{error_line}:{error_column}) "
                                    .format(
                                    check_name=check_name,
                                    check_full_path=e.args[1][0],
                                    error_message=e.args[0],
                                    error_line=e.args[1][1],
                                    error_column=e.args[1][2]
                                )
                            )
