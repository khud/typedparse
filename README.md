# Typedparse

What is typedparse? It is a parser for command-line options based on type hints. Typedparse uses the argparse package as
the backend. So you don't need to define parsers and subparsers by yourself anymore. Just write clean, typed, and
documented code; typedparse will do all work for you.

```python
import typedparse
import typing as ty


def main(file: str, number: ty.Optional[int] = 6):
    """Display first lines of a file.

    Args:
        file: file to display
        number: number of lines to display
    """
    with open(file, "r") as f:
        for i in range(0, number):
            print(f.readline(), end="")


if __name__ == "__main__":
    typedparse.parse(main)
```

Here is a small example that emulates the standard `head` command. Here you need only specify types and default values
for the function's formal parameters and pass them into the `parse` function. You also have to specify the docstring for
the function it will be used to generate help. That's it.

If we run the program with one argument `-h` or `--help`, it produces the following output:

```
usage: head.py [-h] [--number [NUMBER]] file

positional arguments:
  file               file to display

optional arguments:
  -h, --help         show this help message and exit
  --number [NUMBER]  number of lines to display
```

Typedparse heavily relies on not only type hints but [docstring_parser](https://github.com/rr-/docstring_parser)
package. So it supports all popular documentation styles, but you need to be sure your docstring is well-formed
according to the style you chose. This means you can skip the long description but can't skip the short one and
parameters' description.

## Positional and optional arguments

The separation of positional and optional arguments in the function definition and command-line arguments is slightly
different because it allows for a default value. In typedparse, we use Optional type to distinguish positional and
optional arguments:

```python
import typing as ty


def main(foo: str, bar: ty.Optional[str] = "bar"):
    ...
```

In this example, `foo` is a positional argument, and `bar` is optional with the default value "bar". You can add default
value for positional arguments too, e.g. `def main(foo: str = "foo", ...)`.

## Types of arguments

For any argument, we must specify the type using a type hint for a certain formal parameter. It can be the built-in
Python type like `int`, `float` or `str`. Or any user-defined class with a constructor that accepts a string argument.
For example, we can use `Path` instead of `str` type for filenames and paths.

## Short flags

To introduce a short flag, one can use a decorator `options` for the functions:

```python
import typing as ty
import typedparse


@typedparse.options(bar="-b")
def main(foo: str, bar: ty.Optional[str] = "bar"):
    ...
```

Of course, it makes sense only for optional arguments. Now it will work with both
`--bar` and `-b` flags.

To use only the short flag, the simplest way to do it is `@options(bar=["-b"])`. You can also use another
name for the long flag by the same trick: `bar=["--box"]`
or use both `bar=["-b", "--box"]`. It will affect only the command line arguments but not the function's formal
parameters.

## Subparsers

Typedparse supports a hierarchy of parsers in a very natural way. You can combine functions in classes, classes in
lists. Consider the following example:

```python
import typedparse
import typing as ty


class CliExample:

    def add(self, name: str, email: ty.Optional[str] = None):
        """Add user to the database

        Args:
            name: user's name
            email: user's email
        """
        pass

    def remove(self, name: str):
        """Remove user from the database

        Args:
            name: user's name
        """
        pass


if __name__ == "__main__":
    typedparse.parse(CliExample())
```

There are two commands here:  `add` and `remove` with their own set of arguments. Typical usage will look like:

```bash
python commands.py add john --email john@mycompany.com
```

So, the `name` parameter will be bound to `john`, and the `email` will be bound to `john@mycompany.com`.

## List arguments

List arguments are supported out of the box in typedparse:

```python
import typing as ty


def main(numbers: ty.List[int]):
    """My brand new CLI

    Args:
        numbers: a list of numbers
    """
    ...
```

But there are two possible issues here:

- By default, the number of arguments in the list is more than one. This is equivalent to `nargs="+"` in argparse
  package.
- It may be inconvenient to have the displayed name
  (meta variable in terms of argparse) the same as the corresponding formal parameter. It will look
  like `numbers [numbers ...]` if we would try to display help.

How to manage that? For the second case, we can rename the formal parameter or
use `@options(flags=["number"])` to make it singular. If we want to allow an empty list, we can specify it in
the following way `@options(numbers={"nargs": "*"})`. We also can combine these two options if we want:

```python
import typedparse
import typing as ty


@typedparse.options(numbers={
    "flags": ["number"],
    "nargs": "*"
})
def main(numbers: ty.List[int]):
    """My brand new CLI

    Args:
        numbers: a list of numbers
    """
    ...
```

## Custom types

If you want to parse arguments to your own types, you can do that 
in the following manner:

```python
import typedparse
import typing as ty

def to_int(s: str) -> int:
    if s.startswith("0x"):
        return int(s, 16)
    elif s.startswith("0"):
        return int(s, 8)

    return int(s, 10)

@typedparse.options(test={
    "type": to_int
})
def main(test: ty.Optional[int] = 0):
    """Test

    Args:
        test: a test
    """
    ...
```
In this example, we use a custom function to convert string arguments to integers, 
which supports hexadecimal and octal representations.