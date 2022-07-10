import os
import platform

import pytest
import time

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner

# Ensure repo_name is a cloned repository into performance_tests directory.
# Thresholds are in ms, and are set to the current maximum duration of checkov on the repository
performance_configurations = {
    'terraform': {
        'repo_name': 'terraform-aws-components',
        'threshold': {
            "Darwin": 18.0,
            "Linux": 12.0,
            "Windows": 14.0,
        }
    },
    'cloudformation': {
        'repo_name': 'aws-cloudformation-templates',
        'threshold': {
            "Darwin": 350.0,
            "Linux": 250.0,
            "Windows": 300.0,
        }
    },
    'kubernetes': {
        'repo_name': 'kubernetes-yaml-templates',
        'threshold': {
            "Darwin": 550.0,
            "Linux": 300.0,
            "Windows": 500.0,
        }
    }
}

DEVIATION_PERCENT = 10
SYSTEM_NAME = platform.system()


@pytest.mark.benchmark(
    group="terraform-performance-tests",
    disable_gc=True,
    min_time=0.1,
    max_time=0.5,
    min_rounds=10,
    timer=time.time,
    warmup=False,
)
def test_terraform_performance(benchmark):
    repo_name = performance_configurations['terraform']['repo_name']
    repo_threshold = performance_configurations['terraform']['threshold'][SYSTEM_NAME]

    def run_terraform_scan():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, repo_name)
        runner_filter = RunnerFilter()
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner())
        reports = runner_registry.run(root_folder=test_files_dir)
        assert len(reports) > 0

    benchmark(run_terraform_scan)
    assert benchmark.stats.stats.mean <= repo_threshold + (DEVIATION_PERCENT / 100.0) * repo_threshold


@pytest.mark.benchmark(
    group="cloudformation-performance-tests",
    disable_gc=True,
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
    timer=time.time,
    warmup=False
)
def test_cloudformation_performance(benchmark):
    repo_name = performance_configurations['cloudformation']['repo_name']
    repo_threshold = performance_configurations['cloudformation']['threshold'][SYSTEM_NAME]

    def run_cloudformation_scan():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, repo_name)
        runner_filter = RunnerFilter()
        runner_registry = RunnerRegistry(banner, runner_filter, cfn_runner())
        reports = runner_registry.run(root_folder=test_files_dir)
        assert len(reports) > 0

    benchmark(run_cloudformation_scan)
    assert benchmark.stats.stats.mean <= repo_threshold + (DEVIATION_PERCENT / 100) * repo_threshold


@pytest.mark.benchmark(
    group="kubernetes-performance-tests",
    disable_gc=True,
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
    timer=time.time,
    warmup=False
)
def test_k8_performance(benchmark):
    repo_name = performance_configurations['kubernetes']['repo_name']
    repo_threshold = performance_configurations['kubernetes']['threshold'][SYSTEM_NAME]

    def run_kubernetes_scan():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, repo_name)
        runner_filter = RunnerFilter()
        runner_registry = RunnerRegistry(banner, runner_filter, k8_runner())
        reports = runner_registry.run(root_folder=test_files_dir)
        assert len(reports) > 0

    benchmark(run_kubernetes_scan)
    assert benchmark.stats.stats.mean <= repo_threshold + (DEVIATION_PERCENT / 100) * repo_threshold
