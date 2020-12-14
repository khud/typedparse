import typing as ty

import typedparse


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
