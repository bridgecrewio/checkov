import fnmatch
import importlib
import logging
import os
import sys
from abc import abstractmethod
from itertools import chain
from typing import Generator, Tuple

from checkov.common.checks.base_check import BaseCheck

from collections import defaultdict

from checkov.runner_filter import RunnerFilter


class BaseCheckRegistry(object):
    # NOTE: Needs to be static to because external check loading may be triggered by a registry to which
    #       checks aren't registered. (This happens with Serverless, for example.)
    __loading_external_checks = False

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # IMPLEMENTATION NOTE: Checks is used to directly access checks based on an specific entity
        self.checks = defaultdict(list)
        # IMPLEMENTATION NOTE: When using a wildcard, every pattern needs to be checked. To reduce the
        #                      number of checks checks with the same pattern are grouped, which is the
        #                      reason to use a dict for this too.
        self.wildcard_checks = defaultdict(list)
        self.check_id_allowlist = None

    def register(self, check):
        # IMPLEMENTATION NOTE: Checks are registered when the script is loaded
        #                      (see BaseResourceCheck.__init__() for the various frameworks). The only
        #                      difficultly with this process is that external checks need to be specially
        #                      identified for filter handling. That's why you'll see stateful setting of
        #                      RunnerFilters during load_external_checks.
        #                      Built-in checks are registered immediately at script start, before
        #                      external checks.
        if BaseCheckRegistry.__loading_external_checks:
            RunnerFilter.notify_external_check(check.id)

        for entity in check.supported_entities:
            checks = self.wildcard_checks if self._is_wildcard(entity) else self.checks
            checks[entity].append(check)

    @staticmethod
    def _is_wildcard(entity):
        return ('*' in entity
                or '?' in entity
                or ('[' in entity and ']' in entity))

    def get_check_by_id(self, check_id):
        return next(
            filter(
                lambda c: c.id == check_id,
                chain(*self.checks.values(), *self.wildcard_checks.values())
            ), None)

    def all_checks(self) -> Generator[Tuple[str, BaseCheck], None, None]:
        for entity, checks in self.checks.items():
            for check in checks:
                yield entity, check
        for entity, checks in self.wildcard_checks.items():
            for check in checks:
                yield entity, check

    @property
    def contains_wildcard(self) -> bool:
        return bool(self.wildcard_checks)

    def get_checks(self, entity):
        if not self.wildcard_checks:
            # Optimisation: When no wildcards are used, we can use the list in self.checks
            return self.checks.get(entity) or []
        else:
            res = self.checks[entity].copy() if entity in self.checks.keys() else []
            # check wildcards
            for pattern, checks in self.wildcard_checks.items():
                if fnmatch.fnmatchcase(entity, pattern):
                    res += checks
            return res

    def set_checks_allowlist(self, runner_filter):
        if runner_filter.checks:
            self.check_id_allowlist = runner_filter.checks

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def scan(self, scanned_file, entity, skipped_checks, runner_filter):
        (entity_type, entity_name, entity_configuration) = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]

            if runner_filter.should_run_check(check.id):
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

    def load_external_checks(self, directory, runner_filter):
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

                        # Filter is set while loading external checks so the filter can be informed
                        # of the checks, which need to be handled specially.
                        try:
                            BaseCheckRegistry.__loading_external_checks = True
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
                        finally:
                            BaseCheckRegistry.__loading_external_checks = False
