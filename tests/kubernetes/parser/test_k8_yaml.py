import unittest
from pathlib import Path

from checkov.kubernetes.parser.k8_yaml import load

EXAMPLES_DIR = Path(__file__).parent / "examples"


class TestScannerRegistry(unittest.TestCase):
    def test_load_pod(self):
        # given
        file_path = EXAMPLES_DIR / "yaml/busybox.yaml"

        # when
        template, file_lines = load(file_path)

        # then
        assert len(template) == 1
        assert template[0]["apiVersion"] == "v1"
        assert template[0]["kind"] == "Pod"
        assert len(file_lines) == 28


    def test_load_not_k8s_file(self):
        # given
        file_path = EXAMPLES_DIR / "yaml/normal.yaml"

        # when
        template, file_lines = load(file_path)

        # then
        assert template == [{}]
        assert file_lines == []


    def test_load_helm_template_file(self):
        # given
        file_path = EXAMPLES_DIR / "yaml/helm.yaml"

        # when
        template, file_lines = load(file_path)

        # then
        assert template == [{}]
        assert file_lines == []

    def test_load_helm_vars_file(self):
        # given
        file_path = EXAMPLES_DIR / "yaml/helm2.yaml"

        # when
        template, file_lines = load(file_path)

        # then
        assert template == [{}]
        assert file_lines == []

    def test_load_utf8_bom_file(self):
        # given
        file_path = EXAMPLES_DIR / "yaml/busybox_utf8_bom.yaml"

        # when
        template, file_lines = load(file_path)

        # then
        assert len(template) == 1
        assert template[0]["apiVersion"] == "v1"
        assert template[0]["kind"] == "Pod"
        assert len(file_lines) == 28

    def test_load_templating_configmap(self):
        # given
        file_path = EXAMPLES_DIR / "yaml/not_helm_configmap.yaml"

        # when
        template, file_lines = load(file_path)

        # then
        assert len(template) == 1
        assert template[0]["apiVersion"] == "v1"
        assert template[0]["kind"] == "ConfigMap"
        assert len(file_lines) == 8

if __name__ == '__main__':
    unittest.main()
