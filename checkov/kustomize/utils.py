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
        logging.debug(f"An error occurred testing the {kustomize_command} command:", exc_info=True)

    return None


def get_kubectl_version(kubectl_command: str) -> float | None:
    try:
        proc = subprocess.run([kubectl_command, "version", "--client=true"], capture_output=True)  # nosec
        version_output = proc.stdout.decode("utf-8")

        if "Client Version:" in version_output:
            if "Major:" in version_output and "Minor:" in version_output:
                # version <= 1.27 output looks like 'Client Version: version.Info{Major:"1", Minor:"27", GitVersion:...}\n...'
                kubectl_version_major = version_output.split("\n")[0].split('Major:"')[1].split('"')[0]
                kubectl_version_minor = version_output.split("\n")[0].split('Minor:"')[1].split('"')[0]
            else:
                # version >= 1.28 output looks like 'Client Version: v1.28.0\n...'
                kubectl_version_str = version_output.split("\n")[0].replace("Client Version: v", "")
                kubectl_version_major, kubectl_version_minor, *_ = kubectl_version_str.split(".")
            kubectl_version = float(f"{kubectl_version_major}.{kubectl_version_minor}")

            return kubectl_version
    except Exception:
        logging.debug(f"An error occurred testing the {kubectl_command} command:", exc_info=True)

    return None
