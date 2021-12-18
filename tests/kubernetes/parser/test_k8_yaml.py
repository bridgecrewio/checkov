from pathlib import Path

from checkov.kubernetes.parser.k8_yaml import load

EXAMPLES_DIR = Path(__file__).parent / "examples"

def test_load_pod():
    # given
    file_path = EXAMPLES_DIR / "yaml/busybox.yaml"

    # when
    template, file_lines = load(file_path)

    # then
    assert len(template) == 1
    assert template[0]["apiVersion"] == "v1"
    assert template[0]["kind"] == "Pod"
    assert len(file_lines) == 28


def test_load_not_k8s_file():
    # given
    file_path = EXAMPLES_DIR / "yaml/normal.yaml"

    # when
    template, file_lines = load(file_path)

    # then
    assert template == [{}]
    assert file_lines == []
