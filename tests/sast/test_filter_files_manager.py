from checkov.sast.engines.files_filter_manager import FilesFilterManager
from checkov.common.sast.consts import SastLanguages
import pathlib


def test_sast_js_filtered_files_by_ts():
    test_dir = pathlib.Path(__file__).parent.resolve() + '/source_code/js_filtered_build_ts'
    files_filter_manager = FilesFilterManager(test_dir, SastLanguages.JAVASCRIPT)
    filtered_paths = files_filter_manager.get_files_to_filter()
    assert len(filtered_paths) == 2823
    
