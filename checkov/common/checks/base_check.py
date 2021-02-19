import abc
import logging
from abc import abstractmethod
from typing import Dict, Mapping

from checkov.common.util.type_forcers import force_list
from checkov.common.models.enums import CheckResult
from checkov.common.multi_signature import MultiSignatureMeta, multi_signature


class BaseCheck(metaclass=MultiSignatureMeta):
    id = ""
    name = ""
    categories = []
    supported_entities = []

    def __init__(self, name, id, categories, supported_entities, block_type):
        self.name = name
        self.id = id
        self.categories = categories
        self.block_type = block_type
        self.supported_entities = supported_entities
        self.logger = logging.getLogger("{}".format(self.__module__))
        self.evaluated_keys = []

    def run(self, scanned_file, entity_configuration, entity_name, entity_type, skip_info, definition_access):
        check_result = {}
        if skip_info:
            check_result['result'] = CheckResult.SKIPPED
            check_result['suppress_comment'] = skip_info['suppress_comment']
            message = "File {}, {} \"{}.{}\" check \"{}\" Result: {}, Suppression comment: {} ".format(
                scanned_file,
                self.block_type,
                entity_type,
                entity_name,
                self.name,
                check_result,
                check_result['suppress_comment']
            )
            self.logger.debug(message)
        else:
            try:
                self.evaluated_keys = []
                check_result['result'] = self.scan_entity_conf(entity_configuration, entity_type,
                                                               entity_name, definition_access)
                check_result['evaluated_keys'] = self.get_evaluated_keys()
                message = "File {}, {}  \"{}.{}\" check \"{}\" Result: {} ".format(
                    scanned_file,
                    self.block_type,
                    entity_type,
                    entity_name,
                    self.name,
                    check_result
                )
                self.logger.debug(message)

            except Exception as e:
                self.logger.error(
                    "Failed to run check: {} for configuration: {} at file: {}".format(
                        self.name,
                        str(entity_configuration),
                        scanned_file
                    )
                )
                raise e
        return check_result

    @multi_signature()
    @abstractmethod
    def scan_entity_conf(self, conf, entity_type, entity_name, definition_access):
        """
        This is the intended main implementation point for checks. This should be overridden to
        provide the main logic for the check.

        :param conf:                dict containing the configuration for the entity.
        :param entity_type:         The entity's defined type (for example "aws_s3_bucket"). If multiple
                                    resource types are supported, this distinguishes the type of the current
                                    entity.
        :param entity_name:         Name of the current entity as defined, if applicable. For example, the
                                    name for a terraform resource of `resource "aws_s3_bucket" "foo"` would
                                    be "foo". If a name is not applicable to a particular framework or check
                                    type, None will be provided.
        :param definition_access:   An instance of BaseDefinitionAccess which allows access to other parts
                                    of the complete document definition. See that class for more information.
                                    Note that subclasses of BaseCheck may provide more specific
                                    implementations which provide easier access to portions of the
                                    definitions. See your specific check class for more information,
                                    if applicable.

        :return:                    A value of the CheckResult enum.
        """
        raise NotImplementedError()

    @classmethod
    @scan_entity_conf.add_signature(args=["self", "conf", "entity_type"])
    def _scan_entity_conf_self_conf_entitytype(cls, wrapped):
        def wrapper(self, conf, entity_type, entity_name=None, definition_access=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf, entity_type)

        return wrapper

    @classmethod
    @scan_entity_conf.add_signature(args=["self", "conf"])
    def _scan_entity_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None, entity_name=None, definition_access=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper

    def get_evaluated_keys(self):
        """
        Retrieves the evaluated keys for the run's report. Child classes override the function and return the `expected_keys` instead.
        :return: List of the evaluated keys, as JSONPath syntax paths of the checked attributes
        """
        return force_list(self.evaluated_keys)


class BaseDefinitionAccess:
    def __init__(self, doc: Dict) -> None:
        super().__init__()
        self.__full_doc = doc

    def full_definition(self) -> Mapping:
        """
        Return the full document definition. Note that the resulting mapping should not be modified. It
        may allow changes to be made, but they will not affect be seen by other checks.

        :return:        A mapping type of the entire definition structure. What exactly is contained at this
                        level is not strictly defined across all frameworks, but often (not always!!) starts
                        keyed by a file location. See your specific check class for more details.
        """
        # NOTE: defensive copy to prevent mutation. MappingProxyType would be great to prevent the need
        #       to copy, in theory, but dpath doesn't work properly with it. :-(
        return dict(self.__full_doc)
