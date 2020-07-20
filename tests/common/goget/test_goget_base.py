import os
import unittest

from tests.common.goget.local_getter import LocalGetter


class TestBaseGetter(unittest.TestCase):

    def test_directory_creation(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        getter = LocalGetter(current_dir)
        result_dir = getter.get()
        self.assertTrue(current_dir in result_dir)
        print(result_dir)



if __name__ == '__main__':
    unittest.main()
