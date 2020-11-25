import typing as ty
import abc
from argparse import ArgumentParser

from typedparse.parser import Parser, ParserFactory
import typedparse.spec as spec


class AbstractArgParser(abc.ABC, Parser):
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def parse(self, args: ty.Optional[ty.List[str]] = None):
        self.parser.parse_args(args)


class ArgParserLeaf(AbstractArgParser):
    def __init__(self, parser: ArgumentParser, sp: spec.ParserLeaf):
        super().__init__(parser)
        for arg in sp.args:
            name = arg.name if not arg.optional else f"--{arg.name}"
            is_list, in_type = arg.is_list()
            if arg.tpe == "bool":
                self.parser.add_argument(name, help=arg.desc, action="store_true")
            elif is_list:
                pass
            else:
                kwargs = {}
                if arg.default is not None:
                    kwargs.update(nargs="?")
                    # kwargs.update()
                self.parser.add_argument(name, help=arg.desc, **kwargs)


class ArgParserNode(AbstractArgParser):
    def __init__(self, parser: ArgumentParser, sp: spec.ParserNode):
        super().__init__(parser)
        sub = self.parser.add_subparsers()
        for child in sp.children:
            parser = sub.add_parser(child.name)
            factory = ArgParserFactory(parser)
            factory.create(child)


class ArgParserFactory(ParserFactory):
    def __init__(self, parser: ty.Optional[ArgumentParser] = None):
        self.parser = parser or ArgumentParser()

    def create(self, obj: ty.Any) -> Parser:
        if not isinstance(obj, spec.ParserSpec):
            obj = spec.create(obj)

        if isinstance(obj, spec.ParserLeaf):
            return ArgParserLeaf(self.parser, obj)
        elif isinstance(obj, spec.ParserNode):
            return ArgParserNode(self.parser, obj)
        else:
            raise ValueError(obj)
