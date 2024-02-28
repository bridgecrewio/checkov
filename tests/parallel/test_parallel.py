import os
import unittest
from unittest.mock import patch

from checkov.common.models.enums import ParallelizationType
from checkov.common.parallelizer.parallel_runner import ParallelRunner

class TestParallel(unittest.TestCase):
    # Windows os tests
    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_default_for_windows(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Windows'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.THREAD)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0', 'CHECKOV_PARALLELIZATION_TYPE': 'none'})
    def test_windows_with_override_to_none(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Windows'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.NONE)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0', 'CHECKOV_PARALLELIZATION_TYPE': 'fork'})
    def test_windows_with_override_to_fork(self) -> None:
        # fork and spawn is not supporting by Windows
        with unittest.mock.patch('platform.system', return_value='Windows'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.FORK)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_windows_with_explicitly_to_spawn(self) -> None:
        # fork and spawn is not supporting by Windows
        with unittest.mock.patch('platform.system', return_value='Windows'):
            parallel_runner = ParallelRunner(parallelization_type=ParallelizationType.SPAWN)
            self.assertEqual(parallel_runner.type, ParallelizationType.THREAD)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_windows_with_explicitly_to_none(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Darwin'):
            parallel_runner = ParallelRunner(parallelization_type=ParallelizationType.NONE)
            self.assertEqual(parallel_runner.type, ParallelizationType.NONE)

    # macOS os tests
    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_mac_default(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Darwin'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.THREAD)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0', 'CHECKOV_PARALLELIZATION_TYPE': 'none'})
    def test_mac_with_override_to_none(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Darwin'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.NONE)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0', 'CHECKOV_PARALLELIZATION_TYPE': 'fork'})
    def test_mac_with_override_to_fork(self) -> None:
        # fork and spawn is not supporting by macOS
        with unittest.mock.patch('platform.system', return_value='Darwin'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.FORK)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_mac_with_explicitly_to_spawn(self) -> None:
        # fork and spawn is not supporting by macOS
        with unittest.mock.patch('platform.system', return_value='Darwin'):
            parallel_runner = ParallelRunner(parallelization_type=ParallelizationType.SPAWN)
            self.assertEqual(parallel_runner.type, ParallelizationType.THREAD)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_mac_with_explicitly_to_none(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Darwin'):
            parallel_runner = ParallelRunner(parallelization_type=ParallelizationType.NONE)
            self.assertEqual(parallel_runner.type, ParallelizationType.NONE)

    # general tests
    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_default_linux(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Linux'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.FORK)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0', 'CHECKOV_PARALLELIZATION_TYPE': 'spawn'})
    def test_linux_override_by_env_param(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Linux'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.SPAWN)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '0'})
    def test_linux_override_by_incoming_param(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Linux'):
            parallel_runner = ParallelRunner(parallelization_type=ParallelizationType.SPAWN)
            self.assertEqual(parallel_runner.type, ParallelizationType.SPAWN)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '1'})
    def test_linux_running_by_pycharm(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Linux'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.NONE)

    @patch.dict(os.environ, {'PYCHARM_HOSTED': '1', 'CHECKOV_PARALLELIZATION_TYPE': 'spawn'})
    def test_linux_running_by_pycharm_override_by_env_param(self) -> None:
        with unittest.mock.patch('platform.system', return_value='Linux'):
            parallel_runner = ParallelRunner()
            self.assertEqual(parallel_runner.type, ParallelizationType.SPAWN)

if __name__ == "__main__":
    unittest.main()
