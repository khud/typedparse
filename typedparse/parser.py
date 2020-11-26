import abc
import typing as ty


class Parser(object):
    @abc.abstractmethod
    def parse(self, args: ty.Optional[ty.List[str]] = None):
        pass


class ParserFactory(abc.ABC):
    @abc.abstractmethod
    def create(self, obj: ty.Any) -> Parser:
        pass
