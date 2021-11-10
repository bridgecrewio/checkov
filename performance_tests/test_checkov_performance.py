import math
import os

import pytest
import time

from pytest_benchmark.plugin import benchmark

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner

@pytest.mark.benchmark(
    group="performance-tests",
    min_time=0,
    max_time=120,
    min_rounds=1,
    timer=time.time,
    disable_gc=True,
    warmup=False
)
def test_performance(benchmark):
    def test_terragoat():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = "/Users/tronxd/clones/tronxd/terragoat"  # TODO run on forked data
        runner_filter = RunnerFilter()
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner())
        reports = runner_registry.run(root_folder=test_files_dir)
        assert len(reports) > 0

    benchmark(test_terragoat)
