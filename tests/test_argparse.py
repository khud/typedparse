import unittest
import typing as ty

from typedparse.argparse import ArgParserFactory


class ArgHolder:
    def __init__(self):
        self.command: ty.Optional[str] = None
        self.args: ty.Dict = {}


class TestParserSpec(unittest.TestCase):
    def test_simple_parser(self):
        holder = ArgHolder()

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
            def command1(self, filename: str, number: ty.Optional[int] = 0):
                """My command1

                Args:
                    filename: file path
                    number: number of lines
                """
                pass

            def command2(self, test: bool = False, key: ty.Optional[str] = "xxx"):
                """My command2

                Args:
                    test: test mode
                    key: just a key
                """
                pass

        pass

    def test_subparsers_level2(self):
        class Config:
            """Work with configuration"""

            def __init__(self, holder: ArgHolder):
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

            def __init__(self, holder: ArgHolder):
                self.holder = holder

            def start(self):
                """Start server"""

                self.holder.command = "start"

            def stop(self):
                """Stop server"""

                self.holder.command = "stop"

        holder1 = ArgHolder()
        holder2 = ArgHolder()

        parser = ArgParserFactory().create([Config(holder1), Server(holder2)])
        parser.parse(["config", "add", "test"])

        self.assertEqual("add", holder1.command)
        self.assertEqual("test", holder1.args["name"])

        parser.parse(["server", "start"])

        self.assertEqual("start", holder2.command)
        self.assertEqual(0, len(holder2.args))
