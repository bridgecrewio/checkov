import abc

from checkov.common.output.record import Record
from checkov.policies_3d.syntax.syntax import Predicate


class SecretsPredicate(Predicate):
    def __init__(self, record: Record) -> None:
        super().__init__()
        self.record = record

    @abc.abstractmethod
    def __call__(self) -> bool:
        raise NotImplementedError()
