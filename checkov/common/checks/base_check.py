import inspect
import logging
from abc import abstractmethod, ABCMeta

from checkov.common.models.enums import CheckResult


class _CheckMeta(ABCMeta):
    def __new__(mcs, name, bases, *args, **kwargs):
        cls = super().__new__(mcs, name, bases, *args, **kwargs)
        _CheckMeta._fix_scan_entity_conf(cls)
        return cls

    @staticmethod
    def _fix_scan_entity_conf(cls):
        """
        Ensures that `scan_entity_conf` must not expect entity_type. If the implementation doesn't expect it, the method
        is wrapped into a method that expects it but discards it.
        :param cls: the check class to modify.
        """
        function = cls.scan_entity_conf
        args = inspect.getargs(function.__code__).args
        if args == ["self", "conf", "entity_type"]:
            # correct implementation according to the current standpoint.
            wrapper = function
        elif args == ["self", "conf"]:
            # First implementation which does not expect `entity_type`
            # we discard the argument
            def wrapper(self, conf, entity_type):
                return function(self, conf)
        else:
            # unknown implementation
            raise NotImplementedError(
                f"The signature {args} for {function.__name__} is not supported. "
                f"See {BaseCheck.__module__}.{BaseCheck.__name__}.{BaseCheck.scan_entity_conf.__name__}."
            )
        cls.scan_entity_conf = wrapper


class BaseCheck(metaclass=_CheckMeta):
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
                check_result['result'] = self.scan_entity_conf(entity_configuration, entity_type)
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

    @abstractmethod
    def scan_entity_conf(self, conf, entity_type):
        raise NotImplementedError()
