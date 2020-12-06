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
