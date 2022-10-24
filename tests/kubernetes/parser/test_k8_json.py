from pathlib import Path

from checkov.kubernetes.parser.k8_json import load

EXAMPLES_DIR = Path(__file__).parent / "examples"

def test_load_pod():
    # given
    file_path = EXAMPLES_DIR / "json/mongo-pod.json"

    # when
    template, file_lines = load(file_path)

    # then
    assert len(template) == 1
    assert template[0]["apiVersion"] == "v1"
    assert template[0]["kind"] == "Pod"
    assert len(file_lines) == 40


def test_load_not_k8s_file():
    # given
    file_path = EXAMPLES_DIR / "json/normal.json"

    # when
    template, file_lines = load(file_path)

    # then
    assert template == [{}]
    assert file_lines == []
