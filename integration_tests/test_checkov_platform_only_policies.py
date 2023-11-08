import platform
import sys
import unittest
import re
from pathlib import Path

from checkov.common.models.consts import ckv_check_id_pattern

current_dir = Path(__file__).parent


class TestCheckovPlatformOnlyPolicies(unittest.TestCase):

    def test_no_ckv_ids_api_key(self):
        checks_list_path = current_dir.parent / 'checkov_checks_list.txt'
        if sys.version_info[1] == 8 and platform.system() == 'Linux':
            with open(checks_list_path, encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i in [0, 1]:
                        # skip the header lines
                        continue
                    line = "".join(line.split())
                    if line and isinstance(line, str):
                        if line == "---":
                            # end of table
                            continue
                        check_id = line.split('|')[2]
                        ckv_ids = re.match(ckv_check_id_pattern, check_id)
                        self.assertFalse(ckv_ids)


if __name__ == '__main__':
    unittest.main()
