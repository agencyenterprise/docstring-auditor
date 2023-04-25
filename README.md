# Docstring Auditor

Docstring Auditor is a powerful and user-friendly tool that analyzes Python functions' docstrings and provides insightful critiques and suggestions for improvement. With the help of OpenAI's GPT, this tool ensures that your docstrings are clear, concise, and follow the best practices, making your code more maintainable and easier to understand.

## Features
- Analyzes Python functions' docstrings in a given file
- Identifies errors, warnings, and possible improvements
- Provides detailed critiques and suggestions for better docstrings
- Powered by OpenAI's GPT for accurate and insightful analysis
- Easy to use command-line interface


## Installation
To install Docstring Auditor, simply run:

```bash
pip install docstring-auditor
```

## Usage
Using Docstring Auditor is as easy as running the following command:

```bash
docstring-auditor path/to/your/python_file.py
```

The tool will then analyze the functions' docstrings in the specified file and display the critiques and suggestions for improvement.

Example
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

