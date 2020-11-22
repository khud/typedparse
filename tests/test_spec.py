import unittest
import typing as ty

from typedparse import create_spec, Argument


class TestParserSpec(unittest.TestCase):
    def test_positional_and_optional_args(self):
        class MyClass(object):
            """Manage something"""

            def add(self, param1: str = "default", param2: ty.Optional[str] = None, param3: ty.Optional[str] = None,
                    param4: ty.Optional[str] = None, param5: bool = False, param6: ty.Optional[bool] = None,
                    param7: ty.Optional[int] = None):
                """Create a new profile

                Args:
                    param1: do something 1
                    param2: do something 2
                    param3: do something 3
                    param4: do something 4
                    param5: do something 5
                    param6: do something 6
                    param7: do something 7
                """
                pass

        spec = create_spec(MyClass())

        self.assertEqual("Manage something", spec.desc)

        self.assertEqual(Argument(name="param1", tpe="str", optional=False,
                                  default="default", desc="do something 1"), spec.get("param1"))

        self.assertEqual(Argument(name="param2", tpe="str", optional=True,
                                  default=None, desc="do something 2"), spec.get("param2"))

        self.assertEqual(Argument(name="param3", tpe="str", optional=True,
                                  default=None, desc="do something 3"), spec.get("param3"))

        self.assertEqual(Argument(name="param4", tpe="str", optional=True,
                                  default=None, desc="do something 4"), spec.get("param4"))

        self.assertEqual(Argument(name="param5", tpe="bool", optional=True,
                                  default=False, desc="do something 5"), spec.get("param5"))

        self.assertEqual(Argument(name="param6", tpe="bool", optional=True,
                                  default=None, desc="do something 6"), spec.get("param6"))

        self.assertEqual(Argument(name="param7", tpe="int", optional=True,
                                  default=None, desc="do something 7"), spec.get("param7"))

    def test_list_args(self):
        class MyCLI(object):
            """My first CLI"""

            def test(self, files: ty.List[str]):
                """Test files

                Args:
                    files: list of files
                """
                pass

        spec = create_spec(MyCLI())

        self.assertEqual(Argument(name="files", tpe="typing.List[str]", optional=False,
                                  default=None, desc="list of files"), spec.get("files"))
