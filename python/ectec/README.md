# ECTEC

This is the core of the chat programm. This python package provides the main functionalities.
GUIs and other programms can use this package to provide the implemented functions
and add own on top.

## Development Install

1. Enter the directory of this file in a terminal.

2. Enter a virtual python environment.

3. Run:

```bash
pip install -e .
```

4. This module will be installed in development mode in the current python environment.
    Changes to the source code will automatically take affect for the package in this
    environment.

## Building

1. Enter the directory of this file in a terminal.

2. Run:

```bash
python -m build -w -s
```

3. You can find a `.tar.gz` file as source code distribution and a `.wheel` file as a build python
    package in `./dist/`.
