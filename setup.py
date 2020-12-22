from setuptools import setup

setup(
    name="typedparse",
    version="0.1",
    author="Vitaly Khudobakhshov",
    author_email="vitaly.khudobakhshov@gmail.com",
    packages=["typedparse"],
    scripts=[],
    url="https://github.com/khud/typedparse",
    license="Apache License 2.0",
    description="Parser for command-line options based on type hints",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["docstring_parser"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3"
    ]
)
