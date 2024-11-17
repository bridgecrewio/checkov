import shutil
from pathlib import Path
from distutils.dir_util import copy_tree

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner


def test_multiline_keyword_password_in_pod():
    # given
    test_file_path = Path(__file__).parent / "masking_secrets"
    working_test_file_path = test_file_path / "tmp"

    if working_test_file_path.exists():
        shutil.rmtree(working_test_file_path)

    copy_tree(str(test_file_path), str(working_test_file_path))
    #  when
    Runner().mask_files(files=None, root_folder=str(working_test_file_path),
                        runner_filter=RunnerFilter(framework=["secrets"]))

    #  then
    content = (working_test_file_path / "findings_report_with_pass.json").read_text()
    assert content.count("AKIAY**********") == 12
    assert content.count("AKIAYNKRE4OV2LF6TC3N") == 0
    assert content.count("h4t2TJ**********") == 12
    assert content.count("h4t2TJheVRR8em5VdNCjrSJdQ+p7OHl33SxrZoUi") == 0

    content = (working_test_file_path / "assets_report_with_pass.json").read_text()
    assert content.count("AKIAY**********") == 1
    assert content.count("AKIAYNKRE4OV2LF6TC3N") == 0
    assert content.count("h4t2TJ**********") == 1
    assert content.count("h4t2TJheVRR8em5VdNCjrSJdQ+p7OHl33SxrZoUi") == 0

    shutil.rmtree(working_test_file_path)

