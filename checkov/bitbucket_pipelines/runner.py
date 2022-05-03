from checkov.bitbucket_pipelines.checks.registry import registry
from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.BITBUCKET_PIPELINES

    def require_external_checks(self):
        return False

    def import_registry(self):
        return registry

    def _parse_file(self, f):
        if self.is_workflow_file(f):
            return super()._parse_file(f)

    def is_workflow_file(self, file_path):
        """
        :return: True if the file mentioned is named bitbucket-pipelines.yml. Otherwise: False
        """
        return file_path.endswith(("bitbucket-pipelines.yml", "bitbucket-pipelines.yaml"))

    def get_images(self, file_path):
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected

        File sample that will return 4 Image objects:
        #image: node:10.15.0
        #
        #pipelines:
        #  default:
        #    - step:
        #        name: Build and test
        #        image: node:10.0.0
        #        script:
        #          - npm install
        #          - npm test
        #          - npm run build
        #        artifacts:
        #          - dist/**
        #    - step:
        #        name: Deploy
        #        image: python:3.7.2
        #        trigger: manual
        #        script:
        #          - python deploy.py
        #  custom:
        #    sonar:
        #      - step:
        #          image: python:3.8.2
        #          script:
        #            - echo "Manual triggers for Sonar are awesome!"
        #    deployment-to-prod:
        #      - step:
        #          script:
        #            - echo "Manual triggers for deployments are awesome!"
        #  branches:
        #    staging:
        #      - step:
        #          script:
        #            - echo "Auto pipelines are cool too."
        :return: List of container image objects mentioned in the file.

        """

        images = set()

        workflow, workflow_line_numbers = self._parse_file(file_path)
        root_image = workflow.get("image", "")
        self.add_root_image(file_path, images, root_image, workflow_line_numbers)

        pipelines = workflow.get("pipelines", {})
        default_pipeline = pipelines.pop("default", {})
        self.add_default_pipeline_images(file_path, images, default_pipeline)

        self.add_pipeline_images(file_path, images, pipelines)

        return images

    def add_root_image(self, file_path: str, images: set, root_image: str,
                       workflow_line_numbers: tuple[int, str]) -> None:
        if root_image:
            for line_number, line_txt in workflow_line_numbers:
                if "image" in line_txt and not line_txt.startswith(' '):
                    image_id = self.pull_image(root_image)
                    image_obj = Image(
                        file_path=file_path,
                        name=root_image,
                        image_id=image_id,
                        start_line=line_number,
                        end_line=line_number,
                    )
                    images.add(image_obj)

    def add_pipeline_images(self, file_path: str, images: set, pipelines: dict):
        for pipeline_name, pipeline_obj in pipelines.items():
            if isinstance(pipeline_obj, dict):
                for step_name, step_obj in pipeline_obj.items():
                    if isinstance(step_obj, list):
                        for step in step_obj:
                            self.add_step_image(file_path, images, step)

    def add_default_pipeline_images(self, file_path: str, images: set, default_pipeline: dict):
        for step in default_pipeline:
            if isinstance(step, dict):
                self.add_step_image(file_path, images, step)

    def add_step_image(self, file_path, images, step):
        step_obj = step.get('step', {})
        image = step_obj.get("image", '')
        if image:
            image_id = self.pull_image(image)
            if image_id:
                start_line = step_obj['__startline__']
                end_line = step_obj['__endline__']

                image_obj = Image(file_path=file_path, name=image, image_id=image_id,
                                  start_line=start_line,
                                  end_line=end_line)
                images.add(image_obj)
