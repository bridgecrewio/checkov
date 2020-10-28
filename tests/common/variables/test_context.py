import unittest

from checkov.common.variables.context import EntityContext


class ContextTest(unittest.TestCase):
    def test_the_thing(self):
        context = EntityContext(1, 10, [(1, "# TODO: write some code here")], ["CKV_AWS_1234"])
        assert context["start_line"] == 1
        assert context["end_line"] == 10
        assert context["code_lines"] == [(1, "# TODO: write some code here")]
        assert context["skipped_checks"] == ["CKV_AWS_1234"]
