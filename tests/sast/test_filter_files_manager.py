from checkov.sast.engines.files_filter_manager import FilesFilterManager
from checkov.common.sast.consts import SastLanguages
import pathlib
import os


def test_sast_js_filtered_files_by_ts():
    test_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code', 'js_filtered_build_ts')
    files_filter_manager = FilesFilterManager([test_dir], set([SastLanguages.JAVASCRIPT]))
    filtered_paths = files_filter_manager.get_files_to_filter()
    assert len(filtered_paths) == 3
    assert filtered_paths[0].endswith('example2/build/file.js')
    assert filtered_paths[1].endswith('example1/build')
    assert filtered_paths[2].endswith('example3/main.js')
