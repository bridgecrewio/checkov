from typing import Dict

import dpath

from checkov.common.checks.base_check import BaseDefinitionAccess


class TerraformDefinitionAccess(BaseDefinitionAccess):
    def __init__(self, doc: Dict) -> None:
        self.__file_being_processed = None
        super().__init__(doc)

    def find_resource_by_name(self, resource_type: str, resource_name: str) -> Dict:
        """
        Searches definitions for a resource of a given type and name in the context of the current check and,
        if found, returns its configuration data. If not found, an empty dict will be returned.
        """

        # IMPLEMENTATION NOTE: This would be super easy to implement, except for the problem that the full
        #                      full definition might contain definitions that
        if self.__file_being_processed is None:
            raise AssertionError("Logic error: _set_file_being_checked has not been called. Please report "
                                 "this as a checkov bug.")

        file_def = self.full_definition().get(self.__file_being_processed)
        if file_def is None:
            return {}

        try:
            return dpath.get(file_def,
                             f"resource/*/{resource_type}/{resource_name}")
        except KeyError:
            return {}

    def _set_file_being_checked(self, full_file_path):
        """
        Internal function for the runner to indicate which file is being
        :param full_file_path:
        """
        self.__file_being_processed = full_file_path
