import typing as ty
import unittest
from pathlib import Path

from typedparse import options
from typedparse.argparse import ArgParserFactory


class ArgsHolder:
    def __init__(self):
        self.command: ty.Optional[str] = None
        self.args: ty.Dict = {}


class MyType:
    def __init__(self, arg: str):
        self.arg = arg


class TestArgParse(unittest.TestCase):
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

            @options(number="-n")
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
        parser.parse(["command1", "hello.txt", "11.4", "-n", "10"])

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

        @options(number="-n")
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

    def test_bool(self):
        holder = ArgsHolder()

        def main(pos1: bool, pos2: bool = True,
                 opt1: ty.Optional[bool] = False,
                 opt2: ty.Optional[bool] = True):
            """Test path

            Args:
                pos1: pos1
                pos2: pos2
                opt1: opt1
                opt2: opt2
            """
            holder.args["pos1"] = pos1
            holder.args["pos2"] = pos2
            holder.args["opt1"] = opt1
            holder.args["opt2"] = opt2

        parser = ArgParserFactory().create(main)
        parser.parse(["false"])

        self.assertFalse(holder.args["pos1"])
        self.assertTrue(holder.args["pos2"])
        self.assertFalse(holder.args["opt1"])
        self.assertTrue(holder.args["opt2"])

        parser.parse(["false", "false", "--opt1", "--opt2"])

        self.assertFalse(holder.args["pos1"])
        self.assertFalse(holder.args["pos2"])
        self.assertTrue(holder.args["opt1"])
        self.assertFalse(holder.args["opt2"])

    def test_flags(self):
        holder = ArgsHolder()

        @options(number=["-n", "--num"])
        def main(number: ty.Optional[int] = 10):
            """Test path

            Args:
                number: number of lines
            """
            holder.args["number"] = number

        parser = ArgParserFactory().create(main)
        parser.parse(["-n", "20"])
        self.assertEqual(20, holder.args["number"])
        parser.parse(["--num", "30"])
        self.assertEqual(30, holder.args["number"])

    def test_nargs(self):
        holder = ArgsHolder()

        @options(my_list={
            "flags": ["number"],
            "nargs": "*"
        })
        def main(my_list: ty.List[int]):
            """Test path

            Args:
                my_list: a list of numbers
            """
            holder.args["my_list"] = my_list

        parser = ArgParserFactory().create(main)
        parser.parse([])
        self.assertEqual([], holder.args["my_list"])

        parser.parse(["1", "2", "3"])
        self.assertEqual([1, 2, 3], holder.args["my_list"])

    def test_type_func(self):
        holder = ArgsHolder()

        def smart_int(s: str) -> int:
            if s.startswith("0x"):
                return int(s, 16)
            elif s.startswith("0"):
                return int(s, 8)

            return int(s, 10)

        @options(test={
            "type": smart_int
        })
        def main(test: ty.Optional[int] = 0):
            """Test

            Args:
                test: a test
            """
            holder.args["test"] = test

        parser = ArgParserFactory().create(main)
        parser.parse(["--test", "0xFF"])
        self.assertEqual(255, holder.args["test"])

    def test_generate_short_flags(self):
        holder = ArgsHolder()

        def main(foo: str = "qqq", bar: ty.Optional[bool] = False, baz: ty.Optional[bool] = False):
            """Test

            Args:
                foo: foo
                bar: bar
                baz: baz
            """
            holder.args["foo"] = foo
            holder.args["bar"] = bar
            holder.args["baz"] = baz

        parser = ArgParserFactory(generate_short_flags=True).create(main)
        parser.parse(["test", "-b"])
        self.assertEqual("test", holder.args["foo"])
        self.assertTrue(holder.args["bar"])
        self.assertFalse(holder.args["baz"])

        parser.parse(["-a"])
        self.assertEqual("qqq", holder.args["foo"])
        self.assertFalse(holder.args["bar"])
        self.assertTrue(holder.args["baz"])

    def test_snake_and_kebab_case(self):
        holder = ArgsHolder()

        def main(my_long_flag: ty.Optional[str]):
            """My brand-new CLI

            Args:
                my_long_flag: my long flag
            """
            holder.args["my_long_flag"] = my_long_flag

        parser = ArgParserFactory().create(main)
        parser.parse(["--my-long-flag", "test"])

        self.assertEqual("test", holder.args["my_long_flag"])

        parser = ArgParserFactory(snake_case_flags=True).create(main)
        parser.parse(["--my_long_flag", "test"])

        self.assertEqual("test", holder.args["my_long_flag"])