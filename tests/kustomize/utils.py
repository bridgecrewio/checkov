import subprocess

from checkov.kustomize.runner import Runner


def kustomize_exists() -> bool:
    try:
        subprocess.run([Runner.kustomize_command, "version"], check=True, stdout=subprocess.PIPE)
    except Exception:
        return False
    return True
