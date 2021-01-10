import logging
from abc import abstractmethod

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

    def run(self, scanned_file, entity_configuration, entity_name, entity_type, skip_info):
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
                check_result['result'] = self.scan_entity_conf(entity_configuration, entity_type)
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
    def scan_entity_conf(self, conf, entity_type):
        raise NotImplementedError()

    @classmethod
    @scan_entity_conf.add_signature(args=["self", "conf"])
    def _scan_entity_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None):
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper

    def get_evaluated_keys(self):
        """
        Retrieves the evaluated keys for the run's report. Child classes override the function and return the `expected_keys` instead.
        :return: List of the evaluated keys, as JSONPath syntax paths of the checked attributes
        """
        return force_list(self.evaluated_keys)
