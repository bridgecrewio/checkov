import unittest
from typing import Any

import hcl2


# This group of tests is used to confirm assumptions about how the hcl2 library parses into json.
# We want to make sure important assumptions are caught if behavior changes.
from tests.terraform.parser.hcl_load_assumptions_base import HCLLoadAssumptionsBase


class TestHCL2LoadAssumptions(HCLLoadAssumptionsBase, unittest.TestCase):

    def parse(self, terraform: str) -> Any:
        return hcl2.loads(terraform)

    # NOTE: HCL2-specific cases are here, while more general cases
    #       are in the parent class.

    def test_hcl1_map_with_colons(self):
        #
        with self.assertRaises(Exception):
            super().test_hcl1_map_with_colons()
