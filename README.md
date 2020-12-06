# Typedparse
What is typedparse? It is a parser for command-line options based on type hints. 
Typedparse uses the argparse library as the backend. So you don't need to define 
parsers and subparsers by yourself anymore. Just write clean, typed, and documented 
code; the library will do all work for you. 

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
formal parameters and pass it into the `parse` function. 
You also have to specify the docstring for the function 
it will be used to generate help. That's it.

Typedparse heavily relies on not only type hints but [docstring_parser](https://github.com/rr-/docstring_parser)
package. So it supports all popular documentation styles, but you need 
to be sure your docstring is well-formed according to the style 
you chose. This means you can skip the long description but can't skip 
the short one and parameters' description.


