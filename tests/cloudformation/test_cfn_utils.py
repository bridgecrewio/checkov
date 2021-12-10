import os
import unittest

from checkov.cloudformation import cfn_utils

class TestCFNUtils(unittest.TestCase):
    def test_get_files_definitions_where_none_cf(self):
        # Check for return of {}, {} when there is not a single valid CF Template provided.
        # This will be used to stop the CF Runner up the stack.

        # Simplest case: no files means no valid templates.
        # Templates are found based on the file containing CF 'Resources'.
        definitions, definitions_raw = cfn_utils.get_files_definitions([], {})

        # Empty Dict will resolve to false.
        self.assertFalse(definitions)
        self.assertFalse(definitions_raw)


if __name__ == '__main__':
    unittest.main()
