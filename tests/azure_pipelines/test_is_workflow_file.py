from __future__ import annotations

import os
import unittest
from unittest import mock

from checkov.azure_pipelines.runner import (
    DEFAULT_AZURE_PIPELINES_FILE_NAMES,
    Runner,
    _extra_pipelines_file_names,
)


class TestIsWorkflowFile(unittest.TestCase):
    """Coverage for the file-name detection logic exercised by
    ``Runner.is_workflow_file`` after introducing
    ``CHECKOV_AZURE_PIPELINES_FILE_NAMES``."""

    def test_default_file_names_are_recognized(self):
        for name in DEFAULT_AZURE_PIPELINES_FILE_NAMES:
            self.assertTrue(Runner.is_workflow_file(name))
            self.assertTrue(Runner.is_workflow_file(f"path/to/{name}"))

    def test_unrelated_yaml_is_not_recognized(self):
        self.assertFalse(Runner.is_workflow_file("some-other-pipeline.yml"))
        self.assertFalse(Runner.is_workflow_file(".github/workflows/ci.yml"))

    def test_extra_file_names_via_env_var_comma(self):
        env = {"CHECKOV_AZURE_PIPELINES_FILE_NAMES": "ci.yml,pr-pipeline.yaml"}
        with mock.patch.dict(os.environ, env, clear=False):
            self.assertTrue(Runner.is_workflow_file("ci.yml"))
            self.assertTrue(Runner.is_workflow_file(".azuredevops/pr-pipeline.yaml"))
            # Defaults still work
            self.assertTrue(Runner.is_workflow_file("azure-pipelines.yml"))
            # Unrelated names still rejected
            self.assertFalse(Runner.is_workflow_file("foo.yml"))

    def test_extra_file_names_via_env_var_whitespace(self):
        env = {"CHECKOV_AZURE_PIPELINES_FILE_NAMES": "ci.yml  pr-pipeline.yaml\tnightly.yml"}
        with mock.patch.dict(os.environ, env, clear=False):
            for name in ("ci.yml", "pr-pipeline.yaml", "nightly.yml"):
                self.assertTrue(Runner.is_workflow_file(name), msg=name)

    def test_empty_env_var_falls_back_to_defaults(self):
        env = {"CHECKOV_AZURE_PIPELINES_FILE_NAMES": ""}
        with mock.patch.dict(os.environ, env, clear=False):
            self.assertEqual(_extra_pipelines_file_names(), ())
            self.assertTrue(Runner.is_workflow_file("azure-pipelines.yml"))
            self.assertFalse(Runner.is_workflow_file("ci.yml"))

    def test_env_var_with_only_separators_yields_no_extras(self):
        env = {"CHECKOV_AZURE_PIPELINES_FILE_NAMES": " , ,\t  "}
        with mock.patch.dict(os.environ, env, clear=False):
            self.assertEqual(_extra_pipelines_file_names(), ())

    def test_env_var_does_not_persist_across_unset(self):
        env = {"CHECKOV_AZURE_PIPELINES_FILE_NAMES": "ci.yml"}
        with mock.patch.dict(os.environ, env, clear=False):
            self.assertTrue(Runner.is_workflow_file("ci.yml"))
        # After the env var is gone, the extra suffix should no longer match.
        self.assertFalse(Runner.is_workflow_file("ci.yml"))


if __name__ == "__main__":
    unittest.main()
