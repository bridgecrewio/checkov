import os

from checkov.common.images.image_referencer import ImageReferencer
from checkov.common.output.report import CheckType
from checkov.github_actions.checks.job_registry import registry as job_registry
from checkov.yaml_doc.runner import Runner as YamlRunner

WORKFLOW_DIRECTORY = ".github/workflows/"


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.GITHUB_ACTIONS
    block_type_registries = {
        'jobs': job_registry,
    }

    def __init__(self):
        super().__init__()

    def require_external_checks(self):
        return False

    def import_registry(self):
        return self.block_type_registries['jobs']

    def _parse_file(self, f):
        if self.is_workflow_file(f):
            return super()._parse_file(f)

    def is_workflow_file(self, f):
        abspath = os.path.abspath(f)
        return WORKFLOW_DIRECTORY in abspath and abspath.endswith(("yml", "yaml"))

    def get_images(self, f):
        # workflow file can have a job run within a container.
        # example: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#example-defining-credentials-for-a-container-registry

        images = []

        workflow, workflow_line_numbers = self._parse_file(f)
        jobs = workflow.get("jobs", {})
        for job_name, job_object in jobs.items():
            if isinstance(job_object, dict):
                container = job_object.get("container", {})
                image = None
                if isinstance(container, dict):
                    image = container.get("image", "")
                elif isinstance(container, str):
                    image = container
                if image:
                    image_id = self.pull_image(image)
                    if image_id:
                        images.append(image_id)

        return set(images)
