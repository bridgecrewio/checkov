import os
import unittest

from tests.common.goget.local_getter import LocalGetter


class TestBaseGetter(unittest.TestCase):

    def test_directory_creation(self):
        current_dir = os.getcwd()
        getter = LocalGetter(current_dir)
        result_dir = getter.get()
        print(current_dir)
        print(result_dir)
        self.assertIn(current_dir, result_dir)

        # Cleanup
        os.rmdir(getter.temp_dir)



if __name__ == '__main__':
    unittest.main()
