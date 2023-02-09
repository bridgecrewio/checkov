import subprocess

from checkov.helm.runner import Runner


def helm_exists() -> bool:
    try:
        subprocess.run([Runner.helm_command, "version"], check=True, stdout=subprocess.PIPE)
    except Exception:
        return False
    return True
