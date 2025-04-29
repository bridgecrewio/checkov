import shutil
import tempfile
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner


def test_multiline_keyword_password_in_pod():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        shutil.copytree(Path(__file__).parent / 'masking_secrets', tmpdir, dirs_exist_ok=True)
        Runner().mask_files(files=None, root_folder=tmpdir,
                            runner_filter=RunnerFilter(framework=["secrets"]))

        f = tmp / 'findings_report_with_pass.json'
        assert f.is_file()
        content = f.read_text()
        assert content.count("AKIAY**********") == 12
        assert content.count("AKIAYNKRE4OV2LF6TC3N") == 0
        assert content.count("h4t2TJ**********") == 12
        assert content.count("h4t2TJheVRR8em5VdNCjrSJdQ+p7OHl33SxrZoUi") == 0

        f = tmp / 'assets_report_with_pass.json'
        assert f.is_file()
        content = f.read_text()
        assert content.count("AKIAY**********") == 1
        assert content.count("AKIAYNKRE4OV2LF6TC3N") == 0
        assert content.count("h4t2TJ**********") == 1
        assert content.count("h4t2TJheVRR8em5VdNCjrSJdQ+p7OHl33SxrZoUi") == 0

