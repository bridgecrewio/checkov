import unittest

from checkov.terraform.util.docs_generator import get_checks


class TestDocGenerator(unittest.TestCase):

    def test_doc_generator_initiation(self):
        checks = get_checks()
        self.assertGreater(len(checks), 0)


if __name__ == '__main__':
    unittest.main()
