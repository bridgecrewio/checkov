from checkov.sast.checks_infra.base_registry import Registry
import pathlib
import os


checks_dir = pathlib.Path(__file__).parent.resolve().parent.resolve()
registry = Registry(os.path.join(checks_dir, 'checks'))
