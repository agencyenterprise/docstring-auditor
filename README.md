# Docstring Auditor

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docstring-auditor)
[![tests](https://github.com/rob-luke/docstring-auditor/actions/workflows/test.yml/badge.svg)](https://github.com/rob-luke/docstring-auditor/actions/workflows/test.yml)
[![Release](https://github.com/rob-luke/docstring-auditor/actions/workflows/release.yml/badge.svg)](https://github.com/rob-luke/docstring-auditor/actions/workflows/release.yml)

Meet _Docstring Auditor_, your go-to solution for maintaining precise and up-to-date Python code documentation. Tired of misleading or outdated docstrings? Docstring Auditor harnesses the power of large language models to analyze and critique your docstrings, ensuring they align with your code's true purpose. Accessible to both experts and novices, Docstring Auditor is your ultimate companion for clear, concise, and informative docstrings. Say hello to better code documentation!

## Motivation

Recognizing the need for a reliable tool to address the challenge of keeping code documentation in sync with evolving codebases, we developed Docstring Auditor to tackle this issue head-on. Our motivation was to create an accessible, user-friendly solution that empowers developers to maintain clear and up-to-date documentation with ease, enhancing their workflow and reducing misunderstandings.

Docstring Auditor leverages the advanced capabilities of GPT-4, a powerful language model designed to deeply understand both code and natural language. By incorporating GPT-4 into our tool, Docstring Auditor examines the docstrings in your Python code, identifying discrepancies between the documentation and the actual code implementation. The analysis covers errors, warnings, and potential improvements, providing valuable critiques and suggestions to help you keep your documentation accurate and coherent. Docstring Auditor not only ensures that technical details, such as variables and types, are consistent, but it also verifies that the docstrings' meanings are in harmony with the code's functionality.

With Docstring Auditor, you can trust that your documentation stays relevant, informative, and accessible to all members of your team, making collaboration smoother and more efficient than ever before.


## Features
- Analyzes Python functions' docstrings in a given file
- Identifies errors, warnings, and possible improvements
- Provides detailed critiques and suggestions for better docstrings
- Powered by OpenAI's GPT for accurate and insightful analysis
- Easy to use command-line interface


## Installation

The easiest way to use Docstring Auditor is with Docker

1. Install [Docker](https://docs.docker.com/get-docker/)
2. Run the following command:

```bash
docker run -it --rm -e OPENAI_API_KEY=sk-XXXX -v /Path/to/code:/repo docstring-auditor
```


### Local Installation
You can also run Docstring Auditor locally by following these steps:

1. Install [Python 3.6+](https://www.python.org/downloads/)
2. Install [Git](https://git-scm.com/downloads)
3. Clone the repository: `git clone git@github.com:rob-luke/docstring-auditor.git`
4. Setup hatch: `pip install hatch`
5. Run the package `hatch run docstring-auditor /path/to/your/python_file.py`


## Usage
Using Docstring Auditor is as easy as running the following command:

```bash
docstring-auditor path/to/your/python_file.py
```

You can pass in a single file to analyse, or you can pass in a directory and it will analyse every file.

The tool will then analyze the functions' docstrings in the specified file and display the critiques and suggestions for improvement.

## Example
Let's say you have a Python file called example.py with the following content:

```python

def compute(a, b):
    """
    Add two numbers.

    Parameters
    ----------
    a : int or float
        The first number to be added or from which 'b' will be subtracted.
    b : int or float
        The second number to be added or subtracted.

    Returns
    -------
    int or float
        The result of the addition operation.
    """
     if a > 0:
        return a + b
     else:
        return a - b

```

To analyze the docstring of the add function, run:

```bash
docstring-auditor example.py
```
Docstring Auditor will then provide you with a detailed analysis of the docstring, including any errors, warnings, and suggestions for improvement.
The output may look like...

```bash
Processing function 1 of 1...
--------------------------------------------------------------------------------
An error was found in the function: compute

The docstring states that the function adds two numbers, but the code also performs subtraction if 'a' is less than or equal to 0. The docstring should accurately describe both addition and subtraction operations.

A warning was found in the function: compute

The docstring does not follow the numpydoc style completely. The summary line should be a one-line summary, and the extended description should be provided in a separate paragraph.

A proposed solution to these concerns is:

"""
Add or subtract two numbers based on the value of 'a'.

This function performs addition if 'a' is greater than 0, and subtraction if 'a' is less than or equal to 0.

Parameters
----------
a : int or float
    The first number to be added or from which 'b' will be subtracted.
b : int or float
    The second number to be added or subtracted.

Returns
-------
int or float
    The result of the addition or subtraction operation.
"""

```

## Contributing
We welcome contributions to Docstring Auditor! If you'd like to contribute, please fork the repository and submit a pull request with your changes. We also appreciate bug reports and feature requests submitted through the GitHub issues page.

