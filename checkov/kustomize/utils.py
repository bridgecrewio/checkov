from __future__ import annotations

import logging
import subprocess  # nosec


def get_kustomize_version(kustomize_command: str) -> str | None:
    try:
        proc = subprocess.run([kustomize_command, "version"], capture_output=True)  # nosec
        version_output = proc.stdout.decode("utf-8")

        if "Version:" in version_output:
            # version <= 4 output looks like '{Version:kustomize/v4.5.7 GitCommit:...}\n'
            kustomize_version = version_output[version_output.find("/") + 1 : version_output.find("G") - 1]
        elif version_output.startswith("v"):
            # version >= 5 output looks like 'v5.0.0\n'
            kustomize_version = version_output.rstrip("\n")
        else:
            return None

        return kustomize_version
    except Exception:
        logging.debug(f"An error occured testing the {kustomize_command} command:", exc_info=True)

    return None
