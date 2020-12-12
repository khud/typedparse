import typing as ty
import unittest
from pathlib import Path

from typedparse import short
from typedparse.argparse import ArgParserFactory


class ArgsHolder:
    def __init__(self):
        self.command: ty.Optional[str] = None
        self.args: ty.Dict = {}


class MyType:
    def __init__(self, arg: str):
        self.arg = arg


class TestParserSpec(unittest.TestCase):
    def test_simple_parser(self):
        holder = ArgsHolder()

        def main(filename: str, test: ty.Optional[str]):
            """My brand-new cli

            Args:
                filename: file path
                test: test
            """
            holder.args["filename"] = filename
            holder.args["test"] = test

        parser = ArgParserFactory().create(main)
        parser.parse(["--test", "xxx", "test.txt"])

        self.assertEqual("xxx", holder.args["test"])
        self.assertEqual("test.txt", holder.args["filename"])

    def test_subparsers_level1(self):
        class CLI(object):
            def __init__(self, args_holder: ArgsHolder):
                self.holder = args_holder

            def command1(self, filename: str, float_number: float, number: ty.Optional[int] = 0):
                """My command1

                Args:
                    filename: file path
                    float_number: just a float
                    number: number of lines
                """
                self.holder.command = "command1"
                self.holder.args["filename"] = filename
                self.holder.args["number"] = number
                self.holder.args["float_number"] = float_number

            def command2(self, test: ty.Optional[bool] = False, key: ty.Optional[str] = "xxx"):
                """My command2

                Args:
                    test: test mode
                    key: just a key
                """
                self.holder.command = "command2"
                self.holder.args["test"] = test
                self.holder.args["key"] = key

        holder = ArgsHolder()
        parser = ArgParserFactory().create(CLI(holder))
        parser.parse(["command1", "hello.txt", "11.4", "--number", "10"])

        self.assertEqual("command1", holder.command)
        self.assertEqual("hello.txt", holder.args["filename"])
        self.assertEqual(10, holder.args["number"])
        self.assertEqual(11.4, holder.args["float_number"])

        parser.parse(["command2", "--test"])
        self.assertEqual("command2", holder.command)
        self.assertTrue(holder.args["test"])
        self.assertEqual("xxx", holder.args["key"])

    def test_subparsers_level2(self):
        class Config:
            """Work with configuration"""

            def __init__(self, holder: ArgsHolder):
                self.holder = holder

            def add(self, name: str):
                """Add profile

                Args:
                    name: profile name
                """

                self.holder.command = "add"
                self.holder.args["name"] = name

            def remove(self, name: str):
                """Delete profile

                Args:
                    name: profile name
                """

                self.holder.command = "remove"
                self.holder.args["name"] = name

        class Server:
            """Server operations"""

            def __init__(self, holder: ArgsHolder):
                self.holder = holder

            def start(self):
                """Start server"""

                self.holder.command = "start"

            def stop(self):
                """Stop server"""

                self.holder.command = "stop"

        holder1 = ArgsHolder()
        holder2 = ArgsHolder()

        parser = ArgParserFactory().create([Config(holder1), Server(holder2)])
        parser.parse(["config", "add", "test"])

        self.assertEqual("add", holder1.command)
        self.assertEqual("test", holder1.args["name"])

        parser.parse(["server", "start"])

        self.assertEqual("start", holder2.command)
        self.assertEqual(0, len(holder2.args))

    def test_list_arg(self):
        holder = ArgsHolder()

        def main(filename: str, nums: ty.Optional[ty.List[int]]):
            """My brand-new cli

            Args:
                filename: file path
                nums: some numbers
            """
            holder.args["filename"] = filename
            holder.args["nums"] = nums

        parser = ArgParserFactory().create(main)
        parser.parse(["test.txt", "--nums", "1", "2", "3"])

        self.assertEqual([1, 2, 3], holder.args["nums"])
        self.assertEqual("test.txt", holder.args["filename"])

    def test_defaults(self):
        holder = ArgsHolder()

        def main(filename: str, test: int = 10, opt: ty.Optional[str] = None):
            """My brand-new cli

            Args:
                filename: file path
                test: just for test
                opt: optional
            """
            holder.args["filename"] = filename
            holder.args["test"] = test
            holder.args["opt"] = opt

        parser = ArgParserFactory().create(main)
        parser.parse(["test.txt"])

        self.assertEqual("test.txt", holder.args["filename"])
        self.assertEqual(10, holder.args["test"])
        self.assertIsNone(holder.args["opt"])

    def test_specific_type(self):
        holder = ArgsHolder()

        def main(path: Path):
            """Test path

            Args:
                path: file path
            """
            holder.args["path"] = path

        parser = ArgParserFactory().create(main)
        parser.parse(["test.txt"])

        self.assertEqual(Path("test.txt"), holder.args["path"])

    def test_type_in_scope(self):
        holder = ArgsHolder()

        def main(my: MyType):
            """Test type in scope

            Args:
                my: my var
            """
            holder.args["my"] = my

        parser = ArgParserFactory().create(main)
        parser.parse(["test"])

        self.assertTrue(isinstance(holder.args["my"], MyType))
        self.assertEqual("test", holder.args["my"].arg)

    def test_short(self):
        holder = ArgsHolder()

        @short(number="n")
        def main(path: str, number: ty.Optional[int] = 10):
            """Test path

            Args:
                path: file path
                number: number of lines
            """
            holder.args["path"] = path
            holder.args["number"] = number

        parser = ArgParserFactory().create(main)
        parser.parse(["test.txt", "-n", "6"])

        self.assertEqual(6, holder.args["number"])
