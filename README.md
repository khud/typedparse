# Typedparse

What is typedparse? It is a lightweight parser for command-line options based on type hints. Typedparse uses the argparse
package as the backend. So you don't need to define parsers and subparsers by yourself anymore. Just write clean, typed,
and documented code; typedparse will do all work for you.

```python
import typedparse
from typing import Optional


def main(file: str, number: Optional[int] = 6):
    """Display first lines of a file.

    Args:
        file: file to display
        number: number of lines to display
    """
    with open(file, "r") as f:
        for i in range(0, number):
            print(f.readline(), end="")


if __name__ == "__main__":
    typedparse.parse(main, generate_short_flags=True)
```

Here is a small example that emulates the standard `head` command. Here you need only specify types and default values
for the function's formal parameters and pass them into the `parse` function. You also have to specify the docstring for
the function it will be used to generate help. In this case we also use `generate_short_flags=True` to generate short flags.
That's it.

If we run the program with one argument `-h` or `--help`, it produces the following output:

```
usage: head.py [-h] [--number [NUMBER]] file

positional arguments:
  file                  file to display

optional arguments:
  -h, --help            show this help message and exit
  --number [NUMBER], -n [NUMBER]
                        number of lines to display
```

Typedparse heavily relies on not only type hints but [docstring_parser](https://github.com/rr-/docstring_parser)
package. So it supports all popular documentation styles, but you need to be sure your docstring is well-formed
according to the style you chose. This means you can skip the long description but can't skip the short one and
parameters' description.

## Installation

Typedparse is available as a regular PyPI package. To install it, simply type:

```bash
pip install typedparse
```

## Positional and optional arguments

The separation of positional and optional arguments in the function definition and command-line arguments is slightly
different because it allows for a default value. In typedparse, we use Optional type to distinguish positional and
optional arguments:

```python
from typing import Optional


def main(foo: str, bar: Optional[str] = "bar"):
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
import typedparse
from typing import Optional


@typedparse.options(bar="-b")
def main(foo: str, bar: Optional[str] = "bar"):
    ...
```

Of course, it makes sense only for optional arguments. Now it will work with both
`--bar` and `-b` flags.

To use only the short flag, the simplest way to do it is `@options(bar=["-b"])`. You can also use another name for the
long flag by the same trick: `bar=["--box"]`
or use both `bar=["-b", "--box"]`. It will affect only the command line arguments but not the function's formal
parameters.

There is an option to generate short flags automatically for all optional arguments. To do so
use `generate_short_flags=True` as the second argument in `parse` function.

Of course, you can combine both methods. In this case, the generator will use information about used flags during the
generating process. The general algorithm tries to use the first character of the formal parameter as a short flag. If
the flag is in use, it tries to use the second character and so on.

## Subparsers

Typedparse supports a hierarchy of parsers in a very natural way. You can combine functions in classes, classes in
lists. Consider the following example:

```python
import typedparse
from typing import Optional


class CliExample:

    def add(self, name: str, email: Optional[str] = None):
        ...

    def remove(self, name: str):
        ...


if __name__ == "__main__":
    typedparse.parse(CliExample())
```

There are two commands here:  `add` and `remove` with their own set of arguments. 
*Methods started from underscore will be ignored by the parser*. Typical usage will look like:

```bash
python commands.py add john --email john@mycompany.com
```

So, the `name` parameter will be bound to `john`, and the `email` will be bound to `john@mycompany.com`.
If the class construction doesn't have parameters, you can pass the class itself 
into the `parse` function instead of the object: `typedparse.parse(CliExample)`.

Methods 

Actually, you don't need a class if you want to create sub-commands. You can use 
a list of functions instead:

```python
import typedparse
from typing import Optional

def add(name: str, email: Optional[str] = None):
    ...

def remove(name: str):
    ...

if __name__ == "__main__":
    typedparse.parse([add, remove])
```

## List arguments

List arguments are supported out of the box in typedparse:

```python
from typing import List


def main(numbers: List[int]):
    ...
```

But there are two possible issues here:

- By default, the number of arguments in the list is more than one. This is equivalent to `nargs="+"` in argparse
  package.
- It may be inconvenient to have the displayed name
  (meta variable in terms of argparse) the same as the corresponding formal parameter. It will look
  like `numbers [numbers ...]` if we would try to display help.

How to manage that? For the second case, we can rename the formal parameter or use `@options(flags=["number"])` to make
it singular. If we want to allow an empty list, we can specify it in the following
way `@options(numbers={"nargs": "*"})`. We also can combine these two options if we want:

```python
import typedparse
from typing import List


@typedparse.options(numbers={
    "flags": ["number"],
    "nargs": "*"
})
def main(numbers: List[int]):
    """My brand new CLI

    Args:
        numbers: a list of numbers
    """
    ...
```

## Custom types

If you want to parse arguments to your own types, you can do that in the following manner:

```python
import typedparse
from typing import Optional


def to_int(s: str) -> int:
    if s.startswith("0x"):
        return int(s, 16)
    elif s.startswith("0"):
        return int(s, 8)

    return int(s, 10)


@typedparse.options(test={
    "type": to_int
})
def main(test: Optional[int] = 0):
    ...
```

In this example, we use a custom function to convert string arguments to integers, which supports hexadecimal and octal
representations.

## Kebab case vs. snake case arguments

From the version 0.2 typedparse uses kebab case for long optional flags, so 
`my_long_flag: Optional[bool]` will become `--my-long-flag`. You can use snake case,
if you want by setting `snake_case_flags` to true in the `parse` function.