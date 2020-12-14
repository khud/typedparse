# Typedparse
What is typedparse? It is a parser for command-line options based on type hints. 
Typedparse uses the argparse package as the backend. So you don't need to define 
parsers and subparsers by yourself anymore. Just write clean, typed, and documented 
code; typedparse will do all work for you. 

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
Here is a small example that emulates the standard `head` command. 
Here you need only specify types and default values for the function's 
formal parameters and pass them into the `parse` function. 
You also have to specify the docstring for the function 
it will be used to generate help. That's it. 

If we run the program with one argument `-h` or `--help`, 
it produces the following output:

```
usage: head.py [-h] [--number [NUMBER]] file

positional arguments:
  file               file to display

optional arguments:
  -h, --help         show this help message and exit
  --number [NUMBER]  number of lines to display
```

Typedparse heavily relies on not only type hints but [docstring_parser](https://github.com/rr-/docstring_parser)
package. So it supports all popular documentation styles, but you need 
to be sure your docstring is well-formed according to the style 
you chose. This means you can skip the long description but can't skip 
the short one and parameters' description.

## Positional and optional arguments

The separation of positional and optional arguments in the function definition 
and command-line arguments is slightly different because it allows 
for a default value.  In typedparse, we use Optional type to distinguish 
positional and optional arguments:

```python
import typing as ty

def main(foo: str, bar: ty.Optional[str] = "bar"):
    ...
```
In this example, `foo` is a positional argument, and `bar` is optional with 
the default value "bar". You can add default value for positional arguments too, 
e.g. `def main(foo: str = "foo", ...)`.

## Types of arguments
For any argument, we must specify the type using a type hint for a certain 
formal parameter. It can be the built-in Python type like `int`, `float` or `str`. 
Or any user-defined class with a constructor that accepts a string argument. 
For example, we can use `Path` instead of `str` type for filenames and paths.

## Short flags
To introduce a short flag, one can use a decorator `options` for the functions:

```python
import typing as ty
import typedparse


@typedparse.options(bar="b")
def main(foo: str, bar: ty.Optional[str] = "bar"):
    ...
```
Of course, it makes sense only for optional arguments. Now it will work with both 
`--bar` and `-b` flags.

## Subparsers
Typedparse supports a hierarchy of parsers in a very natural way. 
You can combine functions in classes, classes in lists, and dictionaries. 
Consider the following example:

```python
import typedparse
import typing as ty


class CliExample:
    
    @typedparse.options(email="e")
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
There are two commands here:  `add` and `remove` with their own set 
of arguments. Typical usage will look like:

```bash
python commands.py add john -e john@mycompany.com
```
 
So, the `name` parameter will be bound to `john`, and the `email` will 
be bound to `john@mycompany.com`. 