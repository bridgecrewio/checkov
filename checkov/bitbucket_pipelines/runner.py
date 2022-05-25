import jmespath

from checkov.bitbucket_pipelines.registry import registry
from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.BITBUCKET_PIPELINES

    def __init__(self):
        super().__init__()

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
        self.add_default_and_pipelines_images(workflow, images, file_path)
        self.add_root_image(file_path, images, workflow_line_numbers, workflow)

        return images

    def add_default_and_pipelines_images(self, workflow: dict, images: set, file_path: str) -> None:
        """

        :param workflow: parsed workflow file
        :param images: set of images to be updated
        :param file_path: path of analyzed workflow
        """
        keywords = [
            'pipelines.default[].step.{image: image, __startline__: __startline__, __endline__:__endline__}',
            'pipelines.*.[*][][][].step.{image: image, __startline__: __startline__, __endline__:__endline__}']
        for keyword in keywords:
            results = jmespath.search(keyword, workflow)
            for result in results:
                image_name = result.get("image", None)
                if image_name:
                    image_id = self.inspect(image_name)
                    image_obj = Image(file_path=file_path, name=image_name, image_id=image_id,
                                      start_line=result["__startline__"],
                                      end_line=result["__endline__"])
                    images.add(image_obj)

    def add_root_image(self, file_path: str, images: set,
                       workflow_line_numbers: dict, workflow: dict) -> None:
        root_image = workflow.get("image", "")

        if root_image:
            for line_number, line_txt in workflow_line_numbers:
                if "image" in line_txt and not line_txt.startswith(' '):
                    image_id = self.inspect(root_image)
                    image_obj = Image(
                        file_path=file_path,
                        name=root_image,
                        image_id=image_id,
                        start_line=line_number,
                        end_line=line_number,
                    )
                    images.add(image_obj)
